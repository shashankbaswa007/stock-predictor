"""
routes_chat.py — AI Co-Pilot Chat API (Phase 3: Multi-Agent Pipeline)
========================================================================
Receives user prompts, routes them via the Intent Router,
fetches data from the necessary sub-agents (Quant, Fundamental, Risk),
and synthesizes the final JSON response via the Executive Agent.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.intent_router import route_intent
from agents.quant_agent import analyze_quant
from agents.fundamental_agent import analyze_fundamentals
from agents.risk_agent import analyze_risk
from agents.executive_agent import synthesize_response

router = APIRouter()

class UIContext(BaseModel):
    view_mode: str
    portfolio_state: Dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    ticker: str
    ui_context: UIContext
    use_mock_llm: bool = True

class UIAction(BaseModel):
    action: str
    payload: Dict[str, Any]

class ChatResponse(BaseModel):
    message: str
    confidence: float
    signal: str
    reasoning: List[str]
    ui_action: Optional[UIAction] = None
    agent_source: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main entry point for the Dual-Engine AI Co-Pilot.
    Executes the multi-agent orchestration pipeline.
    """
    try:
        # 1. Intent Routing
        # Determine if the user wants quant, fundamental, or risk analysis
        context_dict = {
            "view_mode": request.ui_context.view_mode,
            "portfolio": request.ui_context.portfolio_state
        }
        intent = route_intent(request.message, context_dict)
        
        # 2. Sub-Agent Execution
        # In a real distributed system, these could run in parallel.
        quant_data = {}
        fundamental_data = {}
        risk_data = {}
        
        if intent == "quant":
            quant_data = analyze_quant(request.ticker)
        elif intent == "fundamental":
            fundamental_data = analyze_fundamentals(request.message, request.ticker)
        elif intent == "risk":
            risk_data = analyze_risk(request.ui_context.portfolio_state, request.ticker)
        else:
            # For general chat, maybe we pull a tiny bit of quant data just to have context
            quant_data = analyze_quant(request.ticker)
            
        # 3. Executive Synthesis
        # Pass all context to the master agent to formulate the final JSON response + UI Actions
        final_response = synthesize_response(
            query=request.message,
            intent=intent,
            ticker=request.ticker,
            quant_data=quant_data,
            fundamental_data=fundamental_data,
            risk_data=risk_data,
            use_mock_llm=request.use_mock_llm
        )
        
        return final_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Pipeline Error: {str(e)}")
