import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* ── API Proxy to FastAPI Backend ──────────────────────────────────────── */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
