/**
 * ChatMessage.tsx — Individual Chat Message Bubble
 * =================================================
 * Renders user and AI messages with markdown support,
 * signal badges, confidence meters, and reasoning citations.
 */

"use client";

import React from "react";
import type { ChatMessage as ChatMessageType } from "@/store/useAppStore";
import { Badge } from "@/components/ui/Badge";
import { cn, formatPercent } from "@/lib/utils";
import { Bot, User, ChevronRight, Sparkles } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex items-start gap-3 animate-slide-up",
        isUser && "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5",
          isUser
            ? "bg-accent/20 border border-accent/30"
            : "bg-surface-700 border border-border"
        )}
      >
        {isUser ? (
          <User className="w-3.5 h-3.5 text-accent" />
        ) : (
          <Bot className="w-3.5 h-3.5 text-accent" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn("flex flex-col gap-1.5", isUser ? "items-end" : "items-start")}>
        
        {/* Generative UI: Signal Card */}
        {!isUser && message.signal ? (
          <div className="w-[300px] flex flex-col gap-0 rounded-xl overflow-hidden border border-border/60 shadow-lg animate-fade-in bg-surface-800">
            {/* Header: Signal & Confidence */}
            <div className={cn(
              "px-4 py-3 flex items-center justify-between border-b border-border/40",
              message.signal === "BUY" ? "bg-bull/10" : message.signal === "SELL" ? "bg-bear/10" : "bg-surface-700/50"
            )}>
              <Badge label={message.signal} variant="signal" signal={message.signal} />
              {message.confidence != null && (
                <div className="flex flex-col items-end">
                  <span className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Confidence</span>
                  <span className={cn(
                    "text-lg font-mono font-bold leading-none",
                    message.confidence >= 0.7 ? "text-bull" : message.confidence >= 0.4 ? "text-accent" : "text-bear"
                  )}>
                    {(message.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}
            </div>
            
            {/* Body: Reasoning Bullets */}
            {message.reasoning && message.reasoning.length > 0 && (
              <div className="px-4 py-3 space-y-2.5">
                <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold mb-1">Key Factors</p>
                {message.reasoning.map((r, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-accent/70 mt-0.5 shrink-0" />
                    <span className="text-xs text-text-secondary leading-relaxed">{r}</span>
                  </div>
                ))}
              </div>
            )}
            
            {/* Citations Footer */}
            {message.citations && message.citations.length > 0 && (
              <div className="px-4 py-2 bg-surface-900 border-t border-border/40 flex flex-wrap gap-2 items-center">
                <span className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Sources:</span>
                {message.citations.map((cite, i) => (
                  <span key={i} className="text-[10px] bg-accent/10 text-accent border border-accent/20 px-1.5 py-0.5 rounded cursor-pointer hover:bg-accent/20 transition-colors">
                    {cite}
                  </span>
                ))}
              </div>
            )}
            
            {/* Collapsed Detailed Text (Optional) */}
            {message.content && (
              <div className="px-4 py-2 bg-surface-900/50 border-t border-border/40">
                <details className="group">
                  <summary className="text-[11px] text-text-muted cursor-pointer hover:text-text-primary transition-colors flex items-center gap-1">
                    <ChevronRight className="w-3 h-3 transition-transform group-open:rotate-90" />
                    Read Detailed Analysis
                  </summary>
                  <div className="pt-2 pb-1 text-[11px] text-text-secondary leading-relaxed whitespace-pre-wrap">
                    {renderSimpleMarkdown(message.content)}
                  </div>
                </details>
              </div>
            )}
          </div>
        ) : (
          /* Standard Chat Bubble for normal text */
          <div className={cn("chat-bubble", isUser ? "user" : "ai")}>
            <div className="text-sm leading-relaxed whitespace-pre-wrap">
              {renderSimpleMarkdown(message.content)}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <span suppressHydrationWarning className="text-[10px] text-text-muted px-1 mt-1">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}

// ── Simple Markdown Renderer ─────────────────────────────────────────────────

function renderSimpleMarkdown(text: string): React.ReactNode {
  // Split into lines and process
  const parts: React.ReactNode[] = [];
  const lines = text.split("\n");

  lines.forEach((line, i) => {
    let processed: React.ReactNode = line;

    // Bold: **text**
    if (line.includes("**")) {
      const segments = line.split(/\*\*(.*?)\*\*/g);
      processed = segments.map((seg, j) =>
        j % 2 === 1 ? (
          <strong key={j} className="font-semibold text-text-primary">
            {seg}
          </strong>
        ) : (
          seg
        )
      );
    }

    // Italic: *text*
    if (typeof processed === "string" && processed.includes("*")) {
      const segments = processed.split(/\*(.*?)\*/g);
      processed = segments.map((seg, j) =>
        j % 2 === 1 ? (
          <em key={j} className="italic text-text-secondary">
            {seg}
          </em>
        ) : (
          seg
        )
      );
    }

    // Inline code: `text`
    if (typeof processed === "string" && processed.includes("`")) {
      const segments = processed.split(/`(.*?)`/g);
      processed = segments.map((seg, j) =>
        j % 2 === 1 ? (
          <code
            key={j}
            className="px-1 py-0.5 rounded bg-surface-900/80 text-accent-light text-xs font-mono"
          >
            {seg}
          </code>
        ) : (
          seg
        )
      );
    }

    // Bullet points: • or -
    if (line.startsWith("• ") || line.startsWith("- ")) {
      processed = (
        <div className="flex items-start gap-1.5 ml-1">
          <span className="text-accent mt-1">•</span>
          <span>{typeof processed === "string" ? processed.slice(2) : processed}</span>
        </div>
      );
    }

    parts.push(
      <React.Fragment key={i}>
        {processed}
        {i < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });

  return parts;
}
