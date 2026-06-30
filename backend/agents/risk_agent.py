"""
risk_agent.py — Portfolio Risk Management Engine
==================================================
Evaluates portfolio state (e.g., VaR, position sizing, diversification).
Returns a risk analysis summary for the Executive Agent.
"""

from typing import Dict, Any, List

def analyze_risk(portfolio: Dict[str, Any], target_ticker: str = None) -> Dict[str, Any]:
    """
    Analyze portfolio risk and position sizing.
    
    Args:
        portfolio: The current portfolio state from the frontend context
        target_ticker: Optional ticker the user is asking about
        
    Returns:
        Dict with risk metrics and summary
    """
    try:
        holdings: List[Dict] = portfolio.get("holdings", [])
        total_value = portfolio.get("total_value", 0.0)
        
        if total_value == 0 or not holdings:
            return {
                "agent": "risk",
                "summary": "Portfolio is currently empty. No risk analysis available."
            }
            
        # 1. Diversification Check
        weights = {h["ticker"]: h["value"] / total_value for h in holdings}
        max_weight_ticker = max(weights, key=weights.get)
        max_weight = weights[max_weight_ticker]
        
        concentration_warning = max_weight > 0.25
        
        # 2. Target Ticker specific risk
        target_analysis = ""
        if target_ticker:
            target_ticker = target_ticker.upper()
            target_weight = weights.get(target_ticker, 0.0)
            if target_weight > 0:
                target_analysis = f"You currently have a {target_weight*100:.1f}% exposure to {target_ticker}. "
                if target_weight > 0.2:
                    target_analysis += f"Adding more would severely concentrate your risk in {target_ticker}."
                else:
                    target_analysis += "There is room to add to this position while maintaining diversification."
            else:
                target_analysis = f"You have no current exposure to {target_ticker}. Adding it would increase diversification."
                
        # 3. VaR (Mock Value at Risk 95%)
        # In a real app, this would use covariance matrices of the holdings.
        mock_var_95 = total_value * 0.025 # assume 2.5% daily VaR
        
        summary = f"Portfolio VaR (95%) is estimated at ${mock_var_95:,.2f}. "
        if concentration_warning:
            summary += f"Warning: High concentration in {max_weight_ticker} ({max_weight*100:.1f}%). "
        
        summary += target_analysis
        
        return {
            "agent": "risk",
            "total_value": total_value,
            "var_95": mock_var_95,
            "max_concentration": {
                "ticker": max_weight_ticker,
                "weight": max_weight
            },
            "summary": summary
        }
    except Exception as e:
        return {
            "agent": "risk",
            "error": str(e),
            "summary": f"Failed to run risk analysis: {str(e)}"
        }
