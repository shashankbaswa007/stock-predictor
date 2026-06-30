"""
routes_market.py — Market Data API Routes (Phase 2: Fully Wired)
================================================================
Provides endpoints for:
  • Historical OHLCV data with technical indicators
  • Real-time quote snapshots
  • News headlines
  • ML-based price predictions
"""

from fastapi import APIRouter, Query, HTTPException

from services.mock_data import generate_ohlcv, generate_quote, generate_news
from services.technical_indicators import compute_all, rsi, macd, bollinger_bands
from services.ml_model import quick_predict

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORICAL DATA + INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/history")
async def get_history(
    ticker: str = Query("AAPL", description="Stock ticker symbol"),
    period: str = Query("6mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y"),
    interval: str = Query("1d", description="Candle interval: 1m, 5m, 15m, 1h, 1d, 1wk"),
    indicators: bool = Query(True, description="Include technical indicators"),
):
    """
    Returns historical OHLCV candlestick data with optional technical indicators.

    The response includes:
      • Raw OHLCV candles (open, high, low, close, volume)
      • Technical indicators (RSI, MACD, Bollinger Bands, SMAs) when indicators=true
      • Latest indicator values as a summary object

    All data is deterministic per ticker (seeded by ticker symbol hash).
    """
    try:
        # Generate OHLCV data
        df = generate_ohlcv(ticker.upper(), period, interval)

        if indicators and len(df) >= 26:
            # Compute all technical indicators
            df_enriched = compute_all(df)

            # Replace NaN with None for JSON serialization
            candles = df_enriched.where(df_enriched.notna(), None).to_dict(orient="records")

            # Extract latest indicator values for the summary panel
            latest = df_enriched.iloc[-1]
            indicator_summary = {
                "rsi": _safe_float(latest.get("rsi")),
                "macd": _safe_float(latest.get("macd")),
                "macd_signal": _safe_float(latest.get("macd_signal")),
                "macd_histogram": _safe_float(latest.get("macd_histogram")),
                "sma_10": _safe_float(latest.get("sma_10")),
                "sma_20": _safe_float(latest.get("sma_20")),
                "sma_50": _safe_float(latest.get("sma_50")),
                "ema_12": _safe_float(latest.get("ema_12")),
                "ema_26": _safe_float(latest.get("ema_26")),
                "bb_upper": _safe_float(latest.get("bb_upper")),
                "bb_middle": _safe_float(latest.get("bb_middle")),
                "bb_lower": _safe_float(latest.get("bb_lower")),
                "bb_bandwidth": _safe_float(latest.get("bb_bandwidth")),
                "bb_percent_b": _safe_float(latest.get("bb_percent_b")),
            }
        else:
            candles = df.to_dict(orient="records")
            indicator_summary = None

        return {
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "count": len(candles),
            "data": candles,
            "indicators": indicator_summary,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating market data: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/quote")
async def get_quote(
    ticker: str = Query("AAPL", description="Stock ticker symbol"),
):
    """
    Returns a real-time quote snapshot for the given ticker.
    Includes price, change, volume, and fundamental metrics.
    """
    try:
        quote = generate_quote(ticker.upper())
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quote: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS HEADLINES
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/news")
async def get_news(
    ticker: str = Query("AAPL", description="Stock ticker symbol"),
    count: int = Query(8, ge=1, le=20, description="Number of headlines"),
):
    """
    Returns mock news headlines with sentiment scores for the given ticker.
    """
    try:
        articles = generate_news(ticker.upper(), count)
        return {
            "ticker": ticker.upper(),
            "count": len(articles),
            "articles": articles,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating news: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# ML PREDICTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/predict")
async def get_prediction(
    ticker: str = Query("AAPL", description="Stock ticker symbol"),
    period: str = Query("1y", description="Training data period"),
    steps: int = Query(5, ge=1, le=20, description="Forecast horizon (# candles)"),
):
    """
    Generate ML-based price predictions for the given ticker.

    Uses Ridge Regression trained on historical OHLCV data enriched with
    technical indicators and lag features. Returns multi-step forecast
    with confidence intervals.
    """
    try:
        # Generate sufficient training data
        df = generate_ohlcv(ticker.upper(), period, "1d")
        forecast = quick_predict(df, n_steps=steps)
        forecast["ticker"] = ticker.upper()
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_float(val) -> float | None:
    """Convert a value to float, returning None for NaN/None."""
    if val is None:
        return None
    try:
        import math
        f = float(val)
        return None if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None
