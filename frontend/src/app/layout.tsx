/**
 * layout.tsx — Root Layout
 * =========================
 * Sets up the HTML shell with:
 *  • Dark theme (class="dark" on <html>)
 *  • Inter + JetBrains Mono fonts from Google Fonts
 *  • SEO metadata
 *  • Zero CLS with explicit viewport and font-display
 */

import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Trading Co-Pilot | Dual-Engine Stock Analysis",
  description:
    "AI-powered stock prediction and portfolio management platform with " +
    "dual-engine analysis: Short-Term ML predictions and Long-Term RAG-based " +
    "fundamental analysis. Multi-agent AI architecture for actionable trading insights.",
  keywords: ["stock prediction", "AI trading", "portfolio management", "technical analysis"],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0f1629",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        {/* Google Fonts — Inter (UI) + JetBrains Mono (data) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-surface-950 text-text-primary font-sans antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}
