"""
routes_portfolio.py — Portfolio Management API Routes
=====================================================
CRUD operations for portfolio holdings and risk metrics.
Phase 1: Stub with mock portfolio state.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()


# ── Models ────────────────────────────────────────────────────────────────────

class Holding(BaseModel):
    """A single portfolio holding."""
    ticker: str
    shares: float
    avg_cost: float
    current_price: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    weight: float = 0.0  # Portfolio weight as decimal


class PortfolioSummary(BaseModel):
    """Overall portfolio summary."""
    total_value: float = 0.0
    total_pnl: float = 0.0
    total_pnl_percent: float = 0.0
    holdings: List[Holding] = []
    cash: float = 0.0
    var_95: Optional[float] = None  # 95% Value at Risk


# ── Mock Portfolio ────────────────────────────────────────────────────────────

MOCK_PORTFOLIO = PortfolioSummary(
    total_value=125_430.50,
    total_pnl=8_320.75,
    total_pnl_percent=7.1,
    cash=15_000.00,
    var_95=-3_250.00,
    holdings=[
        Holding(ticker="AAPL", shares=50, avg_cost=178.50, current_price=195.20,
                pnl=835.00, pnl_percent=9.36, weight=0.35),
        Holding(ticker="MSFT", shares=30, avg_cost=380.00, current_price=415.60,
                pnl=1068.00, pnl_percent=9.37, weight=0.28),
        Holding(ticker="NVDA", shares=20, avg_cost=850.00, current_price=920.30,
                pnl=1406.00, pnl_percent=8.27, weight=0.22),
        Holding(ticker="GOOGL", shares=25, avg_cost=165.00, current_price=172.80,
                pnl=195.00, pnl_percent=4.73, weight=0.10),
        Holding(ticker="AMZN", shares=10, avg_cost=185.00, current_price=193.50,
                pnl=85.00, pnl_percent=4.59, weight=0.05),
    ],
)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=PortfolioSummary)
async def get_portfolio():
    """Returns current portfolio holdings and summary metrics."""
    return MOCK_PORTFOLIO


@router.get("/risk")
async def get_risk_metrics():
    """Returns portfolio risk metrics (VaR, sector exposure, etc.)."""
    return {
        "var_95": MOCK_PORTFOLIO.var_95,
        "sharpe_ratio": 1.85,
        "beta": 1.12,
        "sector_exposure": {
            "Technology": 0.95,
            "Consumer Discretionary": 0.05,
        },
        "max_drawdown": -0.082,
        "message": "Risk calculations will be enhanced in Phase 3.",
    }
