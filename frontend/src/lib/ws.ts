/**
 * ws.ts — WebSocket Client for Live Prices
 * ========================================
 * Manages the WebSocket connection to the FastAPI backend.
 */

import { useAppStore } from "@/store/useAppStore";

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private currentSubscription: string | null = null;

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.ws = new WebSocket("ws://localhost:8000/ws/prices");

      this.ws.onopen = () => {
        console.log("[WS] Connected to live prices");
        useAppStore.getState().setWsConnected(true);
        if (this.currentSubscription) {
          this.subscribe(this.currentSubscription);
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Only process price updates
          if (data.price && data.ticker) {
            // Update the live price in the store for the UI headers
            useAppStore.setState({ livePrice: data.price });
          }
        } catch (e) {
          // Ignore parse errors
        }
      };

      this.ws.onclose = () => {
        useAppStore.getState().setWsConnected(false);
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 5000);
  }

  subscribe(ticker: string) {
    this.currentSubscription = ticker;
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: "subscribe", ticker }));
    } else {
      this.connect();
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();
