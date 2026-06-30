/**
 * useAppStore.ts — Zustand Global State Store
 * ============================================
 * Central state management for the AI Trading Co-Pilot.
 *
 * State slices:
 *   • viewMode      — 'short_term' | 'long_term' | 'portfolio'
 *   • currentTicker — currently selected stock ticker
 *   • portfolio     — holdings and summary data
 *   • chat          — message history and loading state
 *   • uiContext     — dynamic context sent to the backend with each chat request
 */

import { create } from "zustand";

// ── Type Definitions ─────────────────────────────────────────────────────────

export type ViewMode = "short_term" | "long_term" | "portfolio";

export type Signal = "BUY" | "SELL" | "HOLD" | null;

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  timestamp: number;
  signal?: Signal;
  confidence?: number;
  reasoning?: string[];
}

export interface Holding {
  ticker: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  weight: number;
}

export interface PortfolioState {
  totalValue: number;
  totalPnl: number;
  totalPnlPercent: number;
  holdings: Holding[];
  cash: number;
  var95: number | null;
}

export interface UIContext {
  viewMode: ViewMode;
  currentTicker: string;
  chartTimeframe: string;
  activeIndicators: string[];
}

// ── Store Interface ──────────────────────────────────────────────────────────

interface AppState {
  // View state
  viewMode: ViewMode;
  currentTicker: string;
  chartTimeframe: string;
  activeIndicators: string[];

  // Portfolio
  portfolio: PortfolioState;

  // Chat
  chatMessages: ChatMessage[];
  isChatLoading: boolean;

  // Connection status
  isBackendConnected: boolean;
  isWsConnected: boolean;
  livePrice: number | null;

  // Actions — View
  setViewMode: (mode: ViewMode) => void;
  setTicker: (ticker: string) => void;
  setChartTimeframe: (tf: string) => void;
  toggleIndicator: (indicator: string) => void;

  // Actions — Portfolio
  setPortfolio: (portfolio: PortfolioState) => void;

  // Actions — Chat
  addMessage: (msg: ChatMessage) => void;
  setChatLoading: (loading: boolean) => void;
  clearChat: () => void;

  // Actions — Connection
  setBackendConnected: (connected: boolean) => void;
  setWsConnected: (connected: boolean) => void;

  // Derived — UI Context for backend
  getUIContext: () => UIContext;
}

// ── Default Portfolio (populated from backend in Phase 2+) ───────────────────

const DEFAULT_PORTFOLIO: PortfolioState = {
  totalValue: 125_430.50,
  totalPnl: 8_320.75,
  totalPnlPercent: 7.1,
  cash: 15_000.00,
  var95: -3_250.00,
  holdings: [
    { ticker: "AAPL", shares: 50, avgCost: 178.50, currentPrice: 195.20, pnl: 835.00, pnlPercent: 9.36, weight: 0.35 },
    { ticker: "MSFT", shares: 30, avgCost: 380.00, currentPrice: 415.60, pnl: 1068.00, pnlPercent: 9.37, weight: 0.28 },
    { ticker: "NVDA", shares: 20, avgCost: 850.00, currentPrice: 920.30, pnl: 1406.00, pnlPercent: 8.27, weight: 0.22 },
    { ticker: "GOOGL", shares: 25, avgCost: 165.00, currentPrice: 172.80, pnl: 195.00, pnlPercent: 4.73, weight: 0.10 },
    { ticker: "AMZN", shares: 10, avgCost: 185.00, currentPrice: 193.50, pnl: 85.00, pnlPercent: 4.59, weight: 0.05 },
  ],
};

// ── Store Creation ───────────────────────────────────────────────────────────

export const useAppStore = create<AppState>((set, get) => ({
  // ── Initial State ────────────────────────────────────────────────────────
  viewMode: "short_term",
  currentTicker: "AAPL",
  chartTimeframe: "1D",
  activeIndicators: ["RSI", "MACD"],

  portfolio: DEFAULT_PORTFOLIO,

  chatMessages: [
    {
      id: "welcome",
      role: "ai",
      content:
        "👋 Welcome to **AI Trading Co-Pilot**. I can analyze stocks using technical indicators, " +
        "ML predictions, and fundamental analysis from SEC filings. Try asking me:\n\n" +
        '• *"Analyze AAPL for a short-term trade"*\n' +
        '• *"What\'s the long-term outlook for NVDA?"*\n' +
        '• *"Show my portfolio risk"*',
      timestamp: Date.now(),
    },
  ],
  isChatLoading: false,

  isBackendConnected: false,
  isWsConnected: false,
  livePrice: null,

  // ── Actions ──────────────────────────────────────────────────────────────

  setViewMode: (mode) => set({ viewMode: mode }),

  setTicker: (ticker) => set({ currentTicker: ticker.toUpperCase() }),

  setChartTimeframe: (tf) => set({ chartTimeframe: tf }),

  toggleIndicator: (indicator) =>
    set((state) => ({
      activeIndicators: state.activeIndicators.includes(indicator)
        ? state.activeIndicators.filter((i) => i !== indicator)
        : [...state.activeIndicators, indicator],
    })),

  setPortfolio: (portfolio) => set({ portfolio }),

  addMessage: (msg) =>
    set((state) => ({
      chatMessages: [...state.chatMessages, msg],
    })),

  setChatLoading: (loading) => set({ isChatLoading: loading }),

  clearChat: () =>
    set({
      chatMessages: [
        {
          id: "welcome",
          role: "ai",
          content: "💬 Chat cleared. How can I help you?",
          timestamp: Date.now(),
        },
      ],
    }),

  setBackendConnected: (connected) => set({ isBackendConnected: connected }),

  setWsConnected: (connected) => set({ isWsConnected: connected }),

  getUIContext: () => {
    const state = get();
    return {
      viewMode: state.viewMode,
      currentTicker: state.currentTicker,
      chartTimeframe: state.chartTimeframe,
      activeIndicators: state.activeIndicators,
    };
  },
}));
