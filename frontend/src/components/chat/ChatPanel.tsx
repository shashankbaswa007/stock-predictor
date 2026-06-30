/**
 * ChatPanel.tsx — AI Co-Pilot Chat Interface
 * ============================================
 * Right side (35%) of the split-screen layout.
 * Full conversational interface with message history, input bar,
 * and UI action handler.
 */

"use client";

import React, { useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { sendChatMessage } from "@/lib/api";
import { generateId } from "@/lib/utils";
import {
  Bot,
  Sparkles,
  Trash2,
  Wifi,
  WifiOff,
} from "lucide-react";

export function ChatPanel() {
  const chatMessages = useAppStore((s) => s.chatMessages);
  const isChatLoading = useAppStore((s) => s.isChatLoading);
  const isBackendConnected = useAppStore((s) => s.isBackendConnected);
  const addMessage = useAppStore((s) => s.addMessage);
  const setChatLoading = useAppStore((s) => s.setChatLoading);
  const clearChat = useAppStore((s) => s.clearChat);
  const currentTicker = useAppStore((s) => s.currentTicker);
  const viewMode = useAppStore((s) => s.viewMode);
  const setViewMode = useAppStore((s) => s.setViewMode);
  const setTicker = useAppStore((s) => s.setTicker);
  const getUIContext = useAppStore((s) => s.getUIContext);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages, isChatLoading]);

  // ── Handle Send Message ────────────────────────────────────────────────
  const handleSend = async (message: string) => {
    // Add user message immediately
    addMessage({
      id: generateId(),
      role: "user",
      content: message,
      timestamp: Date.now(),
    });

    setChatLoading(true);

    try {
      const response = await sendChatMessage({
        message,
        ticker: currentTicker,
        ui_context: {
          view_mode: viewMode,
          portfolio_state: useAppStore.getState().portfolio,
        },
      });

      // Add AI response
      addMessage({
        id: generateId(),
        role: "ai",
        content: response.message,
        timestamp: Date.now(),
        signal: response.signal as "BUY" | "SELL" | "HOLD" | null,
        confidence: response.confidence ?? undefined,
        reasoning: response.reasoning,
      });

      // ── Process UI Action Commands ──────────────────────────────────
      if (response.ui_action) {
        const { action, payload } = response.ui_action;
        switch (action) {
          case "switch_view":
            if (payload.mode) {
              setViewMode(payload.mode as "short_term" | "long_term" | "portfolio");
            }
            break;
          case "change_ticker":
            if (payload.ticker) {
              setTicker(payload.ticker as string);
            }
            break;
          case "show_portfolio":
            setViewMode("portfolio");
            break;
        }
      }
    } catch (error) {
      // Graceful error handling — show error in chat
      addMessage({
        id: generateId(),
        role: "ai",
        content:
          "⚠️ I couldn't connect to the analysis backend. Please make sure the FastAPI server is running on `localhost:8000`.\n\n" +
          "```bash\ncd backend && .venv/bin/uvicorn main:app --reload --port 8000\n```",
        timestamp: Date.now(),
      });
    } finally {
      setChatLoading(false);
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full" id="chat-panel">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-bull flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
              AI Co-Pilot
              <Sparkles className="w-3 h-3 text-accent" />
            </h2>
            <p className="text-[10px] text-text-muted">Multi-Agent Analysis Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            label={isBackendConnected ? "Connected" : "Offline"}
            variant="status"
          />
          <button
            onClick={clearChat}
            className="p-1.5 rounded-md hover:bg-surface-700/50 text-text-muted hover:text-text-secondary transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Message List */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-hide px-4 py-4 space-y-4"
      >
        {chatMessages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* Loading indicator */}
        {isChatLoading && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="w-7 h-7 rounded-lg bg-surface-700 border border-border flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-accent" />
            </div>
            <div className="chat-bubble ai flex items-center gap-2">
              <Spinner size="sm" />
              <span className="text-xs text-text-muted">Analyzing...</span>
            </div>
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="divider-glow" />

      {/* Input Bar */}
      <ChatInput onSend={handleSend} disabled={isChatLoading} />
    </div>
  );
}
