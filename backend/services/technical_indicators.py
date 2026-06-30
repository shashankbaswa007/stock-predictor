"""
technical_indicators.py — Pure Python/Pandas Technical Indicator Calculations
==============================================================================
Implements standard technical analysis indicators as clean, composable functions.
All functions accept and return pandas DataFrames/Series for seamless integration
with both the ML feature pipeline and frontend chart data.

Indicators:
  • SMA   — Simple Moving Average
  • EMA   — Exponential Moving Average
  • RSI   — Relative Strength Index (Wilder's method)
  • MACD  — Moving Average Convergence Divergence
  • BB    — Bollinger Bands
  • compute_all() — Convenience function to add all indicators to OHLCV data
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# MOVING AVERAGES
# ═══════════════════════════════════════════════════════════════════════════════

def sma(series: pd.Series, period: int = 20) -> pd.Series:
    """
    Simple Moving Average.

    The arithmetic mean of the last `period` closing prices.
    First (period - 1) values will be NaN.

    Args:
        series: Price series (typically 'close')
        period: Lookback window

    Returns:
        Series of SMA values
    """
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int = 20) -> pd.Series:
    """
    Exponential Moving Average.

    Applies exponential weighting with decay factor α = 2 / (period + 1).
    More responsive to recent price changes than SMA.

    Args:
        series: Price series (typically 'close')
        period: Lookback window (span)

    Returns:
        Series of EMA values
    """
    return series.ewm(span=period, adjust=False).mean()


# ═══════════════════════════════════════════════════════════════════════════════
# RSI — RELATIVE STRENGTH INDEX
# ═══════════════════════════════════════════════════════════════════════════════

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index using Wilder's smoothing method.

    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over `period` bars.

    Wilder's smoothing: running average using (prev_avg * (period-1) + current) / period.

    Interpretation:
        RSI > 70 → Overbought (potential sell signal)
        RSI < 30 → Oversold  (potential buy signal)

    Args:
        series: Price series (typically 'close')
        period: Lookback window (default 14 per Wilder)

    Returns:
        Series of RSI values (0–100)
    """
    # Price changes
    delta = series.diff()

    # Separate gains and losses
    gains = delta.clip(lower=0)
    losses = (-delta).clip(lower=0)

    # Wilder's smoothing (equivalent to EMA with alpha = 1/period)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    # Relative Strength
    rs = avg_gain / avg_loss.replace(0, np.nan)

    # RSI formula
    result = 100 - (100 / (1 + rs))

    # Handle edge cases: if avg_loss is 0, RSI = 100
    result = result.fillna(100)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MACD — MOVING AVERAGE CONVERGENCE DIVERGENCE
# ═══════════════════════════════════════════════════════════════════════════════

def macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Dict[str, pd.Series]:
    """
    MACD with Signal Line and Histogram.

    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal_period)
    Histogram = MACD Line - Signal Line

    Interpretation:
        MACD crosses above Signal → Bullish
        MACD crosses below Signal → Bearish
        Histogram shows momentum strength

    Args:
        series:        Price series (typically 'close')
        fast_period:   Fast EMA period (default 12)
        slow_period:   Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)

    Returns:
        Dict with keys: 'macd', 'signal', 'histogram'
    """
    ema_fast = ema(series, fast_period)
    ema_slow = ema(series, slow_period)

    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BOLLINGER BANDS
# ═══════════════════════════════════════════════════════════════════════════════

def bollinger_bands(
    series: pd.Series,
    period: int = 20,
    num_std: float = 2.0,
) -> Dict[str, pd.Series]:
    """
    Bollinger Bands — SMA ± (num_std × standard deviation).

    Measures volatility and identifies overbought/oversold conditions.
    Price touching the upper band may signal overbought; lower band, oversold.

    Args:
        series:  Price series (typically 'close')
        period:  SMA lookback window (default 20)
        num_std: Number of standard deviations (default 2.0)

    Returns:
        Dict with keys: 'upper', 'middle', 'lower', 'bandwidth', 'percent_b'
    """
    middle = sma(series, period)
    rolling_std = series.rolling(window=period, min_periods=period).std()

    upper = middle + (rolling_std * num_std)
    lower = middle - (rolling_std * num_std)

    # Bandwidth: (Upper - Lower) / Middle — normalized volatility measure
    bandwidth = (upper - lower) / middle

    # %B: (Price - Lower) / (Upper - Lower) — where price is within the bands
    percent_b = (series - lower) / (upper - lower)

    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
        "bandwidth": bandwidth,
        "percent_b": percent_b,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE: COMPUTE ALL INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_all(
    df: pd.DataFrame,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    bb_period: int = 20,
    bb_std: float = 2.0,
    sma_periods: Optional[list] = None,
) -> pd.DataFrame:
    """
    Add all standard technical indicators to an OHLCV DataFrame.

    Args:
        df: DataFrame with at least a 'close' column
        rsi_period:   RSI lookback period
        macd_fast:    MACD fast EMA period
        macd_slow:    MACD slow EMA period
        macd_signal:  MACD signal line EMA period
        bb_period:    Bollinger Band SMA period
        bb_std:       Bollinger Band standard deviation multiplier
        sma_periods:  List of SMA periods to compute (default [10, 20, 50])

    Returns:
        DataFrame with original columns + all indicator columns added
    """
    if sma_periods is None:
        sma_periods = [10, 20, 50]

    result = df.copy()
    close = result["close"]

    # SMAs
    for period in sma_periods:
        result[f"sma_{period}"] = sma(close, period)

    # EMAs
    result["ema_12"] = ema(close, 12)
    result["ema_26"] = ema(close, 26)

    # RSI
    result["rsi"] = rsi(close, rsi_period)

    # MACD
    macd_data = macd(close, macd_fast, macd_slow, macd_signal)
    result["macd"] = macd_data["macd"]
    result["macd_signal"] = macd_data["signal"]
    result["macd_histogram"] = macd_data["histogram"]

    # Bollinger Bands
    bb_data = bollinger_bands(close, bb_period, bb_std)
    result["bb_upper"] = bb_data["upper"]
    result["bb_middle"] = bb_data["middle"]
    result["bb_lower"] = bb_data["lower"]
    result["bb_bandwidth"] = bb_data["bandwidth"]
    result["bb_percent_b"] = bb_data["percent_b"]

    # Round all float columns to 4 decimal places for clean output
    float_cols = result.select_dtypes(include=[np.floating]).columns
    result[float_cols] = result[float_cols].round(4)
    
    # Replace NaN/Infinity with None for clean JSON serialization in FastAPI
    result.replace([np.inf, -np.inf, np.nan], None, inplace=True)

    return result
