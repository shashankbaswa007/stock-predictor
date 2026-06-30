/**
 * Spinner.tsx — Loading Spinner
 * ==============================
 * Animated spinner with size variants for loading states.
 */

"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: "w-4 h-4 border-[1.5px]",
  md: "w-6 h-6 border-2",
  lg: "w-10 h-10 border-[3px]",
};

export function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <div
      className={cn(
        "animate-spin rounded-full border-accent/30 border-t-accent",
        sizeMap[size],
        className
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
