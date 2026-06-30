import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      /* ── Fintech Color Palette ──────────────────────────────────────── */
      colors: {
        // Base surfaces — deep navy to slate
        surface: {
          "950": "#0a0e1a",   // Deepest background
          "900": "#0f1629",   // Primary background
          "800": "#151d35",   // Card background
          "700": "#1c2642",   // Elevated surface
          "600": "#243050",   // Hover state
          "500": "#2d3a5e",   // Active state
        },
        // Accent — emerald for positive / bullish
        bull: {
          DEFAULT: "#10b981",
          light: "#34d399",
          dark: "#059669",
          muted: "rgba(16, 185, 129, 0.15)",
        },
        // Accent — rose for negative / bearish
        bear: {
          DEFAULT: "#f43f5e",
          light: "#fb7185",
          dark: "#e11d48",
          muted: "rgba(244, 63, 94, 0.15)",
        },
        // Neutral text shades
        text: {
          primary: "#e2e8f0",
          secondary: "#94a3b8",
          muted: "#64748b",
          inverse: "#0f172a",
        },
        // Accent blue for interactive elements
        accent: {
          DEFAULT: "#3b82f6",
          light: "#60a5fa",
          dark: "#2563eb",
          muted: "rgba(59, 130, 246, 0.15)",
        },
        // Border and divider colors
        border: {
          DEFAULT: "rgba(148, 163, 184, 0.12)",
          hover: "rgba(148, 163, 184, 0.25)",
          active: "rgba(59, 130, 246, 0.5)",
        },
      },
      /* ── Typography ─────────────────────────────────────────────────── */
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      /* ── Custom Shadows ─────────────────────────────────────────────── */
      boxShadow: {
        glow: "0 0 20px rgba(59, 130, 246, 0.15)",
        "glow-bull": "0 0 20px rgba(16, 185, 129, 0.2)",
        "glow-bear": "0 0 20px rgba(244, 63, 94, 0.2)",
        glass: "0 8px 32px rgba(0, 0, 0, 0.3)",
      },
      /* ── Backdrop Blur ──────────────────────────────────────────────── */
      backdropBlur: {
        xs: "2px",
      },
      /* ── Animations ─────────────────────────────────────────────────── */
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "ticker-scroll": "tickerScroll 30s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 15px rgba(59, 130, 246, 0.1)" },
          "50%": { boxShadow: "0 0 25px rgba(59, 130, 246, 0.3)" },
        },
        tickerScroll: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
