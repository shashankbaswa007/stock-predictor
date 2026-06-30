"""
fundamental_agent.py — Long-Term Fundamental Analysis Engine
==============================================================
Wraps the RAG pipeline to query the FAISS vector store.
Uses a real LLM to analyze the DuckDuckGo news and generic 10-K data.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from services.vector_store import retrieve_context
from agents.llm_factory import get_llm

class FundamentalAnalysis(BaseModel):
    sentiment_score: float = Field(description="A score between -1.0 (very bearish) and 1.0 (very bullish)")
    sentiment_label: str = Field(description="One of: BULLISH, BEARISH, or NEUTRAL")
    summary: str = Field(description="A 2-3 sentence fundamental summary of the company based on the provided context")

def analyze_fundamentals(query: str, ticker: str) -> Dict[str, Any]:
    """
    Run fundamental analysis using RAG on 10-K and News data with a real LLM.
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
            
        # 2. Extract text for LLM prompt
        context_text = "\n\n".join([f"[{c['metadata'].get('source', 'Unknown')}] {c['content']}" for c in contexts])
        
        # 3. Use LLM to analyze the text
        llm = get_llm()
        structured_llm = llm.with_structured_output(FundamentalAnalysis)
        
        prompt = f"""
        You are a fundamental financial analyst.
        Analyze the following recent news and filing excerpts for {ticker}:
        
        {context_text}
        
        Determine the overall sentiment and provide a concise summary.
        """
        
        analysis = structured_llm.invoke(prompt)
        
        return {
            "agent": "fundamental",
            "ticker": ticker,
            "retrieved_contexts": contexts,
            "sentiment_score": analysis.sentiment_score,
            "sentiment_label": analysis.sentiment_label,
            "summary": analysis.summary
        }
    except Exception as e:
        return {
            "agent": "fundamental",
            "ticker": ticker,
            "error": str(e),
            "summary": f"Failed to run fundamental analysis: {str(e)}"
        }
