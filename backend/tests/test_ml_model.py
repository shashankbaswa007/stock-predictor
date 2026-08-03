import numpy as np
import pandas as pd
import pytest

from services.ml_model import StockPredictor, _create_lag_features, _prepare_features, quick_predict


@pytest.fixture
def sample_df():
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100)

    # Generate somewhat realistic looking random walk prices
    returns = np.random.normal(0.001, 0.02, 100)
    prices = 100 * np.exp(np.cumsum(returns))

    return pd.DataFrame({
        "timestamp": dates,
        "open": prices * np.random.uniform(0.99, 1.01, 100),
        "high": prices * np.random.uniform(1.01, 1.05, 100),
        "low": prices * np.random.uniform(0.95, 0.99, 100),
        "close": prices,
        "volume": np.random.randint(1000, 5000, 100)
    })

def test_create_lag_features(sample_df):
    df_lags = _create_lag_features(sample_df, n_lags=3)

    # Check expected columns
    assert "log_return" in df_lags.columns
    assert "return_lag_1" in df_lags.columns
    assert "return_lag_2" in df_lags.columns
    assert "return_lag_3" in df_lags.columns
    assert "return_rolling_mean_5" in df_lags.columns

    # First few rows should have NaNs for lags
    assert pd.isna(df_lags["return_lag_3"].iloc[0])
    assert pd.isna(df_lags["return_lag_3"].iloc[2])
    assert not pd.isna(df_lags["return_lag_3"].iloc[4])

def test_prepare_features(sample_df):
    enriched, feature_cols = _prepare_features(sample_df, n_lags=5)

    # Check that rows with NaNs were dropped
    assert enriched.isna().sum().sum() == 0
    # Length should be reduced (max of lag windows and indicator windows, e.g., SMA 50 -> drops 49 rows)
    assert len(enriched) < len(sample_df)

    # Check feature_cols doesn't include targets or raw prices
    assert "close" not in feature_cols
    assert "target" not in feature_cols
    assert "sma_10" in feature_cols

def test_stock_predictor(sample_df):
    model = StockPredictor(alpha=1.0, n_lags=5)

    # Test fit
    metrics = model.fit(sample_df)
    assert model.is_fitted
    assert metrics["train_mae"] >= 0
    assert metrics["val_mae"] >= 0

    # Test predict
    forecast = model.predict(sample_df, n_steps=3)
    assert len(forecast["predictions"]) == 3
    assert forecast["signal"] in ["BUY", "SELL", "HOLD"]
    assert 0 <= forecast["confidence_score"] <= 1

def test_quick_predict(sample_df):
    forecast = quick_predict(sample_df, n_steps=2)
    assert len(forecast["predictions"]) == 2
    assert "train_metrics" in forecast
