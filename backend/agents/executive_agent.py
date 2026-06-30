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

class UIActionPayload(BaseModel):
    mode: str = Field(description="One of: 'short_term', 'long_term', 'portfolio'")
    ticker: str = Field(description="The active ticker symbol to display")

class UIAction(BaseModel):
    action: str = Field(description="One of: 'switch_view', 'change_ticker', or 'none'")
    payload: UIActionPayload

class ExecutiveResponse(BaseModel):
    message: str = Field(description="The human-readable markdown response addressing the user's prompt.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    signal: str = Field(description="One of: 'BUY', 'SELL', or 'HOLD'")
    reasoning: List[str] = Field(description="List of 2-3 short bullet points explaining the decision for Explainable AI (XAI) UI badges.")
    ui_action: Optional[UIAction] = Field(None, description="The UI action to perform to update the dashboard view based on the user's intent.")

# ═══════════════════════════════════════════════════════════════════════════════
# MASTER SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

EXECUTIVE_SYSTEM_PROMPT = """
You are an elite quantitative trading Executive AI Co-Pilot.
You will be provided with a user's query and analysis from three sub-engines:
1. Quant Engine (ML price forecasts, technical indicators)
2. Fundamental Engine (RAG over SEC filings and news)
3. Risk Engine (Portfolio VaR, concentration limits)

The primary intent of the user was routed as: {intent}
Target Ticker: {ticker}

Your job is to synthesize this data into a clear, actionable summary for the user.

CRITICAL UI ACTION INSTRUCTIONS:
- If the intent is 'quant' or the user asks for charts/prices/short-term, set ui_action.action="switch_view" and mode="short_term".
- If the intent is 'fundamental' or the user asks for news/10-K/long-term, set ui_action.action="switch_view" and mode="long_term".
- If the intent is 'risk' or the user asks about their holdings/portfolio, set ui_action.action="switch_view" and mode="portfolio".
- ALWAYS ensure ui_action.payload.ticker matches the target ticker.

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
"""

def synthesize_response(
    query: str, 
    intent: str, 
    ticker: str, 
    quant_data: Dict, 
    fundamental_data: Dict, 
    risk_data: Dict,
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
            risk_data=json.dumps(risk_data, indent=2)
        )
        
        prompt += f"\n\nUser Query: {query}\nProvide your synthesis."
        
        # Invoke the LLM
        response: ExecutiveResponse = structured_llm.invoke(prompt)
        
        # Convert back to dict for the API layer to return as JSON
        # Include agent_source for the UI
        result = response.dict()
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
