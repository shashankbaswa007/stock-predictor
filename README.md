# AI Trading Co-Pilot

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=next.js&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.10+-14354C?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

An AI-powered stock market research platform that uses a multi-agent architecture to help users make informed investment decisions. This project demonstrates advanced full-stack capabilities, integrating a highly interactive UI with a robust ML and AI-driven backend.

## 🚀 Features

- **Multi-Agent AI Backend**:
  The application utilizes a distributed, multi-agent orchestration pattern to ensure high-accuracy responses across different financial domains:
  - **1. Intent Router**: The entry point for user queries. It uses NLP keyword heuristics to classify user intents and route the request to the appropriate specialized sub-agent (Quant, Fundamental, Risk, or Discovery).
  - **2. Quant Agent (Short-Term)**: Specializes in technical analysis and statistical forecasting. It runs a custom Machine Learning model (L2 Regularized Ridge Regression) trained dynamically on historical OHLCV data. It computes 25+ technical indicators (RSI, MACD, Bollinger Bands) to provide short-term (5-day) price predictions and confluence signals.
  - **3. Fundamental Agent (Long-Term)**: Specializes in qualitative analysis. It leverages a Retrieval-Augmented Generation (RAG) pipeline to query SEC 10-K filings and recent financial news from a Pinecone Vector Database. It uses a LangChain LLM to parse this unstructured data and output strict, Pydantic-validated JSON sentiment scores.
  - **4. Risk Agent (Portfolio)**: Specializes in portfolio safety. It ingests the user's current holdings and calculates standard financial risk metrics, including 95% Value at Risk (VaR), portfolio beta, and sector concentration risks.
  - **5. Discovery Agent (Market Screener)**: Specializes in market-wide screening. It scans a curated, multi-sector basket of blue-chip stocks to find high-performing equities based on real-time P/E ratios, EPS, and market capitalization.
  - **6. Executive Agent (Synthesizer)**: The final orchestrator. It receives the highly structured output from the designated sub-agent and uses an LLM (Gemini/Groq) to synthesize it into a coherent, human-readable narrative. It outputs actionable BUY/SELL/HOLD signals, distinct reasoning points, and determines the necessary UI state changes (e.g., automatically switching the dashboard to a new ticker).
- **Real-Time Interactive UI**:
  - Split-pane Next.js dashboard featuring TradingView Lightweight Charts.
  - Live price WebSocket streaming.
  - Explainable AI (XAI) UI modules with confidence gauges and reasoning breakdowns.

## 🧠 System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Next.js 15 + React 19)"]
        UI["Split-Pane UI<br/>Dashboard | Chat"]
        Store["Zustand Store<br/>(Global State)"]
        WS["WebSocket Client<br/>(Live Prices)"]
        Chart["TradingView<br/>Lightweight Charts"]
    end

    subgraph API_Layer["API Gateway (FastAPI)"]
        MKT["/api/market/*<br/>History, Quote, News, Predict"]
        CHAT["/api/chat/<br/>Multi-Agent Pipeline"]
        WS_BE["/ws/prices<br/>WebSocket Stream"]
    end

    subgraph Agent_Layer["Multi-Agent System"]
        IR["Intent Router<br/>(Keyword Heuristic)"]
        QA["Quant Agent<br/>(Ridge Regression + Technicals)"]
        FA["Fundamental Agent<br/>(RAG + LLM Synthesis)"]
        RA["Risk Agent<br/>(VaR, Concentration)"]
        DA["Discovery Agent<br/>(Market Screener)"]
        EA["Executive Agent<br/>(LLM Orchestrator)"]
    end

    subgraph Services["Service Layer"]
        ML["ML Model<br/>(scikit-learn Ridge)"]
        TI["Technical Indicators<br/>(RSI, MACD, BB, SMA)"]
        VS["Vector Store<br/>(Pinecone + HuggingFace)"]
        MD["Market Data<br/>(Polygon → Finnhub → yfinance)"]
    end

    UI --> Store
    Store --> CHAT
    Store --> MKT
    WS --> WS_BE
    Chart --> MKT

    MKT --> MD
    MKT --> ML
    MKT --> TI
    CHAT --> IR
    IR --> QA
    IR --> FA
    IR --> RA
    IR --> DA
    QA --> ML
    QA --> TI
    QA --> MD
    FA --> VS
    DA --> MD
    EA --> QA
    EA --> FA
    EA --> RA
    EA --> DA
    WS_BE --> MD
```

## 🛡️ Reliability & Consistency

This application is engineered for production-grade reliability across three pillars:

- **Data Resiliency (Graceful Degradation)**: The market data pipeline uses an **API Cascade** pattern. It attempts to fetch high-fidelity data from premium endpoints (Polygon/Finnhub) first. If rate limits are hit or the service goes down, it seamlessly falls back to `yfinance`. A 5-minute TTL cache protects downstream providers from being overwhelmed.
- **LLM Consistency (Hallucination Prevention)**: The AI agents use **Structured Output Validation** (Pydantic + LangChain) to force deterministic JSON responses from the LLMs. If the LLM fails validation or lacks context, a graceful fallback mechanism intercepts the error and returns a safe, neutral response rather than crashing the UI. Furthermore, the Pinecone Vector Database is configured to dynamically embed missing tickers on the fly to prevent empty context windows.
- **Machine Learning Robustness**: The Quant Agent utilizes **Ridge Regression (L2 Regularized)**. By strictly enforcing a chronological train/test split (preventing look-ahead bias) and penalizing correlated technical indicators, the model avoids the wild, over-confident hallucinations often seen in poorly tuned Neural Networks.
- **System Stability**: The FastAPI backend implements a global exception handler and rate-limiting middleware, while the Next.js frontend wraps critical components in React `ErrorBoundary` modules to isolate component failures.

## 📦 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15, React 19, TypeScript | Server-side rendered dashboard |
| **State Management** | Zustand | Lightweight global state |
| **Charts** | TradingView Lightweight Charts | Real-time candlestick charts |
| **Styling** | Tailwind CSS | Utility-first responsive design |
| **Backend** | FastAPI, Python 3.10+ | Async REST API + WebSocket server |
| **ML Engine** | scikit-learn (Ridge Regression) | Time-series price forecasting |
| **LLM Providers** | Google Gemini / Groq (LLaMA) | AI synthesis and natural language generation |
| **RAG Pipeline** | LangChain + Pinecone + HuggingFace | Retrieval-Augmented Generation over SEC filings |
| **Market Data** | Polygon.io → Finnhub → yfinance | Multi-tier API cascade with graceful fallback |
| **Containerization** | Docker + Docker Compose | One-command deployment |

## 📂 Project Structure

```
Stock_predictor/
├── backend/
│   ├── agents/                # Multi-Agent System
│   │   ├── intent_router.py   # NLP keyword heuristic router
│   │   ├── quant_agent.py     # Short-term ML + technical analysis
│   │   ├── fundamental_agent.py # Long-term RAG + LLM analysis
│   │   ├── risk_agent.py      # Portfolio risk (VaR, concentration)
│   │   ├── discovery_agent.py # Market-wide stock screener
│   │   ├── executive_agent.py # LLM orchestrator + synthesizer
│   │   └── llm_factory.py    # Gemini/Groq/OpenAI abstraction
│   ├── api/                   # FastAPI Route Handlers
│   │   ├── routes_market.py   # OHLCV, quotes, news, predictions
│   │   ├── routes_chat.py     # Multi-agent chat pipeline
│   │   ├── routes_portfolio.py # Portfolio CRUD + risk metrics
│   │   └── routes_ws.py       # WebSocket live price streaming
│   ├── services/              # Core Business Logic
│   │   ├── ml_model.py        # Ridge Regression forecaster
│   │   ├── technical_indicators.py # RSI, MACD, Bollinger Bands, SMA
│   │   ├── vector_store.py    # Pinecone RAG vector database
│   │   └── mock_data.py       # Market data integration layer
│   ├── middleware/             # Request middleware
│   │   └── rate_limit.py      # IP-based rate limiting
│   ├── tests/                 # pytest test suite
│   ├── config.py              # Pydantic Settings (env management)
│   ├── main.py                # FastAPI application entry point
│   ├── Dockerfile             # Backend container image
│   └── requirements.txt       # Python dependencies
├── frontend/
│   └── src/
│       ├── app/               # Next.js App Router pages
│       ├── components/        # React UI components
│       │   ├── dashboard/     # Charts, ticker search, metrics
│       │   ├── chat/          # AI chat panel, messages, input
│       │   ├── portfolio/     # Holdings table, risk gauges
│       │   └── ui/            # Shared UI primitives
│       ├── store/             # Zustand global state
│       └── lib/               # Utility functions
├── docker-compose.yml         # Multi-container orchestration
├── .gitignore
└── README.md
```

## 🛠 Setup Instructions

### 1. Prerequisites
- Docker & Docker Compose (Recommended)
- OR Local Setup:
  - Python 3.10+
  - Node.js 18+

### 2. Environment Variables
Create a `.env` file in the `backend/` directory by copying `.env.example`:
```bash
cp backend/.env.example backend/.env
```
Fill in the API keys (e.g., `GEMINI_API_KEY`, `PINECONE_API_KEY`). If left empty, the application will run using mock data and mock LLM responses.

### 3. Run with Docker (Recommended)
From the root of the repository:
```bash
docker-compose up --build
```
- Frontend available at: `http://localhost:3000`
- Backend API available at: `http://localhost:8000/docs`

### 4. Run Locally (Without Docker)

**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server health check & config status |
| `/api/market/history` | GET | Historical OHLCV + technical indicators |
| `/api/market/quote` | GET | Real-time quote snapshot |
| `/api/market/news` | GET | Company news headlines |
| `/api/market/predict` | GET | ML-based price forecast |
| `/api/chat/` | POST | Multi-agent AI analysis pipeline |
| `/api/portfolio/` | GET | Portfolio holdings & summary |
| `/api/portfolio/risk` | GET | Portfolio risk metrics |
| `/ws/prices` | WS | Live price WebSocket stream |

## 🧪 Testing

The backend includes a comprehensive `pytest` suite for the ML models, intent routers, and technical indicators.
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📝 License
Educational Project. For informational purposes only. Not financial advice.

