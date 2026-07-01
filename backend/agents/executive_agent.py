"""
executive_agent.py — Master Synthesizer Engine (Phase 5: Real API)
==================================================================
Takes the outputs of the sub-agents (Quant, Fundamental, Risk),
applies a master system prompt, and returns a strict JSON response
containing the human message, explainability data points, and UI actions
using a real LLM.
"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from agents.llm_factory import get_llm

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutiveResponse(BaseModel):
    message: str = Field(description="The human-readable markdown response addressing the user's prompt.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    signal: str = Field(description="One of: 'BUY', 'SELL', or 'HOLD'")
    reasoning: List[str] = Field(description="List of 2-3 short bullet points explaining the decision.")
    citations: List[str] = Field(default=[], description="List of 1-3 short citation source names (e.g., 'SEC 10-Q', 'Reuters').")
    ui_action_type: str = Field(description="One of: 'switch_view', 'change_ticker', or 'none'")
    ui_action_mode: str = Field(description="One of: 'short_term', 'long_term', 'portfolio'")
    ui_action_ticker: str = Field(description="The active ticker symbol to display")

# ═══════════════════════════════════════════════════════════════════════════════
# MASTER SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

EXECUTIVE_SYSTEM_PROMPT = """
You are an elite quantitative trading Executive AI Co-Pilot.
You will be provided with a user's query and analysis from sub-engines:
1. Quant Engine (ML price forecasts, technical indicators)
2. Fundamental Engine (RAG over SEC filings and news)
3. Risk Engine (Portfolio VaR, concentration limits)
4. Discovery Engine (Market screening across a basket of top stocks)

The primary intent of the user was routed as: {intent}
Target Ticker: {ticker}

Your job is to synthesize this data into a clear, actionable summary for the user.

CRITICAL UI ACTION INSTRUCTIONS:
- If the intent is 'quant' or the user asks for charts/prices/short-term, set ui_action_type="switch_view" and ui_action_mode="short_term".
- If the intent is 'fundamental' or the user asks for news/10-K/long-term, set ui_action_type="switch_view" and ui_action_mode="long_term".
- If the intent is 'risk' or the user asks about their holdings/portfolio, set ui_action_type="switch_view" and ui_action_mode="portfolio".
- If the intent is 'discovery', provide a comparative summary. Set ui_action_mode="long_term" (or whatever the best fit is) and set ui_action_ticker to your top recommended stock from the basket.
- ALWAYS ensure ui_action_ticker matches the target ticker (or the recommended ticker if discovery).

EXPLAINABLE AI INSTRUCTIONS:
- Extract 1-3 source names from the retrieved_contexts in Fundamental Data and list them in 'citations' (e.g. 'SEC 10-Q', 'Reuters').

Sub-Engine Data:
---
Quant Data:
{quant_data}
---
Fundamental Data:
{fundamental_data}
---
Risk Data:
{risk_data}
---
Discovery Data:
{discovery_data}
---
"""

def synthesize_response(
    query: str, 
    intent: str, 
    ticker: str, 
    quant_data: Dict, 
    fundamental_data: Dict, 
    risk_data: Dict,
    discovery_data: Dict = None,
    use_mock_llm: bool = False
) -> Dict[str, Any]:
    """
    Synthesizes the final AI response using a real LLM.
    """
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ExecutiveResponse)
        
        prompt = EXECUTIVE_SYSTEM_PROMPT.format(
            intent=intent,
            ticker=ticker,
            quant_data=json.dumps(quant_data, indent=2),
            fundamental_data=json.dumps(fundamental_data, indent=2),
            risk_data=json.dumps(risk_data, indent=2),
            discovery_data=json.dumps(discovery_data or {}, indent=2)
        )
        
        prompt += f"\n\nUser Query: {query}\nProvide your synthesis."
        
        # Invoke the LLM
        response: ExecutiveResponse = structured_llm.invoke(prompt)
        
        # Convert back to dict for the API layer to return as JSON
        # Include agent_source for the UI
        result = response.dict()
        result["ui_action"] = {
            "action": result.pop("ui_action_type"),
            "payload": {
                "mode": result.pop("ui_action_mode"),
                "ticker": result.pop("ui_action_ticker")
            }
        }
        result["agent_source"] = intent
        
        return result
        
    except Exception as e:
        print(f"Error in executive_agent: {e}")
        # Fallback response in case the LLM fails
        return {
            "message": f"I encountered an error processing that request with the AI: {str(e)}",
            "confidence": 0.0,
            "signal": "HOLD",
            "reasoning": ["Error connecting to LLM provider"],
            "ui_action": None,
            "agent_source": intent
        }
