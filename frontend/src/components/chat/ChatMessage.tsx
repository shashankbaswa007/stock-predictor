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
        <div className={cn("chat-bubble", isUser ? "user" : "ai")}>
          {/* Message text — simple markdown-like rendering */}
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {renderSimpleMarkdown(message.content)}
          </div>
        </div>

        {/* AI-specific metadata */}
        {!isUser && (message.signal || message.confidence != null) && (
          <div className="flex items-center gap-2 px-1">
            {message.signal && (
              <Badge label={message.signal} variant="signal" signal={message.signal} />
            )}
            {message.confidence != null && (
              <div className="flex items-center gap-1.5">
                <div className="w-16 h-1.5 rounded-full bg-surface-700 overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all duration-500",
                      message.confidence >= 0.7
                        ? "bg-bull"
                        : message.confidence >= 0.4
                        ? "bg-accent"
                        : "bg-bear"
                    )}
                    style={{ width: `${message.confidence * 100}%` }}
                  />
                </div>
                <span className="text-[10px] text-text-muted font-mono">
                  {(message.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        )}

        {/* Reasoning citations (XAI) */}
        {!isUser && message.reasoning && message.reasoning.length > 0 && (
          <div className="px-1 mt-1 flex flex-wrap gap-1.5">
            {message.reasoning.map((r, i) => (
              <div
                key={i}
                className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-surface-700/50 border border-border text-[10px] text-text-secondary whitespace-nowrap"
                title={r}
              >
                <Sparkles className="w-3 h-3 text-accent/70 flex-shrink-0" />
                <span className="truncate max-w-[200px]">{r}</span>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span suppressHydrationWarning className="text-[10px] text-text-muted px-1">
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
