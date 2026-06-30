/**
 * ChatInput.tsx — Chat Input Bar
 * ===============================
 * Message composition with send button, keyboard shortcuts,
 * and quick-action chips for common queries.
 */

"use client";

import React, { useState, useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";
import { Send, Zap } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const QUICK_ACTIONS = [
  { label: "Analyze", prompt: "Analyze {ticker} for a short-term trade" },
  { label: "Outlook", prompt: "What's the long-term outlook for {ticker}?" },
  { label: "Risk", prompt: "Show my portfolio risk analysis" },
];

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState("");
  const currentTicker = useAppStore((s) => s.currentTicker);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleQuickAction = (prompt: string) => {
    const resolved = prompt.replace("{ticker}", currentTicker);
    onSend(resolved);
  };

  return (
    <div className="p-3 space-y-2" id="chat-input">
      {/* Quick Action Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide">
        <Zap className="w-3 h-3 text-text-muted flex-shrink-0" />
        {QUICK_ACTIONS.map((qa) => (
          <button
            key={qa.label}
            onClick={() => handleQuickAction(qa.prompt)}
            disabled={disabled}
            className={cn(
              "flex-shrink-0 px-2.5 py-1 rounded-full text-[11px] font-medium",
              "bg-surface-700/50 text-text-secondary border border-border",
              "hover:bg-accent/10 hover:text-accent-light hover:border-accent/30",
              "transition-all duration-200",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            {qa.label} {currentTicker}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div
        className={cn(
          "flex items-end gap-2 p-2 rounded-xl",
          "bg-surface-900/80 border border-border",
          "focus-within:border-accent/40 focus-within:shadow-glow",
          "transition-all duration-200"
        )}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask about ${currentTicker}...`}
          disabled={disabled}
          rows={1}
          className={cn(
            "flex-1 bg-transparent text-sm text-text-primary",
            "placeholder:text-text-muted resize-none outline-none",
            "min-h-[36px] max-h-[120px] py-1.5 px-1",
            disabled && "opacity-50"
          )}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className={cn(
            "flex-shrink-0 p-2 rounded-lg transition-all duration-200",
            input.trim() && !disabled
              ? "bg-accent text-white hover:bg-accent-dark shadow-glow"
              : "bg-surface-700 text-text-muted cursor-not-allowed"
          )}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      {/* Hint */}
      <p className="text-[10px] text-text-muted text-center">
        Press <kbd className="px-1 py-0.5 rounded bg-surface-700 text-text-secondary text-[9px]">Enter</kbd> to send
        · <kbd className="px-1 py-0.5 rounded bg-surface-700 text-text-secondary text-[9px]">Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
