"""
main.py — FastAPI Application Entry Point
==========================================
Bootstraps the FastAPI app with:
  • CORS middleware (frontend at localhost:3000)
  • Health-check endpoint
  • Router registration for market, chat, portfolio, and WebSocket routes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes_market import router as market_router
from api.routes_chat import router as chat_router
from api.routes_portfolio import router as portfolio_router
from api.routes_ws import router as ws_router

# ── App Initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title="AI Trading Co-Pilot API",
    description="Dual-engine, multi-agent stock prediction backend",
    version="0.1.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Route Registration ───────────────────────────────────────────────────────
app.include_router(market_router, prefix="/api/market", tags=["Market Data"])
app.include_router(chat_router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(ws_router, tags=["WebSocket"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    """Returns server status and current configuration mode."""
    return {
        "status": "healthy",
        "env": settings.app_env,
        "mock_market_data": settings.use_mock_market_data,
        "mock_llm": settings.use_mock_llm,
    }
