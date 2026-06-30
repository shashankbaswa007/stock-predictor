"use client";

import React, { useMemo } from "react";
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface CandlestickData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickChartProps {
  data: CandlestickData[];
}

// Custom shape for candlestick
const Candlestick = (props: any) => {
  const {
    x,
    y,
    width,
    height,
    open,
    close,
    high,
    low,
    yAxis,
  } = props;

  const isBull = close >= open;
  const color = isBull ? "#22c55e" : "#ef4444"; // bull (green) / bear (red)

  // Calculate pixel coordinates
  const yOpen = yAxis.scale(open);
  const yClose = yAxis.scale(close);
  const yHigh = yAxis.scale(high);
  const yLow = yAxis.scale(low);

  const rectY = Math.min(yOpen, yClose);
  const rectHeight = Math.abs(yOpen - yClose) || 1;
  const centerX = x + width / 2;

  return (
    <g>
      {/* Wick */}
      <line
        x1={centerX}
        y1={yHigh}
        x2={centerX}
        y2={yLow}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body */}
      <rect
        x={x}
        y={rectY}
        width={width}
        height={rectHeight}
        fill={color}
        stroke={color}
      />
    </g>
  );
};

export function CandlestickChart({ data }: CandlestickChartProps) {
  // Format data for Recharts
  const chartData = useMemo(() => {
    return data.map((d) => ({
      ...d,
      date: new Date(d.timestamp).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      }),
    }));
  }, [data]);

  if (!data || data.length === 0) return null;

  // Calculate domain for Y axis to add padding
  const minLow = Math.min(...data.map((d) => d.low));
  const maxHigh = Math.max(...data.map((d) => d.high));
  const padding = (maxHigh - minLow) * 0.1;
  const domain = [minLow - padding, maxHigh + padding];

  return (
    <div className="w-full h-full text-xs font-mono">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
          <XAxis 
            dataKey="date" 
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.5)" }} 
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            domain={domain} 
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.5)" }} 
            tickFormatter={(val) => `$${val.toFixed(0)}`}
            tickLine={false}
            axisLine={false}
            orientation="right"
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                const isBull = d.close >= d.open;
                return (
                  <div className="bg-surface-800 border border-border p-2 rounded-lg shadow-lg">
                    <p className="text-text-muted mb-1">{d.date}</p>
                    <p>Open:  <span className="text-text-primary">{formatCurrency(d.open)}</span></p>
                    <p>High:  <span className="text-text-primary">{formatCurrency(d.high)}</span></p>
                    <p>Low:   <span className="text-text-primary">{formatCurrency(d.low)}</span></p>
                    <p>Close: <span className={isBull ? "text-bull" : "text-bear"}>{formatCurrency(d.close)}</span></p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar
            dataKey="close"
            shape={(props: any) => (
              <Candlestick
                {...props}
                open={props.payload.open}
                close={props.payload.close}
                high={props.payload.high}
                low={props.payload.low}
                yAxis={props.yAxis}
              />
            )}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
