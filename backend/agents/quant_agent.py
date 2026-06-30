"""
quant_agent.py — Short-Term Quantitative Analysis Engine
==========================================================
Wraps the ML model and technical indicators from Phase 2.
Returns a quantitative analysis summary for the Executive Agent.
"""

from typing import Dict, Any
from services.mock_data import generate_ohlcv
from services.ml_model import quick_predict
from services.technical_indicators import compute_all

def analyze_quant(ticker: str) -> Dict[str, Any]:
    """
    Run full quantitative analysis on a ticker.
    
    Returns:
        Dict with ML predictions, signals, and technical data.
    """
    try:
        # 1. Fetch 1 year of daily data for the model
        df = generate_ohlcv(ticker, period="1y", interval="1d")
        
        # 2. Run the ML forecast (5 days ahead)
        forecast = quick_predict(df, n_steps=5)
        
        # 3. Get latest technical indicators
        df_enriched = compute_all(df)
        latest = df_enriched.iloc[-1]
        
        indicators = {
            "rsi": float(latest["rsi"]) if not type(latest["rsi"]) == str else 50.0,
            "macd": float(latest["macd"]),
            "macd_signal": float(latest["macd_signal"]),
            "bb_percent_b": float(latest["bb_percent_b"])
        }
        
        # 4. Determine trend agreement
        ml_signal = forecast.get("signal", "HOLD")
        rsi_val = indicators["rsi"]
        
        tech_signal = "HOLD"
        if rsi_val < 30 and indicators["macd"] > indicators["macd_signal"]:
            tech_signal = "BUY"
        elif rsi_val > 70 and indicators["macd"] < indicators["macd_signal"]:
            tech_signal = "SELL"
            
        confluence = "STRONG" if ml_signal == tech_signal and ml_signal != "HOLD" else "MIXED"
        
        return {
            "agent": "quant",
            "ticker": ticker,
            "ml_forecast": forecast,
            "indicators": indicators,
            "technical_signal": tech_signal,
            "confluence_strength": confluence,
            "summary": f"ML model predicts {ml_signal} with a {forecast.get('total_predicted_return', 0)}% return over 5 days. Technicals indicate {tech_signal} (RSI: {rsi_val:.1f}). Confluence is {confluence}."
        }
    except Exception as e:
        return {
            "agent": "quant",
            "ticker": ticker,
            "error": str(e),
            "summary": f"Failed to run quantitative analysis: {str(e)}"
        }
