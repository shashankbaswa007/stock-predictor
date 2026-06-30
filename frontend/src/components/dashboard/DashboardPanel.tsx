/**
 * DashboardPanel.tsx — Main Dashboard Container
 * ===============================================
 * Left side (65%) of the split-screen layout.
 * Renders the header bar with ticker/view controls and the main content area.
 * Switches between Short-Term, Long-Term, and Portfolio views based on Zustand state.
 */

"use client";

import React from "react";
import { useAppStore, ViewMode } from "@/store/useAppStore";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { MetricsGrid } from "./MetricsGrid";
import { TickerSearch } from "./TickerSearch";
import { cn, formatCurrency, formatPercent, trendColor } from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  LineChart,
  Briefcase,
  Activity,
  Zap,
  BookOpen,
} from "lucide-react";

// ── View Mode Tabs ───────────────────────────────────────────────────────────

const VIEW_TABS: { mode: ViewMode; label: string; icon: React.ReactNode; description: string }[] = [
  {
    mode: "short_term",
    label: "Short-Term",
    icon: <Zap className="w-3.5 h-3.5" />,
    description: "Technical & ML Analysis",
  },
  {
    mode: "long_term",
    label: "Long-Term",
    icon: <BookOpen className="w-3.5 h-3.5" />,
    description: "Fundamental & RAG Analysis",
  },
  {
    mode: "portfolio",
    label: "Portfolio",
    icon: <Briefcase className="w-3.5 h-3.5" />,
    description: "Holdings & Risk",
  },
];

import { wsService } from "@/lib/ws";

// ── Component ────────────────────────────────────────────────────────────────

export function DashboardPanel() {
  const viewMode = useAppStore((s) => s.viewMode);
  const setViewMode = useAppStore((s) => s.setViewMode);
  const currentTicker = useAppStore((s) => s.currentTicker);
  const portfolio = useAppStore((s) => s.portfolio);
  const livePrice = useAppStore((s) => s.livePrice);

  React.useEffect(() => {
    wsService.subscribe(currentTicker);
  }, [currentTicker]);

  return (
    <div className="flex flex-col h-full gap-3" id="dashboard-panel">
      {/* ── Top Bar: Ticker + View Tabs ─────────────────────────────────── */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Ticker Selector */}
        <TickerSearch />

        {/* View Mode Tabs */}
        <div className="flex items-center bg-surface-800/80 rounded-lg border border-border p-0.5 ml-auto">
          {VIEW_TABS.map((tab) => (
            <button
              key={tab.mode}
              onClick={() => setViewMode(tab.mode)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200",
                viewMode === tab.mode
                  ? "bg-accent/20 text-accent-light border border-accent/30 shadow-sm"
                  : "text-text-muted hover:text-text-secondary hover:bg-surface-700/50"
              )}
              title={tab.description}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── Quick Stats Bar ─────────────────────────────────────────────── */}
      <div className="flex items-center gap-2 text-xs text-text-muted overflow-x-auto scrollbar-hide">
        <div className="flex items-center gap-1.5 ticker-pill">
          <Activity className="w-3 h-3 text-accent" />
          <span className="text-text-primary font-semibold">{currentTicker}</span>
          {livePrice !== null && (
            <span className="ml-1 text-accent font-mono animate-pulse">
              ${livePrice.toFixed(2)}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 ticker-pill">
          <span>Portfolio</span>
          <span className="text-text-primary font-mono">{formatCurrency(portfolio.totalValue, true)}</span>
          <span className={trendColor(portfolio.totalPnlPercent)}>
            {formatPercent(portfolio.totalPnlPercent)}
          </span>
        </div>
        <div className="flex items-center gap-1 ticker-pill">
          <span>VaR(95%)</span>
          <span className="text-bear font-mono">{formatCurrency(portfolio.var95 ?? 0)}</span>
        </div>
      </div>

      {/* ── Main Content Area ───────────────────────────────────────────── */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-hide space-y-3">
        {viewMode === "short_term" && <ShortTermView ticker={currentTicker} />}
        {viewMode === "long_term" && <LongTermView ticker={currentTicker} />}
        {viewMode === "portfolio" && <PortfolioView />}
      </div>
    </div>
  );
}

// ── Short-Term View (Phase 4 Active) ─────────────────────────────────────────

import { useState, useEffect } from "react";
import { fetchHistory } from "@/lib/api";
import { CandlestickChart } from "./CandlestickChart";
import { TechnicalChart } from "./TechnicalChart";
import { Spinner } from "@/components/ui/Spinner";

function ShortTermView({ ticker }: { ticker: string }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchHistory(ticker, "6mo", "1d")
      .then((res) => {
        if (mounted) {
          setData(res.data || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [ticker]);

  const latest = data.length > 0 ? data[data.length - 1] : null;

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Candlestick Chart */}
      <GlassCard
        header={
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-text-primary">
              {ticker} — Candlestick Chart
            </span>
            <Badge label="1D" />
          </div>
        }
      >
        <div className="h-[320px] p-2">
          {loading ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2">
              <Spinner />
              <span className="text-xs text-text-muted">Loading chart data...</span>
            </div>
          ) : (
            <CandlestickChart data={data} />
          )}
        </div>
      </GlassCard>

      {/* Technical Indicators */}
      <GlassCard
        header={
          <div className="flex items-center gap-2">
            <LineChart className="w-4 h-4 text-bull" />
            <span className="text-sm font-medium text-text-primary">
              Technical Indicators
            </span>
            <Badge label="RSI" />
            <Badge label="MACD" />
          </div>
        }
      >
        <div className="h-[180px] flex p-2 gap-2">
          {loading ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2">
              <Spinner />
            </div>
          ) : (
            <>
              {/* Left Side: Indicator Values */}
              <div className="w-32 flex flex-col items-center justify-center gap-4 border-r border-border/50 shrink-0">
                <div className="text-center">
                  <p className="text-2xl font-mono font-bold text-bull">
                    {latest?.rsi ? latest.rsi.toFixed(1) : "--"}
                  </p>
                  <p className="text-xs text-text-muted mt-0.5">RSI (14)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-mono font-bold text-accent">
                    {latest?.macd ? latest.macd.toFixed(2) : "--"}
                  </p>
                  <p className="text-xs text-text-muted mt-0.5">MACD</p>
                </div>
              </div>
              {/* Right Side: Charts */}
              <div className="flex-1 flex flex-col gap-2 min-w-0">
                <div className="flex-1 min-h-0">
                  <TechnicalChart data={data} type="RSI" />
                </div>
                <div className="flex-1 min-h-0">
                  <TechnicalChart data={data} type="MACD" />
                </div>
              </div>
            </>
          )}
        </div>
      </GlassCard>

      {/* Metrics Grid */}
      <MetricsGrid ticker={ticker} />
    </div>
  );
}

// ── Long-Term View (Phase 1 Placeholder) ─────────────────────────────────────

function LongTermView({ ticker }: { ticker: string }) {
  return (
    <div className="space-y-3 animate-fade-in">
      <GlassCard
        header={
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-text-primary">
              {ticker} — Fundamental Analysis
            </span>
            <Badge label="RAG Pipeline" />
          </div>
        }
      >
        <div className="h-[320px] flex items-center justify-center p-6">
          <div className="text-center space-y-3">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-bull/10 border border-bull/20 flex items-center justify-center">
              <BookOpen className="w-8 h-8 text-bull/60" />
            </div>
            <div>
              <p className="text-text-secondary text-sm font-medium">
                RAG-Powered Fundamental Analysis
              </p>
              <p className="text-text-muted text-xs mt-1">
                SEC filings, earnings calls & macro analysis — loading in Phase 3
              </p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "P/E Ratio", value: "28.5x", trend: null },
          { label: "Revenue Growth", value: "+12.3%", trend: "up" },
          { label: "Debt/Equity", value: "1.45", trend: null },
          { label: "Free Cash Flow", value: "$4.2B", trend: "up" },
        ].map((m) => (
          <div key={m.label} className="metric-card">
            <p className="text-text-muted text-xs">{m.label}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <p className="text-lg font-mono font-semibold text-text-primary">
                {m.value}
              </p>
              {m.trend === "up" && <TrendingUp className="w-3.5 h-3.5 text-bull" />}
              {m.trend === "down" && <TrendingDown className="w-3.5 h-3.5 text-bear" />}
            </div>
          </div>
        ))}
      </div>

      <MetricsGrid ticker={ticker} />
    </div>
  );
}

// ── Portfolio View (Phase 1 Placeholder) ─────────────────────────────────────

function PortfolioView() {
  const portfolio = useAppStore((s) => s.portfolio);
  const setTicker = useAppStore((s) => s.setTicker);

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="metric-card positive">
          <p className="text-text-muted text-xs">Total Value</p>
          <p className="text-xl font-mono font-bold text-text-primary mt-1">
            {formatCurrency(portfolio.totalValue, true)}
          </p>
        </div>
        <div className={cn("metric-card", portfolio.totalPnl >= 0 ? "positive" : "negative")}>
          <p className="text-text-muted text-xs">Total P&L</p>
          <div className="flex items-center gap-1.5 mt-1">
            <p className={cn("text-xl font-mono font-bold", trendColor(portfolio.totalPnl))}>
              {formatCurrency(portfolio.totalPnl, true)}
            </p>
          </div>
          <p className={cn("text-xs font-mono mt-0.5", trendColor(portfolio.totalPnlPercent))}>
            {formatPercent(portfolio.totalPnlPercent)}
          </p>
        </div>
        <div className="metric-card">
          <p className="text-text-muted text-xs">Cash Balance</p>
          <p className="text-xl font-mono font-bold text-text-primary mt-1">
            {formatCurrency(portfolio.cash, true)}
          </p>
        </div>
        <div className="metric-card negative">
          <p className="text-text-muted text-xs">VaR (95%)</p>
          <p className="text-xl font-mono font-bold text-bear mt-1">
            {formatCurrency(portfolio.var95 ?? 0)}
          </p>
        </div>
      </div>

      {/* Holdings Table */}
      <GlassCard
        header={
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-text-primary">Holdings</span>
            <Badge label={`${portfolio.holdings.length} positions`} />
          </div>
        }
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs">
                <th className="text-left py-2.5 px-4 font-medium">Ticker</th>
                <th className="text-right py-2.5 px-4 font-medium">Shares</th>
                <th className="text-right py-2.5 px-4 font-medium">Avg Cost</th>
                <th className="text-right py-2.5 px-4 font-medium">Price</th>
                <th className="text-right py-2.5 px-4 font-medium">P&L</th>
                <th className="text-right py-2.5 px-4 font-medium">Weight</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map((h) => (
                <tr
                  key={h.ticker}
                  className="border-b border-border/50 hover:bg-surface-700/30 transition-colors cursor-pointer"
                  onClick={() => setTicker(h.ticker)}
                >
                  <td className="py-2.5 px-4">
                    <span className="font-mono font-semibold text-text-primary">
                      {h.ticker}
                    </span>
                  </td>
                  <td className="text-right py-2.5 px-4 font-mono text-text-secondary">
                    {h.shares}
                  </td>
                  <td className="text-right py-2.5 px-4 font-mono text-text-secondary">
                    {formatCurrency(h.avgCost)}
                  </td>
                  <td className="text-right py-2.5 px-4 font-mono text-text-primary">
                    {formatCurrency(h.currentPrice)}
                  </td>
                  <td className="text-right py-2.5 px-4">
                    <span className={cn("font-mono font-medium", trendColor(h.pnl))}>
                      {formatCurrency(h.pnl)}
                    </span>
                    <span className={cn("text-xs ml-1", trendColor(h.pnlPercent))}>
                      ({formatPercent(h.pnlPercent)})
                    </span>
                  </td>
                  <td className="text-right py-2.5 px-4 font-mono text-text-secondary">
                    {(h.weight * 100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
