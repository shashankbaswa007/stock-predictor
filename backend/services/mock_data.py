"""
mock_data.py — Real Market Data via yfinance
==============================================
Replaces the Phase 1-4 mock generators with real data using yfinance.
Maintains the same function signatures so the rest of the application
(like technical_indicators.py and the ML models) continues to work perfectly.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from langchain_community.tools import DuckDuckGoSearchRun
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════════════════════
# OHLCV GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=128)
def generate_ohlcv(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch real OHLCV candlestick data from Yahoo Finance.

    Args:
        ticker:   Stock ticker symbol
        period:   Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
        interval: Candle interval (1m, 5m, 15m, 1h, 1d, 1wk)

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    try:
        # yfinance uses lowercase interval strings like "1d", "1wk"
        # but period strings match exactly what we passed in Phase 1-4
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
            
        # Reset index to make Date/Datetime a column
        df.reset_index(inplace=True)
        
        # Determine the datetime column name (can be 'Date' or 'Datetime' depending on interval)
        date_col = "Datetime" if "Datetime" in df.columns else "Date"
        
        # Rename columns to match what our technical_indicators expect
        df.rename(columns={
            date_col: "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)
        
        # Drop any rows with NaN values which break JSON serialization
        df.dropna(subset=["open", "high", "low", "close"], inplace=True)
        
        # Format timestamp to ISO string
        df["timestamp"] = df["timestamp"].apply(lambda x: x.isoformat())
        
        # Return only the columns we care about
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
        
    except Exception as e:
        print(f"Error fetching OHLCV for {ticker}: {e}")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_quote(ticker: str) -> Dict:
    """
    Fetch a real snapshot quote from Yahoo Finance.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
        prev_close = info.get("previousClose", price)
        change = price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0.0
        
        return {
            "ticker": ticker.upper(),
            "price": round(price, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "prev_close": round(prev_close, 2),
            "open": round(info.get("open", prev_close), 2),
            "day_high": round(info.get("dayHigh", price), 2),
            "day_low": round(info.get("dayLow", price), 2),
            "week_52_high": round(info.get("fiftyTwoWeekHigh", price), 2),
            "week_52_low": round(info.get("fiftyTwoWeekLow", price), 2),
            "volume": info.get("volume", 0),
            "avg_volume": info.get("averageVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": round(info.get("trailingPE", 0), 2),
            "eps": round(info.get("trailingEps", 0), 2),
            "dividend_yield": round(info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0, 2),
            "beta": round(info.get("beta", 1.0), 2),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error fetching quote for {ticker}: {e}")
        # Return empty safe defaults if yf fails
        return {
            "ticker": ticker.upper(), "price": 0.0, "change": 0.0, "change_percent": 0.0,
            "prev_close": 0.0, "open": 0.0, "day_high": 0.0, "day_low": 0.0,
            "week_52_high": 0.0, "week_52_low": 0.0, "volume": 0, "avg_volume": 0,
            "market_cap": 0, "pe_ratio": 0.0, "eps": 0.0, "dividend_yield": 0.0,
            "beta": 1.0, "timestamp": datetime.now().isoformat(),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# NEWS HEADLINE GENERATOR (Using DuckDuckGo)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_news(ticker: str, count: int = 5) -> List[Dict]:
    """
    Scrape real news headlines using DuckDuckGo search.
    """
    try:
        search = DuckDuckGoSearchRun()
        query = f"{ticker} stock news financial"
        # DuckDuckGo returns a block of text, we'll try to parse it into distinct items
        result = search.run(query)
        
        # Quick hacky split since DDG returns concatenated snippets
        snippets = result.split("...")
        articles = []
        for i, s in enumerate(snippets[:count]):
            text = s.strip()
            if text:
                articles.append({
                    "headline": text[:150] + ("" if len(text) <= 150 else "..."),
                    "source": "Web Search",
                    "sentiment": 0.0, # We'll let the LLM judge sentiment instead of hardcoding
                    "published_at": datetime.now().isoformat(),
                    "url": f"https://finance.yahoo.com/quote/{ticker}/news",
                })
        
        return articles if articles else [{"headline": f"No recent news found for {ticker}.", "source": "System", "sentiment": 0.0, "published_at": datetime.now().isoformat(), "url": ""}]
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []

# ═══════════════════════════════════════════════════════════════════════════════
# 10-K / SEC FILING EXCERPT GENERATOR (Kept for fallback RAG pipeline)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_10k_excerpts(ticker: str) -> List[Dict]:
    """
    Provide generic company descriptions to populate the vector DB if needed.
    """
    try:
        info = yf.Ticker(ticker).info
        summary = info.get("longBusinessSummary", f"{ticker} is a publicly traded company.")
        return [{
            "section": "business_overview",
            "content": summary,
            "ticker": ticker.upper(),
            "filing_date": datetime.now().strftime("%Y-02-15"),
            "fiscal_year": datetime.now().year - 1,
            "doc_type": "10-K",
        }]
    except:
        return []
