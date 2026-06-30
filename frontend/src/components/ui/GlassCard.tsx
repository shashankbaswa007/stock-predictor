/**
 * GlassCard.tsx — Frosted Glass Container Component
 * ==================================================
 * Reusable glass-morphism card with optional header, hover effects,
 * and glow variants for the fintech dark theme.
 */

"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  header?: React.ReactNode;
  /** Adds hover glow effect */
  hoverable?: boolean;
  /** Glow color variant */
  glow?: "none" | "accent" | "bull" | "bear";
  /** HTML id for testing */
  id?: string;
}

export function GlassCard({
  children,
  className,
  header,
  hoverable = false,
  glow = "none",
  id,
}: GlassCardProps) {
  const glowMap = {
    none: "",
    accent: "shadow-glow",
    bull: "shadow-glow-bull",
    bear: "shadow-glow-bear",
  };

  return (
    <div
      id={id}
      className={cn(
        hoverable ? "glass-panel-hover" : "glass-panel",
        glowMap[glow],
        "overflow-hidden",
        className
      )}
    >
      {header && (
        <>
          <div className="px-4 py-3 flex items-center justify-between">
            {header}
          </div>
          <div className="divider-glow" />
        </>
      )}
      {children}
    </div>
  );
}
