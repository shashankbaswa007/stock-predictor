"""
routes_ws.py — WebSocket Route for Live Price Streaming (Phase 2: Realistic Ticks)
====================================================================================
Streams realistic mock price ticks via WebSocket using the TickGenerator.
Supports multiple tickers per connection via query parameter.
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from services.mock_data import TickGenerator

router = APIRouter()


@router.websocket("/ws/prices")
async def websocket_prices(
    websocket: WebSocket,
    ticker: str = Query("AAPL", description="Ticker to stream"),
):
    """
    WebSocket endpoint for streaming live price updates.

    Sends a realistic random-walk tick every 500ms using the TickGenerator.
    The tick includes: price, bid, ask, volume, and timestamp.

    Query params:
      • ticker — Stock symbol to stream (default: AAPL)

    Message format (server → client):
      {
        "type": "tick",
        "ticker": "AAPL",
        "price": 195.32,
        "bid": 195.29,
        "ask": 195.35,
        "volume": 2450,
        "tick_number": 42,
        "timestamp": "2024-01-15T10:30:00.000"
      }

    Client can send JSON messages to change the ticker mid-stream:
      {"action": "subscribe", "ticker": "NVDA"}
    """
    await websocket.accept()

    # Initialize tick generator for the requested ticker
    generator = TickGenerator(ticker.upper())

    try:
        while True:
            # Check for incoming messages (non-blocking)
            try:
                # Wait briefly for client messages (ticker change requests)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.5  # 500ms tick interval
                )
                # Parse client command
                try:
                    data = json.loads(message)
                    if data.get("action") == "subscribe" and data.get("ticker"):
                        new_ticker = data["ticker"].upper()
                        generator = TickGenerator(new_ticker)
                        # Acknowledge subscription change
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "ticker": new_ticker,
                            "message": f"Now streaming {new_ticker}",
                        }))
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass  # Ignore malformed messages

            except asyncio.TimeoutError:
                pass  # No message — proceed to send tick

            # Generate and send the next tick
            tick = generator.next_tick()
            await websocket.send_text(json.dumps(tick))

    except WebSocketDisconnect:
        pass  # Client disconnected gracefully
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
