import numpy as np
import pandas as pd
import pytest

from services.technical_indicators import bollinger_bands, compute_all, ema, macd, rsi, sma


@pytest.fixture
def sample_df():
    # Create a simple upward trending dataframe
    dates = pd.date_range("2023-01-01", periods=100)
    prices = np.linspace(100, 200, 100)

    return pd.DataFrame({
        "timestamp": dates,
        "open": prices * 0.99,
        "high": prices * 1.01,
        "low": prices * 0.98,
        "close": prices,
        "volume": np.random.randint(1000, 5000, 100)
    })

def test_sma(sample_df):
    sma_20 = sma(sample_df["close"], period=20)
    assert len(sma_20) == 100
    assert pd.isna(sma_20.iloc[0])
    assert not pd.isna(sma_20.iloc[19])

    # Since prices are linearly increasing, SMA should be lower than current price
    assert sma_20.iloc[-1] < sample_df["close"].iloc[-1]

def test_ema(sample_df):
    ema_20 = ema(sample_df["close"], period=20)
    assert len(ema_20) == 100
    assert not pd.isna(ema_20.iloc[-1])
    # EMA responds faster, should be closer to current price than SMA in a trend
    sma_20 = sma(sample_df["close"], period=20)
    assert ema_20.iloc[-1] > sma_20.iloc[-1]

def test_rsi(sample_df):
    rsi_14 = rsi(sample_df["close"], period=14)
    # Since it's a straight line up, RSI should be 100
    assert rsi_14.iloc[-1] == 100.0

def test_macd(sample_df):
    macd_data = macd(sample_df["close"])
    assert "macd" in macd_data
    assert "signal" in macd_data
    assert "histogram" in macd_data

def test_bollinger_bands(sample_df):
    bb = bollinger_bands(sample_df["close"])
    assert "upper" in bb
    assert "middle" in bb
    assert "lower" in bb
    assert "bandwidth" in bb
    assert "percent_b" in bb

def test_compute_all(sample_df):
    enriched = compute_all(sample_df)

    expected_cols = [
        "sma_10", "sma_20", "sma_50", "ema_12", "ema_26", "rsi",
        "macd", "macd_signal", "macd_histogram",
        "bb_upper", "bb_middle", "bb_lower", "bb_bandwidth", "bb_percent_b"
    ]

    for col in expected_cols:
        assert col in enriched.columns
