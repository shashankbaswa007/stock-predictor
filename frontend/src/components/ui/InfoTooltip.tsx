import React from "react";
import { Info } from "lucide-react";

interface InfoTooltipProps {
  content: string;
  children?: React.ReactNode;
}

export function InfoTooltip({ content, children }: InfoTooltipProps) {
  return (
    <div className="group relative inline-flex items-center gap-1 cursor-help">
      {children}
      <Info className="w-3.5 h-3.5 text-text-muted group-hover:text-accent transition-colors" />
      <div className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-800 text-text-primary text-xs p-2 rounded border border-border shadow-lg z-50">
        {content}
        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-surface-800" />
      </div>
    </div>
  );
}
