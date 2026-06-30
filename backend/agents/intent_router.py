"""
intent_router.py — User Intent Routing
========================================
Analyzes the user's chat prompt and current UI context to determine
which specialized sub-agent (Quant, Fundamental, Risk) should handle the request.

In production, this would be an LLM-based router (e.g., using LangChain's MultiPromptChain).
For this mock-first implementation, we use a robust keyword-based heuristic.
"""

from typing import Dict, Any


def route_intent(prompt: str, context: Dict[str, Any]) -> str:
    """
    Determine the target sub-agent based on the prompt and context.
    
    Returns one of: 'quant', 'fundamental', 'risk', or 'general'
    """
    prompt_lower = prompt.lower()
    
    # 1. Check for explicit view mode from the frontend
    view_mode = context.get("view_mode", "")
    
    # 2. Define keyword clusters
    quant_keywords = ["short", "trade", "technical", "rsi", "macd", "chart", "price", "predict", "forecast", "momentum", "trend", "moving average"]
    fundamental_keywords = ["long", "invest", "value", "10-k", "sec", "earnings", "revenue", "growth", "outlook", "fundamental", "news"]
    risk_keywords = ["risk", "portfolio", "var", "exposure", "hedging", "diversification", "drawdown", "loss"]
    
    # 3. Score the prompt
    quant_score = sum(1 for k in quant_keywords if k in prompt_lower)
    fundamental_score = sum(1 for k in fundamental_keywords if k in prompt_lower)
    risk_score = sum(1 for k in risk_keywords if k in prompt_lower)
    
    # 4. Route based on highest score, breaking ties with the UI view_mode
    max_score = max(quant_score, fundamental_score, risk_score)
    
    if max_score == 0:
        # Fallback to UI context
        if view_mode == "short_term":
            return "quant"
        elif view_mode == "long_term":
            return "fundamental"
        elif view_mode == "portfolio":
            return "risk"
        else:
            return "general"
            
    if risk_score == max_score:
        return "risk"
    if fundamental_score == max_score:
        return "fundamental"
    if quant_score == max_score:
        return "quant"
        
    return "general"
