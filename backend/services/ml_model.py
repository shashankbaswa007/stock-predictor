"""
ml_model.py — Lightweight Time-Series Forecasting Baseline
============================================================
Implements a scikit-learn Ridge Regression model for short-term stock price
prediction. Uses lag features + technical indicators as features.

Architecture is pluggable — this baseline can be swapped for LSTM/Transformer
models in production by implementing the same predict() interface.

Pipeline:
  1. Feature Engineering: Lag returns, rolling stats, technical indicators
  2. Train/Test Split: Chronological (no lookahead bias)
  3. Model: Ridge Regression (L2 regularized linear model)
  4. Prediction: Next-N candle forecast with confidence intervals
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from services.technical_indicators import compute_all


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

def _create_lag_features(df: pd.DataFrame, n_lags: int = 10) -> pd.DataFrame:
    """
    Create lagged return features and rolling statistics from OHLCV data.

    Features generated:
      • close_ret_lag_1..N     — Lagged log-returns
      • close_rolling_mean_5   — 5-period rolling mean of returns
      • close_rolling_std_5    — 5-period rolling std of returns
      • close_rolling_mean_10  — 10-period rolling mean of returns
      • close_rolling_std_10   — 10-period rolling std of returns
      • volume_ret_lag_1..3    — Lagged volume changes
      • range_pct              — (High - Low) / Close (intra-candle volatility)
      • body_pct               — (Close - Open) / Open (candle body)
      • upper_wick_pct         — Upper wick as % of range
      • lower_wick_pct         — Lower wick as % of range

    Args:
        df:     OHLCV DataFrame
        n_lags: Number of lag periods for returns

    Returns:
        DataFrame with original + feature columns
    """
    result = df.copy()

    # Log returns
    result["log_return"] = np.log(result["close"] / result["close"].shift(1))

    # Lagged returns
    for lag in range(1, n_lags + 1):
        result[f"return_lag_{lag}"] = result["log_return"].shift(lag)

    # Rolling statistics on returns
    for window in [5, 10]:
        result[f"return_rolling_mean_{window}"] = (
            result["log_return"].rolling(window).mean()
        )
        result[f"return_rolling_std_{window}"] = (
            result["log_return"].rolling(window).std()
        )

    # Volume features
    result["volume_change"] = result["volume"].pct_change()
    for lag in range(1, 4):
        result[f"volume_change_lag_{lag}"] = result["volume_change"].shift(lag)

    # Candlestick body features
    result["range_pct"] = (result["high"] - result["low"]) / result["close"]
    result["body_pct"] = (result["close"] - result["open"]) / result["open"]

    candle_range = result["high"] - result["low"]
    candle_range_safe = candle_range.replace(0, np.nan)
    result["upper_wick_pct"] = (
        (result["high"] - result[["close", "open"]].max(axis=1)) / candle_range_safe
    )
    result["lower_wick_pct"] = (
        (result[["close", "open"]].min(axis=1) - result["low"]) / candle_range_safe
    )

    return result


def _prepare_features(df: pd.DataFrame, n_lags: int = 10) -> Tuple[pd.DataFrame, List[str]]:
    """
    Full feature engineering pipeline:
      1. Compute technical indicators
      2. Create lag features
      3. Select feature columns
      4. Drop NaN rows

    Args:
        df:     Raw OHLCV DataFrame
        n_lags: Number of return lags

    Returns:
        Tuple of (processed DataFrame, list of feature column names)
    """
    # Step 1: Technical indicators
    enriched = compute_all(df)

    # Step 2: Lag features
    enriched = _create_lag_features(enriched, n_lags)

    # Step 3: Define feature columns (exclude target and non-features)
    exclude_cols = {"timestamp", "open", "high", "low", "close", "volume",
                    "log_return", "volume_change"}
    feature_cols = [
        col for col in enriched.columns
        if col not in exclude_cols and enriched[col].dtype in [np.float64, np.float32, np.int64]
    ]

    # Step 4: Drop rows with NaN (from lag/rolling calculations)
    enriched = enriched.dropna(subset=feature_cols).reset_index(drop=True)

    return enriched, feature_cols


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class StockPredictor:
    """
    Ridge Regression time-series forecaster.

    Predicts the next candle's log-return (which is converted to a price forecast).
    Uses L2 regularization to prevent overfitting on the small feature set.
    """

    def __init__(self, alpha: float = 1.0, n_lags: int = 10):
        """
        Args:
            alpha:  Ridge regularization strength
            n_lags: Number of lag features to create
        """
        self.alpha = alpha
        self.n_lags = n_lags
        self.model = Ridge(alpha=alpha)
        self.scaler = StandardScaler()
        self.feature_cols: List[str] = []
        self.is_fitted = False
        self._residual_std: float = 0.0  # For confidence intervals

    def fit(self, df: pd.DataFrame) -> Dict:
        """
        Train the model on OHLCV data.

        Uses a chronological split: 80% train, 20% validation.

        Args:
            df: OHLCV DataFrame

        Returns:
            Dict with training metrics
        """
        # Feature engineering
        enriched, self.feature_cols = _prepare_features(df, self.n_lags)

        if len(enriched) < 20:
            raise ValueError(f"Insufficient data for training: {len(enriched)} rows (need ≥20)")

        # Target: next-period log return
        enriched["target"] = enriched["log_return"].shift(-1)
        enriched = enriched.dropna(subset=["target"]).reset_index(drop=True)

        # Chronological split (no shuffle — respects time ordering)
        split_idx = int(len(enriched) * 0.8)
        train = enriched.iloc[:split_idx]
        val = enriched.iloc[split_idx:]

        # Extract features
        X_train = train[self.feature_cols].values
        y_train = train["target"].values
        X_val = val[self.feature_cols].values
        y_val = val["target"].values

        # Scale features (fit on train only)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)

        # Train
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        val_pred = self.model.predict(X_val_scaled)

        # Residual std for confidence intervals
        residuals = y_val - val_pred
        self._residual_std = float(np.std(residuals))

        metrics = {
            "train_mae": round(float(mean_absolute_error(y_train, train_pred)), 6),
            "val_mae": round(float(mean_absolute_error(y_val, val_pred)), 6),
            "train_rmse": round(float(np.sqrt(mean_squared_error(y_train, train_pred))), 6),
            "val_rmse": round(float(np.sqrt(mean_squared_error(y_val, val_pred))), 6),
            "n_train": len(train),
            "n_val": len(val),
            "n_features": len(self.feature_cols),
            "residual_std": round(self._residual_std, 6),
        }

        return metrics

    def predict(
        self,
        df: pd.DataFrame,
        n_steps: int = 5,
        confidence: float = 0.95,
    ) -> Dict:
        """
        Generate multi-step price forecasts with confidence intervals.

        Uses iterative single-step prediction: predict next return,
        update price, re-compute features, repeat.

        Args:
            df:         OHLCV DataFrame (most recent data)
            n_steps:    Number of future candles to forecast
            confidence: Confidence level for prediction intervals

        Returns:
            Dict with forecast data:
              - predictions: list of {price, upper, lower, return}
              - current_price: last known price
              - signal: BUY / SELL / HOLD
              - confidence_score: 0–1 model confidence
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        # Prepare features from input data
        enriched, _ = _prepare_features(df, self.n_lags)

        if len(enriched) == 0:
            raise ValueError("Not enough data to generate features for prediction")

        # Z-score for confidence interval
        from scipy import stats as sp_stats
        z_score = sp_stats.norm.ppf((1 + confidence) / 2)

        # Last known price
        current_price = float(df["close"].iloc[-1])
        price = current_price

        predictions = []

        for step in range(n_steps):
            # Get the latest row of features
            X = enriched[self.feature_cols].iloc[[-1]].values
            X_scaled = self.scaler.transform(X)

            # Predict log return
            pred_return = float(self.model.predict(X_scaled)[0])

            # Uncertainty grows with forecast horizon
            step_std = self._residual_std * np.sqrt(step + 1)

            # Price forecast
            price_pred = price * np.exp(pred_return)
            price_upper = price * np.exp(pred_return + z_score * step_std)
            price_lower = price * np.exp(pred_return - z_score * step_std)

            predictions.append({
                "step": step + 1,
                "predicted_price": round(price_pred, 2),
                "upper_bound": round(price_upper, 2),
                "lower_bound": round(price_lower, 2),
                "predicted_return": round(pred_return * 100, 4),  # As percentage
            })

            price = price_pred

        # Aggregate signal from predictions
        total_return = (predictions[-1]["predicted_price"] - current_price) / current_price
        avg_confidence = max(0, 1 - (self._residual_std * n_steps / 0.05))

        if total_return > 0.01:
            signal = "BUY"
        elif total_return < -0.01:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "current_price": current_price,
            "predictions": predictions,
            "signal": signal,
            "total_predicted_return": round(total_return * 100, 4),
            "confidence_score": round(float(np.clip(avg_confidence, 0, 1)), 4),
            "model_type": "ridge_regression",
            "n_features": len(self.feature_cols),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE: QUICK PREDICT (trains on the fly)
# ═══════════════════════════════════════════════════════════════════════════════

def quick_predict(
    df: pd.DataFrame,
    n_steps: int = 5,
    alpha: float = 1.0,
) -> Dict:
    """
    One-shot train + predict convenience function.

    Trains a fresh Ridge model on the provided OHLCV data and immediately
    generates a multi-step forecast. Suitable for API endpoints where the
    model doesn't need to persist across requests.

    Args:
        df:      OHLCV DataFrame
        n_steps: Forecast horizon
        alpha:   Ridge regularization strength

    Returns:
        Dict with predictions + training metrics
    """
    model = StockPredictor(alpha=alpha)

    try:
        train_metrics = model.fit(df)
        forecast = model.predict(df, n_steps=n_steps)
        forecast["train_metrics"] = train_metrics
        return forecast
    except (ValueError, RuntimeError) as e:
        # Graceful fallback — return a neutral signal
        current_price = float(df["close"].iloc[-1]) if len(df) > 0 else 0
        return {
            "current_price": current_price,
            "predictions": [],
            "signal": "HOLD",
            "total_predicted_return": 0.0,
            "confidence_score": 0.0,
            "model_type": "ridge_regression",
            "n_features": 0,
            "error": str(e),
        }
