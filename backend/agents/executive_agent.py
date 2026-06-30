"""
executive_agent.py — Master Synthesizer Engine
================================================
Takes the outputs of the sub-agents (Quant, Fundamental, Risk),
applies a master system prompt, and returns a strict JSON response
containing the human message, explainability data points, and UI actions.

In production, this wraps a strong LLM (e.g., GPT-4o).
In mock-mode, it uses deterministic logic to generate the JSON response.
"""

import json
from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# MASTER SYSTEM PROMPT (For Real LLM Integration)
# ═══════════════════════════════════════════════════════════════════════════════

EXECUTIVE_SYSTEM_PROMPT = """
You are an elite quantitative trading Executive AI Co-Pilot.
You will be provided with analysis from three sub-engines:
1. Quant Engine (ML price forecasts, technical indicators)
2. Fundamental Engine (RAG over SEC filings and news)
3. Risk Engine (Portfolio VaR, concentration limits)

Your job is to synthesize this data into a clear, actionable summary for the user.

CRITICAL INSTRUCTION: You MUST return your response as a raw JSON object with the following schema:
{
  "message": "The human-readable markdown response",
  "confidence": 0.85,  // float between 0 and 1
  "signal": "BUY" | "SELL" | "HOLD",
  "reasoning": [
    "List of 2-3 short bullet points explaining the decision for XAI"
  ],
  "ui_action": {
    "action": "switch_view" | "change_ticker" | "none",
    "payload": {
       "mode": "short_term" | "long_term" | "portfolio",
       "ticker": "AAPL"
    }
  } // Can be null if no action needed
}
"""

def synthesize_response(
    query: str, 
    intent: str, 
    ticker: str, 
    quant_data: Dict, 
    fundamental_data: Dict, 
    risk_data: Dict,
    use_mock_llm: bool = True
) -> Dict[str, Any]:
    """
    Synthesizes the final AI response.
    """
    if not use_mock_llm:
        # In the future, pass EXECUTIVE_SYSTEM_PROMPT and the sub-agent JSONs to an LLM here
        raise NotImplementedError("Real LLM execution is not yet implemented. Use use_mock_llm=True.")
        
    # ── MOCK EXECUTIVE LOGIC ──────────────────────────────────────────────────
    
    # Base response structure
    response = {
        "confidence": 0.0,
        "signal": "HOLD",
        "reasoning": [],
        "ui_action": None,
        "agent_source": intent
    }
    
    # 1. Determine UI Action based on intent
    if intent == "quant":
        response["ui_action"] = {"action": "switch_view", "payload": {"mode": "short_term"}}
    elif intent == "fundamental":
        response["ui_action"] = {"action": "switch_view", "payload": {"mode": "long_term"}}
    elif intent == "risk":
        response["ui_action"] = {"action": "switch_view", "payload": {"mode": "portfolio"}}
        
    # 2. Synthesize based on the primary intent
    if intent == "quant":
        ml = quant_data.get("ml_forecast", {})
        ml_return = ml.get("total_predicted_return", 0.0)
        signal = ml.get("signal", "HOLD")
        
        response["signal"] = signal
        response["confidence"] = ml.get("confidence_score", 0.75)
        response["reasoning"] = [
            f"ML Ridge Regression forecasts a {ml_return}% return over 5 days.",
            f"Technical Confluence: {quant_data.get('confluence_strength', 'MIXED')}",
            f"Current RSI: {quant_data.get('indicators', {}).get('rsi', 50):.1f}"
        ]
        
        icon = "📈" if signal == "BUY" else "📉" if signal == "SELL" else "📊"
        response["message"] = (
            f"**{icon} Quant Analysis for {ticker.upper()}**\n\n"
            f"Our ML models predict a **{signal}** signal with an expected move of **{ml_return}%** "
            f"over the next 5 periods. Technical indicators show {quant_data.get('technical_signal', 'HOLD').lower()} momentum. "
            f"I have switched your dashboard to the **Short-Term View** to visualize this."
        )
        
    elif intent == "fundamental":
        sentiment = fundamental_data.get("sentiment_label", "NEUTRAL")
        score = fundamental_data.get("sentiment_score", 0.0)
        
        response["signal"] = "BUY" if sentiment == "BULLISH" else "SELL" if sentiment == "BEARISH" else "HOLD"
        response["confidence"] = min(0.9, 0.5 + abs(score))
        response["reasoning"] = [
            f"Sentiment Analysis: {sentiment} ({score:.2f})",
            "RAG retrieved context from most recent 10-K filings.",
            "Recent news headlines align with fundamental thesis."
        ]
        
        response["message"] = (
            f"**🏢 Fundamental Analysis for {ticker.upper()}**\n\n"
            f"Based on my RAG pipeline over recent SEC filings and news, the outlook is **{sentiment}**. "
            f"{fundamental_data.get('summary', '')} "
            f"I have opened the **Long-Term View** for deeper fundamental metrics."
        )
        
    elif intent == "risk":
        var = risk_data.get("var_95", 0.0)
        conc = risk_data.get("max_concentration", {})
        
        response["signal"] = "HOLD"
        response["confidence"] = 0.90
        response["reasoning"] = [
            f"Portfolio VaR (95%): ${var:,.2f}",
            f"Max concentration: {conc.get('ticker')} at {conc.get('weight', 0)*100:.1f}%",
            f"Target {ticker} correlation check complete."
        ]
        
        response["message"] = (
            f"**🛡️ Risk Analysis & Sizing**\n\n"
            f"{risk_data.get('summary', '')} "
            f"I have switched your view to the **Portfolio Manager** so you can review your current exposures."
        )
        
    else: # general
        response["message"] = (
            f"I am your AI Trading Co-Pilot. I can analyze {ticker.upper()} using quantitative "
            f"models, fundamental RAG pipelines, or portfolio risk metrics. Try asking me:\n\n"
            f"* 'What's the short-term forecast for {ticker.upper()}?'\n"
            f"* 'Show me the fundamental outlook for {ticker.upper()}'\n"
            f"* 'How would buying {ticker.upper()} affect my portfolio risk?'"
        )
        
    return response
