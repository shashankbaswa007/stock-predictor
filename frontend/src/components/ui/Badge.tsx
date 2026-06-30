/**
 * Badge.tsx — Signal & Status Badges
 * ===================================
 * Visual indicators for BUY/SELL/HOLD signals and status labels.
 */

"use client";

import React from "react";
import { cn, signalClass } from "@/lib/utils";

interface BadgeProps {
  label: string;
  variant?: "signal" | "status" | "tag";
  signal?: string | null;
  className?: string;
}

export function Badge({ label, variant = "tag", signal, className }: BadgeProps) {
  if (variant === "signal" && signal) {
    return (
      <span className={cn("signal-badge", signalClass(signal), className)}>
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full",
            signal === "BUY" && "bg-bull",
            signal === "SELL" && "bg-bear",
            signal === "HOLD" && "bg-accent"
          )}
        />
        {label}
      </span>
    );
  }

  if (variant === "status") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs",
          "bg-surface-700 text-text-secondary border border-border",
          className
        )}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-bull animate-pulse" />
        {label}
      </span>
    );
  }

  // Default tag style
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium",
        "bg-surface-700/50 text-text-secondary border border-border",
        className
      )}
    >
      {label}
    </span>
  );
}
