"""
mock_data.py — Premium Market Data Integration (Phase 7)
==========================================================
Replaces yfinance with Premium APIs (Polygon & Finnhub).
Graceful degradation to yfinance if rate limits are hit.
"""

import os
import time
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import settings

# ── TTL Cache (5 minutes) for real-time data freshness ────────────────────────
_ohlcv_cache: Dict[Tuple, Tuple[float, pd.DataFrame]] = {}
_OHLCV_TTL = 300  # 5 minutes

# ═══════════════════════════════════════════════════════════════════════════════
# OHLCV GENERATOR (Polygon -> yfinance)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_polygon_dates(period: str) -> tuple[str, str]:
    """Helper to convert relative periods to YYYY-MM-DD for Polygon."""
    end = datetime.now()
    if period == "1d":
        start = end - timedelta(days=1)
    elif period == "5d":
        start = end - timedelta(days=5)
    elif period == "1mo":
        start = end - timedelta(days=30)
    elif period == "3mo":
        start = end - timedelta(days=90)
    elif period == "6mo":
        start = end - timedelta(days=180)
    elif period == "1y":
        start = end - timedelta(days=365)
    elif period == "2y":
        start = end - timedelta(days=730)
    elif period == "5y":
        start = end - timedelta(days=1825)
    else:
        start = end - timedelta(days=180)
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def generate_ohlcv(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch real OHLCV data primarily from Polygon (fallback to yfinance)."""
    # Check TTL cache
    cache_key = (ticker.upper(), period, interval)
    if cache_key in _ohlcv_cache:
        cached_time, cached_df = _ohlcv_cache[cache_key]
        if time.time() - cached_time < _OHLCV_TTL:
            return cached_df
    if settings.polygon_api_key:
        try:
            # 1. Try Polygon Aggregates API
            multiplier = 1
            timespan = "day" if "d" in interval else "minute"
            if interval == "1wk":
                timespan = "week"
            elif interval == "1mo":
                timespan = "month"
            elif interval == "5m":
                multiplier = 5
                timespan = "minute"
                
            start_date, end_date = _get_polygon_dates(period)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/range/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={settings.polygon_api_key}"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if "results" in data:
                    records = []
                    for r in data["results"]:
                        # Convert unix timestamp to ISO string
                        dt = datetime.fromtimestamp(r["t"] / 1000.0).isoformat()
                        records.append({
                            "timestamp": dt,
                            "open": r["o"],
                            "high": r["h"],
                            "low": r["l"],
                            "close": r["c"],
                            "volume": r["v"]
                        })
                    df = pd.DataFrame(records)
                    _ohlcv_cache[cache_key] = (time.time(), df)
                    return df
        except Exception as e:
            print(f"Polygon API failed: {e}. Falling back to yfinance.")

    # 2. Fallback to yfinance if Polygon key is missing or request failed/rate-limited
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
            
        df.reset_index(inplace=True)
        date_col = "Datetime" if "Datetime" in df.columns else "Date"
        
        df.rename(columns={
            date_col: "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)
        
        df.dropna(subset=["open", "high", "low", "close"], inplace=True)
        df["timestamp"] = df["timestamp"].apply(lambda x: x.isoformat())
        result_df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        _ohlcv_cache[cache_key] = (time.time(), result_df)
        return result_df
        
    except Exception as e:
        print(f"Error fetching OHLCV for {ticker}: {e}")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])


# ═══════════════════════════════════════════════════════════════════════════════
# YFINANCE FUNDAMENTALS SUPPLEMENT (cached 15 min)
# ═══════════════════════════════════════════════════════════════════════════════

_fundamentals_cache: Dict[str, tuple] = {}
_FUNDAMENTALS_TTL = 900  # 15 minutes

def _get_yfinance_fundamentals(ticker: str) -> Dict:
    """Fetch supplementary fundamentals from yfinance (volume, market_cap, PE, 52W, etc.)."""
    cache_key = ticker.upper()
    if cache_key in _fundamentals_cache:
        cached_time, cached_data = _fundamentals_cache[cache_key]
        if time.time() - cached_time < _FUNDAMENTALS_TTL:
            return cached_data
    
    try:
        info = yf.Ticker(ticker).info
        result = {
            "volume": info.get("volume", 0) or 0,
            "avg_volume": info.get("averageVolume", 0) or 0,
            "market_cap": info.get("marketCap", 0) or 0,
            "pe_ratio": round(info.get("trailingPE", 0) or 0, 2),
            "eps": round(info.get("trailingEps", 0) or 0, 2),
            "dividend_yield": round(info.get("dividendYield", 0) or 0, 2),
            "beta": round(info.get("beta", 1.0) or 1.0, 2),
            "week_52_high": round(info.get("fiftyTwoWeekHigh", 0) or 0, 2),
            "week_52_low": round(info.get("fiftyTwoWeekLow", 0) or 0, 2),
        }
        _fundamentals_cache[cache_key] = (time.time(), result)
        return result
    except Exception as e:
        print(f"yfinance fundamentals failed for {ticker}: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE GENERATOR (Finnhub -> yfinance)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_quote(ticker: str) -> Dict:
    """Fetch live quote primarily from Finnhub, supplemented with yfinance fundamentals."""
    
    if settings.finnhub_api_key:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={ticker.upper()}&token={settings.finnhub_api_key}"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if "c" in data and data["c"] != 0:
                    # Supplement Finnhub price data with yfinance fundamentals
                    supplemental = _get_yfinance_fundamentals(ticker)
                    return {
                        "ticker": ticker.upper(),
                        "price": round(data["c"], 2),
                        "change": round(data["d"] or 0, 2),
                        "change_percent": round(data["dp"] or 0, 2),
                        "prev_close": round(data["pc"], 2),
                        "open": round(data["o"], 2),
                        "day_high": round(data["h"], 2),
                        "day_low": round(data["l"], 2),
                        "week_52_high": supplemental.get("week_52_high", round(data["h"], 2)),
                        "week_52_low": supplemental.get("week_52_low", round(data["l"], 2)),
                        "volume": supplemental.get("volume", 0),
                        "avg_volume": supplemental.get("avg_volume", 0),
                        "market_cap": supplemental.get("market_cap", 0),
                        "pe_ratio": supplemental.get("pe_ratio", 0.0),
                        "eps": supplemental.get("eps", 0.0),
                        "dividend_yield": supplemental.get("dividend_yield", 0.0),
                        "beta": supplemental.get("beta", 1.0),
                        "timestamp": datetime.now().isoformat(),
                    }
        except Exception as e:
            print(f"Finnhub Quote failed: {e}. Falling back to yfinance.")

    # Fallback to yfinance
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
            "dividend_yield": round(info.get("dividendYield", 0) or 0, 2),
            "beta": round(info.get("beta", 1.0), 2),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error fetching quote for {ticker}: {e}")
        return {
            "ticker": ticker.upper(), "price": 0.0, "change": 0.0, "change_percent": 0.0,
            "prev_close": 0.0, "open": 0.0, "day_high": 0.0, "day_low": 0.0,
            "week_52_high": 0.0, "week_52_low": 0.0, "volume": 0, "avg_volume": 0,
            "market_cap": 0, "pe_ratio": 0.0, "eps": 0.0, "dividend_yield": 0.0,
            "beta": 1.0, "timestamp": datetime.now().isoformat(),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# NEWS GENERATOR (Finnhub)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_news(ticker: str, count: int = 5) -> List[Dict]:
    """Fetch premium news from Finnhub."""
    if settings.finnhub_api_key:
        try:
            end = datetime.now()
            start = end - timedelta(days=30)
            url = f"https://finnhub.io/api/v1/company-news?symbol={ticker.upper()}&from={start.strftime('%Y-%m-%d')}&to={end.strftime('%Y-%m-%d')}&token={settings.finnhub_api_key}"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                articles = []
                for article in data[:count]:
                    dt = datetime.fromtimestamp(article.get("datetime", end.timestamp())).isoformat()
                    articles.append({
                        "headline": article.get("headline", ""),
                        "source": article.get("source", "Finnhub"),
                        "sentiment": 0.0,
                        "published_at": dt,
                        "url": article.get("url", ""),
                        "summary": article.get("summary", "")
                    })
                if articles:
                    return articles
        except Exception as e:
            print(f"Finnhub News failed: {e}")
            
    return [{"headline": f"No recent news found for {ticker}.", "source": "System", "sentiment": 0.0, "published_at": datetime.now().isoformat(), "url": ""}]

# ═══════════════════════════════════════════════════════════════════════════════
# 10-K EXCERPT GENERATOR (yfinance fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_10k_excerpts(ticker: str) -> List[Dict]:
    """Provide generic company descriptions to populate the vector DB."""
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
