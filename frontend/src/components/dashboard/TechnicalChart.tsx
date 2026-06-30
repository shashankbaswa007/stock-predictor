"use client";

import React, { useMemo } from "react";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface TechnicalData {
  timestamp: string;
  rsi: number;
  macd: number;
  macd_signal: number;
  macd_hist: number;
}

interface TechnicalChartProps {
  data: TechnicalData[];
  type: "RSI" | "MACD";
}

export function TechnicalChart({ data, type }: TechnicalChartProps) {
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

  return (
    <div className="w-full h-full text-xs font-mono">
      <ResponsiveContainer width="100%" height="100%">
        {type === "RSI" ? (
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="date" hide />
            <YAxis 
              domain={[0, 100]} 
              stroke="rgba(255,255,255,0.3)" 
              tick={{ fill: "rgba(255,255,255,0.5)" }}
              tickCount={5}
              orientation="right"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-surface-800 border border-border p-2 rounded-lg shadow-lg">
                      <p className="text-text-primary">RSI: {payload[0].value?.toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine y={70} stroke="rgba(239, 68, 68, 0.5)" strokeDasharray="3 3" />
            <ReferenceLine y={30} stroke="rgba(34, 197, 94, 0.5)" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="rsi"
              stroke="#8b5cf6" // accent color
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        ) : (
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="date" hide />
            <YAxis 
              stroke="rgba(255,255,255,0.3)" 
              tick={{ fill: "rgba(255,255,255,0.5)" }}
              tickFormatter={(val) => val.toFixed(1)}
              orientation="right"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length >= 3) {
                  return (
                    <div className="bg-surface-800 border border-border p-2 rounded-lg shadow-lg">
                      <p className="text-bull">MACD: {Number(payload[1].value).toFixed(2)}</p>
                      <p className="text-bear">Signal: {Number(payload[2].value).toFixed(2)}</p>
                      <p className="text-text-muted">Hist: {Number(payload[0].value).toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            {/* MACD Histogram (Bar) */}
            <Bar
              dataKey="macd_hist"
              isAnimationActive={false}
              shape={(props: any) => {
                const { x, y, width, height, value } = props;
                const fill = value >= 0 ? "rgba(34, 197, 94, 0.5)" : "rgba(239, 68, 68, 0.5)";
                return <rect x={x} y={y} width={width} height={height} fill={fill} />;
              }}
            />
            {/* MACD Line */}
            <Line
              type="monotone"
              dataKey="macd"
              stroke="#3b82f6"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
            {/* Signal Line */}
            <Line
              type="monotone"
              dataKey="macd_signal"
              stroke="#f59e0b"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
