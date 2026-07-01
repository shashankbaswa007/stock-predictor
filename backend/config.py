"""
config.py — Centralized Configuration via Pydantic Settings
============================================================
All secrets and tunables are loaded from environment variables (or .env file).
Every field has a safe default so the app runs fully in mock mode out of the box.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    # ── Server ────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000"]

    # ── Market Data Providers (leave empty → mock data) ───────────────────
    alpha_vantage_api_key: str = ""
    finnhub_api_key: str = ""
    polygon_api_key: str = ""

    # ── AI / LLM (leave empty → mock agent responses) ─────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    gemini_api_key: str = ""
    groq_api_key: str = ""

    # ── Vector Database (leave empty → in-memory FAISS) ───────────────────
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "trading-copilot"

    # ── Helpers ───────────────────────────────────────────────────────────
    @property
    def use_mock_market_data(self) -> bool:
        """True when no real market data provider key is configured."""
        # For Phase 5 we use yfinance which is always free and needs no key.
        # But we leave this for architecture consistency.
        return not any([
            self.alpha_vantage_api_key,
            self.finnhub_api_key,
            self.polygon_api_key,
        ])

    @property
    def use_mock_llm(self) -> bool:
        """True when no real LLM key is configured."""
        return not any([
            self.openai_api_key,
            self.gemini_api_key,
            self.groq_api_key
        ])

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False,
    }


# Singleton instance — import this everywhere
settings = Settings()

import os
if settings.pinecone_api_key:
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
if settings.groq_api_key:
    os.environ["GROQ_API_KEY"] = settings.groq_api_key
