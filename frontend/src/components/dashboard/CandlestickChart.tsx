"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, CrosshairMode, CandlestickSeries, HistogramSeries } from "lightweight-charts";

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

export function CandlestickChart({ data }: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return;

    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "rgba(255, 255, 255, 0.5)",
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.05)" },
        horzLines: { color: "rgba(255, 255, 255, 0.05)" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: "rgba(255, 255, 255, 0.1)",
      },
      timeScale: {
        borderColor: "rgba(255, 255, 255, 0.1)",
        timeVisible: false,
        secondsVisible: false,
      },
      autoSize: true, // Automatically handles resize
    });

    // Add candlestick series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    // Format data for lightweight-charts
    const formattedData = data.map((d) => {
      // Lightweight charts expects time as a string 'YYYY-MM-DD' for daily data
      // Or Unix timestamp for intraday. We'll use YYYY-MM-DD for consistency
      const dObj = new Date(d.timestamp);
      return {
        time: dObj.toISOString().split('T')[0] as any,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      };
    }).sort((a, b) => a.time.localeCompare(b.time));

    // Remove duplicates which lightweight-charts rejects
    const uniqueData = formattedData.filter((v, i, a) => a.findIndex(t => (t.time === v.time)) === i);

    candlestickSeries.setData(uniqueData);

    // Optional: Add volume as a histogram at the bottom
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // Set as an overlay
    });
    
    // Scale volume to be at the bottom 20% of the chart
    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    const formattedVolume = uniqueData.map((d, idx) => ({
      time: d.time,
      value: data[idx].volume,
      color: d.close >= d.open ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
    }));
    
    volumeSeries.setData(formattedVolume);

    // Cleanup on unmount
    return () => {
      chart.remove();
    };
  }, [data]);

  return <div ref={chartContainerRef} className="w-full h-full" />;
}
