"""
fundamental_agent.py — Long-Term Fundamental Analysis Engine
==============================================================
Wraps the RAG pipeline to query the FAISS vector store.
Returns qualitative sentiment and fundamental summaries for the Executive Agent.
"""

from typing import Dict, Any, List
from services.vector_store import retrieve_context

def analyze_fundamentals(query: str, ticker: str) -> Dict[str, Any]:
    """
    Run fundamental analysis using RAG on 10-K and News data.
    
    Args:
        query: The user's chat prompt
        ticker: The stock ticker
        
    Returns:
        Dict with retrieved contexts and a fundamental summary.
    """
    try:
        # 1. Retrieve top 5 most relevant chunks from FAISS
        contexts = retrieve_context(query, ticker, k=5)
        
        if not contexts:
            return {
                "agent": "fundamental",
                "ticker": ticker,
                "summary": f"No fundamental data found for {ticker}."
            }
            
        # 2. Extract news sentiment if available
        news_contexts = [c for c in contexts if c["metadata"].get("doc_type") == "news"]
        sentiment_score = 0.0
        if news_contexts:
            sentiment_score = sum(c["metadata"].get("sentiment", 0.0) for c in news_contexts) / len(news_contexts)
            
        sentiment_label = "NEUTRAL"
        if sentiment_score > 0.2:
            sentiment_label = "BULLISH"
        elif sentiment_score < -0.2:
            sentiment_label = "BEARISH"
            
        # 3. Build a mock synthesized summary (in production, an LLM would read the contexts here)
        financial_highlights = [c["content"] for c in contexts if c["metadata"].get("section") == "financial_highlights"]
        
        summary = f"Based on SEC 10-K filings and recent news, the fundamental outlook for {ticker} is {sentiment_label}."
        if financial_highlights:
            summary += f" Key highlight: {financial_highlights[0][:100]}..."
            
        return {
            "agent": "fundamental",
            "ticker": ticker,
            "retrieved_contexts": contexts,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "summary": summary
        }
    except Exception as e:
        return {
            "agent": "fundamental",
            "ticker": ticker,
            "error": str(e),
            "summary": f"Failed to run fundamental analysis: {str(e)}"
        }
