"""
mock_data.py — Deterministic Mock Data Generators
===================================================
Generates realistic financial data using seeded random number generators
so results are reproducible per ticker symbol. All generators produce
data that looks authentic on charts without requiring real API keys.

Generators:
  • generate_ohlcv()     — Candlestick OHLCV time-series
  • generate_quote()     — Snapshot quote for a ticker
  • generate_tick()      — Single price tick for WebSocket streaming
  • generate_news()      — Mock news headlines with sentiment
  • generate_10k_excerpts() — Mock SEC 10-K filing excerpts for RAG
"""

import hashlib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _ticker_seed(ticker: str) -> int:
    """
    Derive a deterministic integer seed from a ticker symbol.
    Uses SHA-256 hash truncated to 32 bits for stable cross-platform results.
    """
    h = hashlib.sha256(ticker.upper().encode()).hexdigest()
    return int(h[:8], 16)


# Base prices for well-known tickers (for realism). Unknown tickers get
# a hash-derived base price between $20 and $500.
_BASE_PRICES: Dict[str, float] = {
    "AAPL": 192.50,  "MSFT": 415.60,  "NVDA": 920.30,
    "GOOGL": 172.80, "AMZN": 193.50,  "META": 505.75,
    "TSLA": 248.40,  "JPM": 198.20,   "V": 278.90,
    "JNJ": 155.30,   "WMT": 168.50,   "XOM": 110.80,
    "AMD": 162.40,   "NFLX": 635.20,  "DIS": 101.50,
}

# Volatility profiles per sector-like grouping
_VOLATILITY: Dict[str, float] = {
    "AAPL": 0.018,  "MSFT": 0.016,  "NVDA": 0.032,
    "GOOGL": 0.019, "AMZN": 0.022,  "META": 0.025,
    "TSLA": 0.038,  "JPM": 0.015,   "V": 0.014,
    "JNJ": 0.010,   "WMT": 0.012,   "XOM": 0.020,
    "AMD": 0.035,   "NFLX": 0.028,  "DIS": 0.022,
}


def _get_base_price(ticker: str) -> float:
    """Return base price — known tickers use preset, others get hash-derived."""
    if ticker in _BASE_PRICES:
        return _BASE_PRICES[ticker]
    seed = _ticker_seed(ticker)
    return 20.0 + (seed % 48000) / 100.0  # $20 – $500


def _get_volatility(ticker: str) -> float:
    """Return daily volatility — known tickers use preset, others get moderate."""
    if ticker in _VOLATILITY:
        return _VOLATILITY[ticker]
    seed = _ticker_seed(ticker)
    return 0.012 + (seed % 2500) / 100000.0  # 1.2% – 3.7%


# ═══════════════════════════════════════════════════════════════════════════════
# OHLCV GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def _period_to_days(period: str) -> int:
    """Convert period string to approximate number of calendar days."""
    mapping = {
        "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
        "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
    }
    return mapping.get(period, 180)


def _interval_to_minutes(interval: str) -> int:
    """Convert interval string to minutes per candle."""
    mapping = {
        "1m": 1, "5m": 5, "15m": 15, "30m": 30,
        "1h": 60, "4h": 240, "1d": 1440, "1wk": 10080,
    }
    return mapping.get(interval, 1440)


def generate_ohlcv(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Generate realistic OHLCV candlestick data using geometric Brownian motion
    with mean-reverting tendencies, occasional gaps, and volume correlation.

    Args:
        ticker:   Stock ticker symbol (used as seed)
        period:   Time period — 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
        interval: Candle interval — 1m, 5m, 15m, 1h, 1d, 1wk

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    rng = np.random.default_rng(_ticker_seed(ticker))
    base_price = _get_base_price(ticker)
    daily_vol = _get_volatility(ticker)

    total_days = _period_to_days(period)
    minutes_per_candle = _interval_to_minutes(interval)

    # Calculate number of candles
    if minutes_per_candle >= 1440:
        # Daily or weekly — only trading days
        trading_days = int(total_days * 5 / 7)
        if minutes_per_candle == 10080:  # weekly
            n_candles = max(trading_days // 5, 10)
        else:
            n_candles = max(trading_days, 5)
    else:
        # Intraday — ~6.5 hours trading per day
        trading_minutes_per_day = 390
        candles_per_day = trading_minutes_per_day // minutes_per_candle
        trading_days = min(int(total_days * 5 / 7), 5)  # Limit intraday
        n_candles = max(candles_per_day * trading_days, 20)

    # ── Generate close prices via GBM with mean-reversion ─────────────────
    # Scale volatility to match candle interval
    candle_vol = daily_vol * math.sqrt(minutes_per_candle / 1440)

    # Drift: slight upward bias (realistic for equities)
    mu = 0.0002 * (minutes_per_candle / 1440)

    # Mean-reversion strength (pulls price back toward base)
    reversion_strength = 0.002

    closes = np.zeros(n_candles)
    closes[0] = base_price * (1 + rng.normal(0, 0.005))

    for i in range(1, n_candles):
        # Mean-reverting drift
        log_ratio = math.log(closes[i - 1] / base_price)
        reversion = -reversion_strength * log_ratio

        # Occasional momentum shifts (regime changes)
        if rng.random() < 0.03:
            shock = rng.normal(0, candle_vol * 3)
        else:
            shock = rng.normal(0, candle_vol)

        # Autocorrelation in returns (momentum)
        if i >= 2:
            prev_return = (closes[i - 1] - closes[i - 2]) / closes[i - 2]
            momentum = 0.15 * prev_return
        else:
            momentum = 0.0

        ret = mu + reversion + shock + momentum
        closes[i] = closes[i - 1] * (1 + ret)

        # Floor price at $1
        closes[i] = max(closes[i], 1.0)

    # ── Derive OHLC from close prices ─────────────────────────────────────
    opens = np.zeros(n_candles)
    highs = np.zeros(n_candles)
    lows = np.zeros(n_candles)

    opens[0] = closes[0] * (1 + rng.normal(0, 0.002))
    for i in range(1, n_candles):
        # Gap: open can differ from previous close
        gap = rng.normal(0, candle_vol * 0.3)
        opens[i] = closes[i - 1] * (1 + gap)

    # Intra-candle range
    for i in range(n_candles):
        candle_range = abs(closes[i] - opens[i])
        wick_up = abs(rng.normal(0, candle_range * 0.5)) + candle_range * 0.1
        wick_down = abs(rng.normal(0, candle_range * 0.5)) + candle_range * 0.1

        highs[i] = max(opens[i], closes[i]) + wick_up
        lows[i] = min(opens[i], closes[i]) - wick_down
        lows[i] = max(lows[i], 0.50)  # Floor

    # ── Generate volume ───────────────────────────────────────────────────
    # Volume correlates with price movement magnitude
    base_volume = rng.integers(20_000_000, 80_000_000)
    price_changes = np.abs(np.diff(closes, prepend=closes[0])) / closes
    volume_noise = rng.lognormal(0, 0.4, n_candles)
    volumes = (base_volume * volume_noise * (1 + price_changes * 5)).astype(int)

    # Scale volume for intraday
    if minutes_per_candle < 1440:
        volumes = (volumes * minutes_per_candle / 1440).astype(int)

    # ── Generate timestamps ───────────────────────────────────────────────
    end_dt = datetime.now().replace(second=0, microsecond=0)
    if minutes_per_candle >= 1440:
        # Daily/weekly — generate trading days (skip weekends)
        timestamps = []
        dt = end_dt
        while len(timestamps) < n_candles:
            if dt.weekday() < 5:  # Mon–Fri
                timestamps.append(dt)
            dt -= timedelta(days=1)
        timestamps.reverse()
    else:
        # Intraday
        timestamps = []
        dt = end_dt
        for _ in range(n_candles):
            timestamps.append(dt)
            dt -= timedelta(minutes=minutes_per_candle)
        timestamps.reverse()

    # Trim to exact count
    timestamps = timestamps[:n_candles]

    # ── Build DataFrame ───────────────────────────────────────────────────
    df = pd.DataFrame({
        "timestamp": [t.isoformat() for t in timestamps],
        "open": np.round(opens, 2),
        "high": np.round(highs, 2),
        "low": np.round(lows, 2),
        "close": np.round(closes, 2),
        "volume": volumes,
    })

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_quote(ticker: str) -> Dict:
    """
    Generate a realistic snapshot quote for the given ticker.
    Uses the last candle from a short OHLCV generation.
    """
    rng = np.random.default_rng(_ticker_seed(ticker) + 42)
    base = _get_base_price(ticker)
    vol = _get_volatility(ticker)

    price = base * (1 + rng.normal(0, vol))
    prev_close = base * (1 + rng.normal(0, vol * 0.5))
    change = price - prev_close
    change_pct = (change / prev_close) * 100

    day_high = price * (1 + abs(rng.normal(0, vol * 0.6)))
    day_low = price * (1 - abs(rng.normal(0, vol * 0.6)))
    week52_high = base * (1 + abs(rng.normal(0.05, 0.08)))
    week52_low = base * (1 - abs(rng.normal(0.05, 0.08)))

    volume = int(rng.integers(20_000_000, 80_000_000))
    avg_volume = int(volume * rng.uniform(0.8, 1.3))
    market_cap = price * rng.integers(1_000_000_000, 15_000_000_000)

    pe_ratio = rng.uniform(15, 45)
    eps = price / pe_ratio
    dividend_yield = rng.uniform(0, 2.5) if rng.random() > 0.3 else 0.0
    beta = rng.uniform(0.7, 1.8)

    return {
        "ticker": ticker.upper(),
        "price": round(price, 2),
        "change": round(change, 2),
        "change_percent": round(change_pct, 2),
        "prev_close": round(prev_close, 2),
        "open": round(prev_close * (1 + rng.normal(0, 0.003)), 2),
        "day_high": round(day_high, 2),
        "day_low": round(day_low, 2),
        "week_52_high": round(week52_high, 2),
        "week_52_low": round(week52_low, 2),
        "volume": volume,
        "avg_volume": avg_volume,
        "market_cap": int(market_cap),
        "pe_ratio": round(pe_ratio, 2),
        "eps": round(eps, 2),
        "dividend_yield": round(dividend_yield, 2),
        "beta": round(beta, 2),
        "timestamp": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LIVE TICK GENERATOR (for WebSocket)
# ═══════════════════════════════════════════════════════════════════════════════

class TickGenerator:
    """
    Stateful tick generator for WebSocket price streaming.
    Maintains price state across ticks to create a realistic random walk.
    Each instance is bound to a ticker with a deterministic starting price.
    """

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.rng = np.random.default_rng(_ticker_seed(self.ticker) + int(datetime.now().timestamp()) % 10000)
        self.price = _get_base_price(self.ticker)
        self.vol = _get_volatility(self.ticker) * 0.1  # Per-tick vol (much smaller)
        self.bid_spread = self.price * 0.0003  # 3 bps spread
        self.tick_count = 0

    def next_tick(self) -> Dict:
        """Generate the next price tick."""
        # Random walk step
        shock = self.rng.normal(0, self.vol)

        # Occasional micro-jumps (simulates order flow)
        if self.rng.random() < 0.05:
            shock *= 3

        self.price *= (1 + shock)
        self.price = max(self.price, 1.0)
        self.tick_count += 1

        # Bid/Ask spread
        bid = self.price - self.bid_spread / 2
        ask = self.price + self.bid_spread / 2

        # Tick volume (random trade size)
        tick_volume = int(self.rng.integers(100, 5000))

        return {
            "type": "tick",
            "ticker": self.ticker,
            "price": round(self.price, 2),
            "bid": round(bid, 2),
            "ask": round(ask, 2),
            "volume": tick_volume,
            "tick_number": self.tick_count,
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS HEADLINE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

_NEWS_TEMPLATES_POSITIVE = [
    "{ticker} Reports Record Quarterly Revenue, Beating Wall Street Estimates by {pct}%",
    "{ticker} Announces Strategic Partnership with Major Cloud Provider",
    "{ticker} Raises Full-Year Guidance on Strong Consumer Demand",
    "Analysts Upgrade {ticker} to 'Outperform', Citing AI Growth Runway",
    "{ticker} Board Approves ${amount}B Share Buyback Program",
    "{ticker} Expands into International Markets with {region} Launch",
    "Insider Buying Detected: {ticker} CEO Purchases {shares}K Shares",
    "{ticker} Patent Portfolio Grows to {patents} Active Patents in Q{quarter}",
    "{ticker}'s New Product Line Sees {pct}% Adoption Rate in First Month",
    "Morgan Stanley Raises {ticker} Price Target to ${target}",
]

_NEWS_TEMPLATES_NEGATIVE = [
    "{ticker} Misses Earnings Expectations, Revenue Down {pct}% YoY",
    "SEC Launches Investigation into {ticker}'s Accounting Practices",
    "{ticker} Announces {count} Layoffs Amid Restructuring Plan",
    "Analysts Downgrade {ticker} on Concerns Over Market Saturation",
    "{ticker} Faces Supply Chain Disruptions, Warns of Delayed Shipments",
    "{ticker} CFO Departure Raises Governance Concerns Among Investors",
    "Short Sellers Increase Positions in {ticker} by {pct}%",
    "{ticker}'s Key Patent Challenged in Federal Court",
    "Consumer Reports Flags Quality Issues with {ticker}'s Flagship Product",
    "{ticker} Loses Major Contract to Competitor Worth ${amount}B",
]

_NEWS_TEMPLATES_NEUTRAL = [
    "{ticker} Scheduled to Report Q{quarter} Earnings on {date}",
    "{ticker} CEO to Keynote at Annual Tech Innovation Summit",
    "Options Activity Elevated Ahead of {ticker} Earnings Release",
    "{ticker} Maintains Dividend at ${div} Per Share for Q{quarter}",
    "Institutional Ownership of {ticker} Remains Stable at {pct}%",
    "Industry Report: {ticker}'s Market Share Holds Steady at {pct}%",
]

_SOURCES = [
    "Reuters", "Bloomberg", "CNBC", "WSJ", "MarketWatch",
    "Barron's", "Financial Times", "Seeking Alpha", "The Motley Fool",
]

_REGIONS = ["European", "Asia-Pacific", "Latin American", "Middle Eastern"]


def generate_news(ticker: str, count: int = 8) -> List[Dict]:
    """
    Generate realistic mock news headlines with sentiment scores.

    Args:
        ticker: Stock ticker symbol
        count:  Number of headlines to generate

    Returns:
        List of dicts with: headline, source, sentiment, published_at
    """
    rng = np.random.default_rng(_ticker_seed(ticker) + 100)
    articles = []

    for i in range(count):
        # Weighted sentiment distribution: ~40% positive, 25% negative, 35% neutral
        roll = rng.random()
        if roll < 0.40:
            templates = _NEWS_TEMPLATES_POSITIVE
            sentiment = round(rng.uniform(0.5, 0.95), 2)
        elif roll < 0.65:
            templates = _NEWS_TEMPLATES_NEGATIVE
            sentiment = round(rng.uniform(-0.95, -0.3), 2)
        else:
            templates = _NEWS_TEMPLATES_NEUTRAL
            sentiment = round(rng.uniform(-0.15, 0.15), 2)

        template = templates[rng.integers(0, len(templates))]

        headline = template.format(
            ticker=ticker.upper(),
            pct=rng.integers(3, 25),
            amount=round(rng.uniform(0.5, 10.0), 1),
            region=_REGIONS[rng.integers(0, len(_REGIONS))],
            shares=rng.integers(5, 50),
            patents=rng.integers(200, 5000),
            quarter=rng.integers(1, 5),
            target=int(_get_base_price(ticker) * rng.uniform(1.05, 1.35)),
            count=rng.integers(500, 5000),
            date=(datetime.now() + timedelta(days=int(rng.integers(5, 45)))).strftime("%B %d"),
            div=round(rng.uniform(0.20, 2.50), 2),
        )

        published_at = datetime.now() - timedelta(
            hours=int(rng.integers(1, 168))  # Up to 1 week ago
        )

        articles.append({
            "headline": headline,
            "source": _SOURCES[rng.integers(0, len(_SOURCES))],
            "sentiment": sentiment,
            "published_at": published_at.isoformat(),
            "url": f"https://example.com/news/{ticker.lower()}-{i}",
        })

    # Sort by recency
    articles.sort(key=lambda a: a["published_at"], reverse=True)
    return articles


# ═══════════════════════════════════════════════════════════════════════════════
# 10-K / SEC FILING EXCERPT GENERATOR (for RAG pipeline)
# ═══════════════════════════════════════════════════════════════════════════════

_10K_SECTIONS = {
    "business_overview": [
        "The Company operates in {segments} reportable segments and generated "
        "total revenue of ${revenue}B for the fiscal year ended {fy_end}. "
        "Our principal products and services include cloud computing, enterprise "
        "software, and consumer electronics. We continue to invest heavily in "
        "research and development, with R&D expenditures of ${rd}B representing "
        "{rd_pct}% of total revenue.",

        "During the fiscal year, the Company expanded its operations to "
        "{countries} countries and increased its global workforce to approximately "
        "{employees} employees. Key growth drivers included our AI and machine "
        "learning platforms, which saw {ai_growth}% year-over-year revenue growth.",
    ],
    "risk_factors": [
        "We face intense competition across all of our market segments. Our "
        "competitors include large, well-established technology companies as well "
        "as numerous emerging startups. Failure to innovate and maintain market "
        "share could materially impact our revenue and profitability. Additionally, "
        "regulatory changes in key markets, including the European Union's Digital "
        "Markets Act, may impose operational constraints.",

        "Our international operations subject us to risks including foreign "
        "currency fluctuations, geopolitical instability, and varying regulatory "
        "requirements. Approximately {intl_rev}% of our total revenue is derived "
        "from international markets. Trade restrictions or tariffs could adversely "
        "affect our supply chain and cost structure.",
    ],
    "financial_highlights": [
        "Total revenue for fiscal year {fy} was ${revenue}B, representing a "
        "{rev_growth}% increase compared to the prior year. Gross margin improved "
        "to {gross_margin}% from {prev_gm}% in the prior year, driven by favorable "
        "product mix and operational efficiencies. Operating income was ${op_income}B, "
        "a {op_growth}% increase year-over-year.",

        "Cash and cash equivalents totaled ${cash}B as of {fy_end}. During the "
        "fiscal year, we generated ${fcf}B in free cash flow, returned ${buyback}B "
        "to shareholders through share repurchases, and paid ${dividends}B in "
        "dividends. Our debt-to-equity ratio stands at {de_ratio}.",
    ],
    "management_discussion": [
        "Management believes the Company is well-positioned to capitalize on "
        "the growing demand for artificial intelligence solutions. Our investment "
        "in proprietary large language models and inference infrastructure positions "
        "us competitively in the enterprise AI market, which we estimate will reach "
        "${tam}B by {tam_year}.",

        "Looking ahead, we expect revenue growth in the range of {low_guide}% to "
        "{high_guide}% for the next fiscal year, driven primarily by our cloud "
        "services and AI platform segments. Capital expenditures are projected at "
        "${capex}B as we expand data center capacity to meet growing demand.",
    ],
}


def generate_10k_excerpts(ticker: str) -> List[Dict]:
    """
    Generate mock 10-K filing excerpts suitable for embedding in a vector store.

    Args:
        ticker: Stock ticker symbol

    Returns:
        List of dicts with: section, content, filing_date, fiscal_year
    """
    rng = np.random.default_rng(_ticker_seed(ticker) + 200)
    base = _get_base_price(ticker)
    excerpts = []

    # Scale financial figures to be proportional to stock price (rough proxy)
    scale = base / 200.0  # Normalize around $200 base

    fy = 2024
    fy_end = f"December 31, {fy}"

    params = {
        "segments": rng.integers(2, 6),
        "revenue": round(scale * rng.uniform(30, 120), 1),
        "rd": round(scale * rng.uniform(5, 25), 1),
        "rd_pct": round(rng.uniform(12, 28), 1),
        "countries": rng.integers(40, 180),
        "employees": f"{rng.integers(30, 200)},000",
        "ai_growth": rng.integers(25, 85),
        "intl_rev": rng.integers(35, 65),
        "fy": fy,
        "fy_end": fy_end,
        "rev_growth": rng.integers(5, 22),
        "gross_margin": round(rng.uniform(55, 78), 1),
        "prev_gm": round(rng.uniform(52, 75), 1),
        "op_income": round(scale * rng.uniform(8, 40), 1),
        "op_growth": rng.integers(8, 30),
        "cash": round(scale * rng.uniform(10, 60), 1),
        "fcf": round(scale * rng.uniform(8, 45), 1),
        "buyback": round(scale * rng.uniform(5, 25), 1),
        "dividends": round(scale * rng.uniform(1, 8), 1),
        "de_ratio": round(rng.uniform(0.3, 2.0), 2),
        "tam": rng.integers(200, 800),
        "tam_year": 2028 + rng.integers(0, 4),
        "low_guide": rng.integers(6, 12),
        "high_guide": rng.integers(13, 22),
        "capex": round(scale * rng.uniform(5, 20), 1),
    }

    for section_name, templates in _10K_SECTIONS.items():
        for template in templates:
            content = template.format(**params)
            excerpts.append({
                "section": section_name,
                "content": content,
                "ticker": ticker.upper(),
                "filing_date": f"{fy + 1}-02-{rng.integers(10, 28):02d}",
                "fiscal_year": fy,
                "doc_type": "10-K",
            })

    return excerpts
