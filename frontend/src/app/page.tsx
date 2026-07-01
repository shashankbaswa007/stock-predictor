/**
 * page.tsx — Main Application Page
 * ==================================
 * The split-screen layout: 65% Dashboard (left) + 35% Chat Co-Pilot (right).
 * Includes:
 *  • Top navigation bar with branding and status indicators
 *  • Responsive split pane
 *  • Backend health check on mount
 */

"use client";

import React, { useEffect } from "react";
import { Group, Panel, Separator } from "react-resizable-panels";
import { useAppStore } from "@/store/useAppStore";
import { DashboardPanel } from "@/components/dashboard/DashboardPanel";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { checkBackendHealth } from "@/lib/api";
import {
  Activity,
  Cpu,
  Signal,
  Wifi,
  WifiOff,
  TrendingUp,
} from "lucide-react";

export default function HomePage() {
  const isBackendConnected = useAppStore((s) => s.isBackendConnected);
  const setBackendConnected = useAppStore((s) => s.setBackendConnected);

  // ── Health Check on Mount ──────────────────────────────────────────────
  useEffect(() => {
    let mounted = true;

    const check = async () => {
      const healthy = await checkBackendHealth();
      if (mounted) setBackendConnected(healthy);
    };

    check();
    // Re-check every 15 seconds
    const interval = setInterval(check, 15_000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [setBackendConnected]);

  return (
    <div className="h-screen flex flex-col" id="app-root">
      {/* ═══════════════════════════════════════════════════════════════════
          TOP NAVIGATION BAR
          ═══════════════════════════════════════════════════════════════════ */}
      <header className="flex-shrink-0 h-12 border-b border-border bg-surface-900/80 backdrop-blur-md z-50">
        <div className="h-full flex items-center justify-between px-4">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent via-accent-dark to-bull flex items-center justify-center shadow-glow">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-sm font-bold text-text-primary leading-none">
                AI Trading Co-Pilot
              </h1>
              <p className="text-[10px] text-text-muted leading-none mt-0.5">
                Dual-Engine · Multi-Agent
              </p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-3">
            {/* Engine Status */}
            <div className="hidden md:flex items-center gap-2 text-[11px]">
              <div className="flex items-center gap-1 text-text-muted">
                <Cpu className="w-3 h-3" />
                <span>Quant Engine</span>
                <span className="w-1.5 h-1.5 rounded-full bg-bull animate-pulse" />
              </div>
              <div className="w-px h-3 bg-border" />
              <div className="flex items-center gap-1 text-text-muted">
                <Activity className="w-3 h-3" />
                <span>RAG Pipeline</span>
                <span className="w-1.5 h-1.5 rounded-full bg-bull animate-pulse" />
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-800 border border-border text-[11px]">
              {isBackendConnected ? (
                <>
                  <Wifi className="w-3 h-3 text-bull" />
                  <span className="text-bull font-medium">Live</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3 h-3 text-bear" />
                  <span className="text-bear font-medium">Offline</span>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════════
          MAIN CONTENT — SPLIT SCREEN
          ═══════════════════════════════════════════════════════════════════ */}
      <main className="flex-1 flex min-h-0 overflow-hidden">
        <Group direction="horizontal">
          {/* ── Dashboard Panel ───────────────────────────────────── */}
          <Panel defaultSize={65} minSize={30}>
            <div className="h-full p-3 pr-1.5 overflow-hidden">
              <div className="h-full glass-panel p-4 overflow-hidden flex flex-col">
                <DashboardPanel />
              </div>
            </div>
          </Panel>

          {/* ── Vertical Divider Handle ─────────────────────────────────── */}
          <Separator className="w-1.5 group flex items-center justify-center">
            <div className="w-px h-12 bg-border group-hover:bg-accent/50 group-hover:w-1 transition-all rounded" />
          </Separator>

          {/* ── Chat Co-Pilot Panel ───────────────────────────────── */}
          <Panel defaultSize={35} minSize={25}>
            <div className="h-full p-3 pl-1.5 overflow-hidden">
              <div className="h-full glass-panel overflow-hidden flex flex-col">
                <ChatPanel />
              </div>
            </div>
          </Panel>
        </Group>
      </main>

      {/* ═══════════════════════════════════════════════════════════════════
          BOTTOM STATUS BAR
          ═══════════════════════════════════════════════════════════════════ */}
      <footer className="flex-shrink-0 h-8 border-t border-border bg-surface-900/60 backdrop-blur-sm">
        <div className="h-full flex items-center justify-between px-4 text-[10px] text-text-muted">
          <div className="flex items-center gap-3">
            <span>v0.1.0</span>
            <span>·</span>
            <span className="text-accent/80 font-medium">For educational and informational purposes only. Not financial advice.</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Signal className="w-2.5 h-2.5" />
              API: {isBackendConnected ? "Connected" : "Disconnected"}
            </span>
            <span>·</span>
            <span suppressHydrationWarning>{new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
