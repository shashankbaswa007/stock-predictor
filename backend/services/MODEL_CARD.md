# Model Card: AI Trading Co-Pilot Short-Term Forecaster

## Model Details
- **Architecture**: Ridge Regression (L2 Regularized Linear Model)
- **Framework**: `scikit-learn`
- **Training Paradigm**: Online / On-the-fly (Model is trained chronologically on the most recent 1 year of daily data per inference request).
- **Purpose**: Provide a fast, robust baseline for short-term (5-day) price movement forecasting.

## Intended Use
- **Primary Use Case**: Generating directional signals (BUY/SELL/HOLD) based on predicted price returns.
- **Out-of-Scope**: High-frequency trading (HFT), long-term fundamental valuation, options pricing.

## Feature Engineering
The model uses 25+ engineered features to capture momentum, volatility, and mean reversion:
1. **Lagged Returns**: Log returns from `t-1` to `t-10`.
2. **Rolling Statistics**: 5-day and 10-day rolling mean and standard deviation of returns.
3. **Candlestick Morphology**: Intra-candle volatility (`range_pct`), body size (`body_pct`), and wick ratios (`upper_wick_pct`, `lower_wick_pct`).
4. **Technical Indicators**: RSI (14), MACD (12, 26, 9), Bollinger Bands (20, 2σ), and SMAs (10, 20, 50).

## Evaluation Data & Metrics
- **Split Strategy**: 80/20 chronological split (no shuffling) to strictly prevent lookahead bias.
- **Metrics Tracked**: 
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - Residual Standard Deviation (used for generating Confidence Intervals)

## Rationale: Why Ridge Regression?
When pitching this architecture in an interview setting, the choice of Ridge Regression over complex Neural Networks (like LSTMs or Transformers) is highly deliberate:
1. **Data Scarcity**: Time-series forecasting on daily candle data for a single asset often lacks the volume required to train deep learning models without severe overfitting.
2. **Interpretability & Robustness**: Linear models are less prone to hallucinating extreme non-linear price spikes based on noise.
3. **Latency**: The model trains and infers in under 100ms, making it ideal for a real-time web application.
4. **Regularization**: The L2 penalty shrinks the coefficients of highly correlated technical indicators (e.g., SMA-10 and SMA-20), naturally handling multicollinearity.

## Future Roadmap
To upgrade the prediction engine in future iterations:
- **XGBoost / LightGBM**: Introduce non-linear tree-based ensembles to capture interaction effects between technical indicators.
- **Temporal Fusion Transformers (TFT)**: For multi-horizon forecasting if the dataset is expanded to include macroeconomic covariates (interest rates, CPI) across multiple assets simultaneously.
