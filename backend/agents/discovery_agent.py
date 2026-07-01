"""
discovery_agent.py — Market Screener & Discovery Agent
======================================================
Evaluates a curated list of top stocks to provide market-wide recommendations
when the user asks broad questions like "Which company should I invest in?".
"""

from typing import Dict, Any, List
from services.mock_data import generate_quote

# A curated basket of high-volume tech stocks for screening
CURATED_BASKET = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "META", "AMZN"]

def analyze_discovery() -> Dict[str, Any]:
    """
    Fetches real-time quotes and basic fundamentals for the curated basket.
    Returns a dictionary mapping tickers to their screening metrics.
    """
    discovery_data = {}
    
    for ticker in CURATED_BASKET:
        try:
            quote = generate_quote(ticker)
            discovery_data[ticker] = {
                "price": quote.get("price"),
                "change_percent": quote.get("change_percent"),
                "pe_ratio": quote.get("pe_ratio"),
                "eps": quote.get("eps"),
                "beta": quote.get("beta"),
                "market_cap": quote.get("market_cap")
            }
        except Exception as e:
            print(f"DiscoveryAgent: Error fetching {ticker}: {e}")
            discovery_data[ticker] = {"error": str(e)}
            
    return {
        "basket": CURATED_BASKET,
        "metrics": discovery_data,
        "agent_note": "Discovery agent has screened the curated basket of top tech stocks."
    }
