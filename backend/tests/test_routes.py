import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "env" in data

def test_market_history():
    response = client.get("/api/market/history?ticker=AAPL&period=1mo&interval=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["period"] == "1mo"
    assert "data" in data
    assert len(data["data"]) > 0
    # Check that technical indicators are included by default
    assert "indicators" in data

def test_market_quote():
    response = client.get("/api/market/quote?ticker=MSFT")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "MSFT"
    assert "price" in data
    assert "change_percent" in data

def test_market_news():
    response = client.get("/api/market/news?ticker=NVDA&count=3")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "NVDA"
    assert len(data["articles"]) == 3
    assert "headline" in data["articles"][0]

# Chat tests can be flaky if using real LLM, but since config defaults to mock if no key,
# this test is safe to run in a test environment without keys.
def test_chat_pipeline():
    payload = {
        "message": "analyze AAPL for short term",
        "ticker": "AAPL",
        "ui_context": {
            "view_mode": "short_term",
            "portfolio_state": {}
        }
    }
    response = client.post("/api/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "signal" in data
    assert "reasoning" in data
    assert "agent_source" in data
