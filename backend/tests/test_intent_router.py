import pytest
from agents.intent_router import route_intent

def test_route_intent_quant():
    context = {}
    assert route_intent("what is the short term forecast?", context) == "quant"
    assert route_intent("show me the RSI and MACD", context) == "quant"

def test_route_intent_fundamental():
    context = {}
    assert route_intent("is this a good long term investment?", context) == "fundamental"
    assert route_intent("what was the revenue growth in the latest 10-K?", context) == "fundamental"

def test_route_intent_risk():
    context = {}
    assert route_intent("what is my portfolio risk?", context) == "risk"
    assert route_intent("am I overexposed to tech?", context) == "risk"

def test_route_intent_discovery():
    context = {}
    assert route_intent("what companies should I invest in?", context) == "discovery"
    assert route_intent("give me the top 5 stocks to buy", context) == "discovery"

def test_route_intent_view_mode_fallback():
    # When no keywords match, it should fall back to view_mode
    assert route_intent("tell me more", {"view_mode": "short_term"}) == "quant"
    assert route_intent("tell me more", {"view_mode": "long_term"}) == "fundamental"
    assert route_intent("tell me more", {"view_mode": "portfolio"}) == "risk"

def test_route_intent_default_fallback():
    # When no keywords and no view_mode match, default to fundamental
    assert route_intent("tell me more", {}) == "fundamental"
