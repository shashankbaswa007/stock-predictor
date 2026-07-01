/**
 * DashboardPanel.tsx — Main Dashboard Container
 * ===============================================
 * Left side (65%) of the split-screen layout.
 * Renders the header bar with ticker/view controls and the main content area.
 * Switches between Short-Term, Long-Term, and Portfolio views based on Zustand state.
 */

"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAppStore, ViewMode } from "@/store/useAppStore";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { InfoTooltip } from "@/components/ui/InfoTooltip";
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

// ── Custom Hook for Flash Effect ─────────────────────────────────────────────
function usePrevious<T>(value: T): T | undefined {
  const ref = React.useRef<T>();
  React.useEffect(() => {
    ref.current = value;
  }, [value]);
  return ref.current;
}

export function DashboardPanel() {
  const viewMode = useAppStore((s) => s.viewMode);
  const setViewMode = useAppStore((s) => s.setViewMode);
  const currentTicker = useAppStore((s) => s.currentTicker);
  const portfolio = useAppStore((s) => s.portfolio);
  const livePrice = useAppStore((s) => s.livePrice);

  const prevPrice = usePrevious(livePrice);
  const [flashClass, setFlashClass] = React.useState("");

  React.useEffect(() => {
    if (livePrice && prevPrice && livePrice !== prevPrice) {
      setFlashClass(livePrice > prevPrice ? "bg-bull/20 text-bull" : "bg-bear/20 text-bear");
      const timer = setTimeout(() => setFlashClass("text-accent"), 500);
      return () => clearTimeout(timer);
    }
  }, [livePrice, prevPrice]);

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
            <span className={cn("ml-1 font-mono transition-colors duration-300 px-1.5 rounded", flashClass || "text-accent")}>
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
          <InfoTooltip content="Value at Risk (VaR): A statistical measure of the risk of loss for an investment. It estimates how much a set of investments might lose given normal market conditions.">
            <span className="cursor-help border-b border-dashed border-text-muted/50">VaR(95%)</span>
          </InfoTooltip>
          <span className="text-bear font-mono">{formatCurrency(portfolio.var95 ?? 0)}</span>
        </div>
        {livePrice !== null && (
          <div className="flex items-center gap-1 text-[10px] ml-auto">
            <span className="text-text-muted/70">Data Source:</span>
            <span className="text-text-secondary font-medium">Finnhub Real-Time</span>
            <span className="mx-1 text-border">•</span>
            <span className="text-text-muted/70">Last updated:</span>
            <span className="text-text-secondary font-mono">
              {new Date().toLocaleTimeString([], { hour12: false })}
            </span>
          </div>
        )}
      </div>

      {/* ── Main Content Area ───────────────────────────────────────────── */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-hide space-y-3 relative overflow-hidden">
        <AnimatePresence mode="wait">
          {viewMode === "short_term" && (
            <motion.div key="short_term" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }} className="h-full">
              <ShortTermView ticker={currentTicker} />
            </motion.div>
          )}
          {viewMode === "long_term" && (
            <motion.div key="long_term" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }} className="h-full">
              <LongTermView ticker={currentTicker} />
            </motion.div>
          )}
          {viewMode === "portfolio" && (
            <motion.div key="portfolio" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }} className="h-full">
              <PortfolioView />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ── Short-Term View (Phase 4 Active) ─────────────────────────────────────────

import { useState, useEffect } from "react";
import { fetchHistory, fetchNews, fetchQuote } from "@/lib/api";
import { CandlestickChart } from "./CandlestickChart";
import { TechnicalChart } from "./TechnicalChart";
import { Spinner } from "@/components/ui/Spinner";

function ShortTermView({ ticker }: { ticker: string }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showIndicators, setShowIndicators] = useState(true);

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
          <div 
            className="flex items-center gap-2 cursor-pointer select-none group w-full"
            onClick={() => setShowIndicators(!showIndicators)}
          >
            <LineChart className="w-4 h-4 text-bull" />
            <span className="text-sm font-medium text-text-primary group-hover:text-accent-light transition-colors">
              Technical Indicators
            </span>
            <Badge label="RSI" />
            <Badge label="MACD" />
            <div className="ml-auto text-text-muted transition-transform duration-200" style={{ transform: showIndicators ? "rotate(0deg)" : "rotate(180deg)" }}>
              ▼
            </div>
          </div>
        }
      >
        <AnimatePresence>
          {showIndicators && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="h-[220px] flex p-2 gap-4">
                {loading ? (
                  <div className="w-full h-full flex flex-col items-center justify-center gap-2">
                    <Spinner />
                  </div>
                ) : (
                  <>
                    {/* Left Side: Indicator Values */}
                    <div className="w-32 flex flex-col justify-around py-4 border-r border-border/50 shrink-0">
                      <div className="text-center flex flex-col items-center">
                        <p className="text-3xl font-mono font-bold text-bull tracking-tighter">
                          {latest?.rsi ? latest.rsi.toFixed(1) : "--"}
                        </p>
                        <InfoTooltip content="Relative Strength Index (RSI): Measures the speed and magnitude of recent price changes to evaluate overvalued or undervalued conditions. >70 is typically overbought, <30 is oversold.">
                          <p className="text-xs text-text-muted mt-1 uppercase tracking-widest font-semibold">RSI (14)</p>
                        </InfoTooltip>
                      </div>
                      <div className="text-center flex flex-col items-center">
                        <p className="text-3xl font-mono font-bold text-accent tracking-tighter">
                          {latest?.macd ? latest.macd.toFixed(2) : "--"}
                        </p>
                        <InfoTooltip content="Moving Average Convergence Divergence (MACD): A trend-following momentum indicator that shows the relationship between two moving averages of a security's price.">
                          <p className="text-xs text-text-muted mt-1 uppercase tracking-widest font-semibold">MACD</p>
                        </InfoTooltip>
                      </div>
                    </div>
                    {/* Right Side: Charts */}
                    <div className="flex-1 flex flex-col gap-3 min-w-0">
                      <div className="flex-1 min-h-0 border border-border/30 rounded-lg bg-surface-900/30 p-1">
                        <TechnicalChart data={data} type="RSI" />
                      </div>
                      <div className="flex-1 min-h-0 border border-border/30 rounded-lg bg-surface-900/30 p-1">
                        <TechnicalChart data={data} type="MACD" />
                      </div>
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Metrics Grid */}
      <MetricsGrid ticker={ticker} />
    </div>
  );
}

// ── Long-Term View (Phase 7: Live Data) ──────────────────────────────────────



function LongTermView({ ticker }: { ticker: string }) {
  const [news, setNews] = useState<any[]>([]);
  const [quote, setQuote] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([fetchNews(ticker), fetchQuote(ticker)])
      .then(([newsRes, quoteRes]) => {
        if (mounted) {
          setNews(newsRes.articles || []);
          setQuote(quoteRes);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [ticker]);

  return (
    <div className="space-y-3 animate-fade-in">
      {/* News Feed */}
      <GlassCard
        header={
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-text-primary">
              {ticker} — Latest News & Analysis
            </span>
            <Badge label="Finnhub" />
          </div>
        }
      >
        <div className="max-h-[320px] overflow-y-auto scrollbar-hide p-2 space-y-2">
          {loading ? (
            <div className="w-full h-[200px] flex flex-col items-center justify-center gap-2">
              <Spinner />
              <span className="text-xs text-text-muted">Loading news...</span>
            </div>
          ) : news.length === 0 ? (
            <div className="text-center py-8 text-text-muted text-sm">
              No recent news found for {ticker}.
            </div>
          ) : (
            news.map((article, i) => (
              <a
                key={i}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 rounded-lg bg-surface-800/50 border border-border/50 hover:border-accent/30 hover:bg-surface-700/50 transition-all duration-200 group"
              >
                <p className="text-sm font-medium text-text-primary group-hover:text-accent-light line-clamp-2">
                  {article.headline}
                </p>
                <div className="flex items-center gap-2 mt-1.5 text-[11px] text-text-muted">
                  <span className="font-medium text-accent/80">{article.source}</span>
                  <span>·</span>
                  <span>{new Date(article.published_at).toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                </div>
                {article.summary && (
                  <p className="text-xs text-text-muted mt-1.5 line-clamp-2">{article.summary}</p>
                )}
              </a>
            ))
          )}
        </div>
      </GlassCard>

      {/* Key Metrics from live quote */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "P/E Ratio", value: quote ? `${quote.pe_ratio}x` : "--", trend: null, tooltip: "Price-to-Earnings Ratio: Measures the company's current share price relative to its per-share earnings." },
          { label: "EPS", value: quote ? `$${quote.eps}` : "--", trend: quote?.eps > 0 ? "up" : null, tooltip: "Earnings Per Share: A company's profit divided by the outstanding shares of its common stock." },
          { label: "Div Yield", value: quote ? `${quote.dividend_yield}%` : "--", trend: null, tooltip: "Dividend Yield: A financial ratio that shows how much a company pays out in dividends each year relative to its stock price." },
          { label: "Beta", value: quote ? quote.beta.toFixed(2) : "--", trend: null, tooltip: "Beta: A measure of the volatility, or systematic risk, of a security compared to the market as a whole (Beta > 1 means more volatile)." },
        ].map((m) => (
          <div key={m.label} className="metric-card">
            <InfoTooltip content={m.tooltip}>
              <p className="text-text-muted text-xs cursor-help">{m.label}</p>
            </InfoTooltip>
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
