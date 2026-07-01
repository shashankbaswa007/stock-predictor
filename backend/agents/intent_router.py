"""
intent_router.py — User Intent Routing
========================================
Analyzes the user's chat prompt and current UI context to determine
which specialized sub-agent (Quant, Fundamental, Risk) should handle the request.

In production, this would be an LLM-based router (e.g., using LangChain's MultiPromptChain).
For this mock-first implementation, we use a robust keyword-based heuristic.
"""

from typing import Dict, Any
import re

def extract_ticker(prompt: str, current_ticker: str) -> str:
    """
    Extracts a stock ticker from the user's prompt. 
    If a valid stock ticker is found (e.g., AAPL, TSLA), returns it.
    Otherwise, returns the current_ticker.
    """
    # Look for patterns like 1-5 uppercase letters that could be a ticker
    # This is a naive heuristic. In a full production system, we'd use an LLM or an NER model.
    # For common requests like "Analyze JPM", "What about MSFT?", this works well.
    words = re.findall(r'\b[A-Z]{1,5}\b', prompt)
    
    # Filter out common uppercase words that aren't tickers
    stop_words = {"A", "I", "WHAT", "HOW", "WHY", "IS", "THE", "ARE", "AM", "BUY", "SELL", "HOLD", "SEC"}
    
    for word in words:
        if word not in stop_words:
            return word
            
    return current_ticker

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
    discovery_keywords = ["which company", "which companies", "what stocks", "recommend", "best stock", "screener", "which stock", "top stock", "what company", "what companies", "top companies", "best companies", "top 5", "top 10", "what to invest", "good stock", "good stocks"]
    
    # 3. Score the prompt
    quant_score = sum(1 for k in quant_keywords if k in prompt_lower)
    fundamental_score = sum(1 for k in fundamental_keywords if k in prompt_lower)
    risk_score = sum(1 for k in risk_keywords if k in prompt_lower)
    discovery_score = sum(1 for k in discovery_keywords if k in prompt_lower)
    
    # 4. Route based on highest score, breaking ties with the UI view_mode
    max_score = max(quant_score, fundamental_score, risk_score, discovery_score)
    
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
            
    if discovery_score == max_score:
        return "discovery"
    if risk_score == max_score:
        return "risk"
    if fundamental_score == max_score:
        return "fundamental"
    if quant_score == max_score:
        return "quant"
        
    return "general"
