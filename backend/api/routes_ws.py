"""
routes_ws.py — WebSocket Route for Live Price Streaming (Phase 5: Real API)
=============================================================================
Streams real price ticks via WebSocket using yfinance polling.
"""

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from services.mock_data import generate_quote

router = APIRouter()

@router.websocket("/ws/prices")
async def websocket_prices(
    websocket: WebSocket,
    ticker: str = Query("AAPL", description="Ticker to stream"),
):
    await websocket.accept()
    current_ticker = ticker.upper()
    tick_count = 0

    try:
        while True:
            # Check for incoming messages (non-blocking)
            try:
                # Wait briefly for client messages (ticker change requests)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=10.0  # Poll yfinance every 10 seconds
                )
                try:
                    data = json.loads(message)
                    if data.get("action") == "subscribe" and data.get("ticker"):
                        current_ticker = data["ticker"].upper()
                        tick_count = 0
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "ticker": current_ticker,
                            "message": f"Now streaming {current_ticker}",
                        }))
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass
            except asyncio.TimeoutError:
                pass  # Proceed to send tick after timeout

            # Fetch real quote from yfinance
            quote = generate_quote(current_ticker)
            tick_count += 1
            
            tick = {
                "type": "tick",
                "ticker": current_ticker,
                "price": quote.get("price", 0.0),
                "bid": quote.get("price", 0.0), # yf doesn't always provide bid/ask for free
                "ask": quote.get("price", 0.0),
                "volume": quote.get("volume", 0),
                "tick_number": tick_count,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(tick))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS Error: {e}")
        try:
            await websocket.close()
        except:
            pass
