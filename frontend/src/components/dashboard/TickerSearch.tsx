/**
 * TickerSearch.tsx — Stock Ticker Autocomplete Selector
 * =====================================================
 * Quick-select from popular tickers or type a custom symbol.
 * Updates the Zustand store on selection.
 */

"use client";

import React, { useState, useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";
import { Search, ChevronDown } from "lucide-react";

const POPULAR_TICKERS = [
  { symbol: "AAPL", name: "Apple Inc." },
  { symbol: "MSFT", name: "Microsoft Corp." },
  { symbol: "NVDA", name: "NVIDIA Corp." },
  { symbol: "GOOGL", name: "Alphabet Inc." },
  { symbol: "AMZN", name: "Amazon.com Inc." },
  { symbol: "META", name: "Meta Platforms" },
  { symbol: "TSLA", name: "Tesla Inc." },
  { symbol: "JPM", name: "JPMorgan Chase" },
];

export function TickerSearch() {
  const currentTicker = useAppStore((s) => s.currentTicker);
  const setTicker = useAppStore((s) => s.setTicker);
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filtered = POPULAR_TICKERS.filter(
    (t) =>
      t.symbol.toLowerCase().includes(search.toLowerCase()) ||
      t.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (symbol: string) => {
    setTicker(symbol);
    setIsOpen(false);
    setSearch("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && search.trim()) {
      handleSelect(search.trim().toUpperCase());
    }
  };

  return (
    <div className="relative" ref={dropdownRef} id="ticker-search">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium",
          "bg-surface-800/80 border border-border hover:border-border-hover",
          "transition-all duration-200",
          isOpen && "border-accent/50 shadow-glow"
        )}
      >
        <Search className="w-3.5 h-3.5 text-text-muted" />
        <span className="font-mono font-bold text-text-primary">{currentTicker}</span>
        <ChevronDown
          className={cn(
            "w-3.5 h-3.5 text-text-muted transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className={cn(
            "absolute top-full left-0 mt-1.5 w-64 z-50",
            "glass-panel shadow-glass animate-fade-in overflow-hidden"
          )}
        >
          {/* Search Input */}
          <div className="p-2 border-b border-border">
            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-surface-900/80">
              <Search className="w-3.5 h-3.5 text-text-muted" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search ticker..."
                className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
                autoFocus
              />
            </div>
          </div>

          {/* Options */}
          <div className="max-h-[240px] overflow-y-auto scrollbar-hide py-1">
            {filtered.map((t) => (
              <button
                key={t.symbol}
                onClick={() => handleSelect(t.symbol)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 text-left",
                  "hover:bg-surface-700/50 transition-colors",
                  t.symbol === currentTicker && "bg-accent/10"
                )}
              >
                <span
                  className={cn(
                    "font-mono text-sm font-semibold",
                    t.symbol === currentTicker ? "text-accent" : "text-text-primary"
                  )}
                >
                  {t.symbol}
                </span>
                <span className="text-xs text-text-muted truncate">{t.name}</span>
              </button>
            ))}
            {filtered.length === 0 && search && (
              <div className="px-3 py-4 text-center">
                <p className="text-xs text-text-muted">Press Enter to search</p>
                <p className="text-xs text-accent mt-0.5 font-mono">{search.toUpperCase()}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
