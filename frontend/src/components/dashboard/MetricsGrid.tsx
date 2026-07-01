/**
 * MetricsGrid.tsx — Key Financial Metrics Grid
 * ==============================================
 * Displays key market stats for the currently selected ticker.
 */

"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, DollarSign, BarChart2, Clock, Hash } from "lucide-react";
import { cn, formatCurrency, trendColor } from "@/lib/utils";
import { fetchQuote } from "@/lib/api";
import { Spinner } from "@/components/ui/Spinner";

interface MetricsGridProps {
  ticker: string;
}

function formatNumberShort(num: number) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + "T";
  if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
  if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
  return num.toLocaleString();
}

export function MetricsGrid({ ticker }: MetricsGridProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchQuote(ticker)
      .then((res) => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Quote fetch error", err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [ticker]);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center p-6 h-[80px] bg-surface-800/50 rounded-xl border border-border">
        <Spinner size="sm" />
      </div>
    );
  }

  const metrics = [
    { label: "Market Cap", value: `$${formatNumberShort(data.market_cap)}`, icon: <DollarSign className="w-3.5 h-3.5" /> },
    { label: "Volume", value: formatNumberShort(data.volume), icon: <BarChart2 className="w-3.5 h-3.5" /> },
    { label: "52W High", value: formatCurrency(data.week_52_high), icon: <TrendingUp className="w-3.5 h-3.5" /> },
    { label: "52W Low", value: formatCurrency(data.week_52_low), icon: <TrendingDown className="w-3.5 h-3.5" /> },
    { label: "Avg Volume", value: formatNumberShort(data.avg_volume), icon: <Hash className="w-3.5 h-3.5" /> },
    { label: "Beta", value: data.beta.toFixed(2), icon: <Clock className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" id="metrics-grid">
      {metrics.map((m) => (
        <div key={m.label} className="metric-card group bg-surface-800/80 hover:bg-surface-800 transition-colors border border-border/50 hover:border-border p-4 rounded-xl">
          <div className="flex items-center gap-1.5 text-text-muted mb-2">
            <span className="opacity-70 group-hover:opacity-100 transition-opacity text-accent">
              {m.icon}
            </span>
            <span className="text-xs font-semibold tracking-wide uppercase">{m.label}</span>
          </div>
          <p className="text-lg font-mono font-bold text-text-primary tracking-tight">
            {m.value}
          </p>
        </div>
      ))}
    </div>
  );
}
