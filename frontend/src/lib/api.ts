/**
 * lib/api.ts — Backend API Client
 * ================================
 * Typed fetch wrappers for all FastAPI endpoints.
 * Uses Next.js rewrites so requests go to /api/* (proxied to localhost:8000).
 */

// ── Chat API ─────────────────────────────────────────────────────────────────

export interface ChatRequest {
  message: string;
  ticker: string;
  ui_context: {
    view_mode: string;
    portfolio_state: Record<string, unknown>;
  };
  use_mock_llm?: boolean;
}

export interface UIAction {
  action: string;
  payload: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  confidence: number | null;
  signal: string | null;
  reasoning: string[];
  ui_action: UIAction | null;
  agent_source: string;
}

export async function sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch("/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
  return res.json();
}

// ── Market API ───────────────────────────────────────────────────────────────

export async function fetchHistory(
  ticker: string,
  period = "6mo",
  interval = "1d"
) {
  const params = new URLSearchParams({ ticker, period, interval });
  const res = await fetch(`/api/market/history?${params}`);
  if (!res.ok) throw new Error(`Market history error: ${res.status}`);
  return res.json();
}

export async function fetchQuote(ticker: string) {
  const res = await fetch(`/api/market/quote?ticker=${ticker}`);
  if (!res.ok) throw new Error(`Quote error: ${res.status}`);
  return res.json();
}

// ── Portfolio API ────────────────────────────────────────────────────────────

export async function fetchPortfolio() {
  const res = await fetch("/api/portfolio/");
  if (!res.ok) throw new Error(`Portfolio error: ${res.status}`);
  return res.json();
}

export async function fetchRiskMetrics() {
  const res = await fetch("/api/portfolio/risk");
  if (!res.ok) throw new Error(`Risk metrics error: ${res.status}`);
  return res.json();
}

// ── Health Check ─────────────────────────────────────────────────────────────

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/health");
    return res.ok;
  } catch {
    return false;
  }
}
