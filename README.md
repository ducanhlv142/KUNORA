# KUNORA

**KUNORA** is a modular market intelligence platform built to analyze financial markets through a unified data architecture.

The project currently supports cryptocurrency market data through Binance and is being designed to expand toward equities, forex, commodities, and other market data providers.

> KUNORA is under active development.

---

## Overview

KUNORA separates external market data from the application's internal financial domain.

Instead of exposing provider-specific structures directly to the frontend, external data is normalized into KUNORA's own models for instruments, quotes, and candles.

```text
Market Provider
      ↓
Provider Client
      ↓
Data Mapper
      ↓
Market Data Provider
      ↓
KUNORA Domain
      ↓
Service Layer
      ↓
FastAPI
      ↓
Next.js

This architecture allows additional providers and asset classes to be added without tightly coupling the application to a single exchange or API.
Current Features
Market data
- Binance Spot market integration
- Instrument normalization
- Latest market quotes
- Historical OHLCV candles
- Multiple candle intervals
- 24-hour price and volume statistics
- Open/closed candle detection
- Decimal-safe financial data models
Backend
- FastAPI REST API
- Provider abstraction layer
- Market data service layer
- Stable domain error boundaries
- Provider/network error translation
- Shared asynchronous HTTP client lifecycle
- API versioning under /api/v1
Frontend
- Next.js App Router
- TypeScript
- Tailwind CSS
- Candlestick charts using Lightweight Charts
- Instrument selector
- Timeframe selector
- URL-based market state
- Loading states
- Backend availability handling
- Retry/recovery flow
Testing
- Unit tests for domain/provider mapping
- HTTP client failure tests using mocked transports
- Provider error-boundary tests
- FastAPI API contract tests
- Live Binance integration tests
Architecture
                         KUNORA
                            │
              ┌─────────────┴─────────────┐
              │                           │
           Frontend                    Backend
           Next.js                     FastAPI
              │                           │
              │                    MarketDataService
              │                           │
              │                    MarketDataProvider
              │                           │
              │                BinanceMarketDataProvider
              │                           │
              │                     BinanceClient
              │                           │
              └──────────── API ──────────┤
                                          │
                                       Binance

The provider layer is intentionally isolated from the domain layer.
For example:
BTCUSDT
   ↓
Binance Mapper
   ↓
BTC-USDT
   ↓
KUNORA Instrument

The rest of the application does not need to know how Binance identifies the instrument.
Tech Stack
Backend
- Python
- FastAPI
- Pydantic
- httpx
- Uvicorn
- pytest
- pytest-asyncio
Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Lightweight Charts
Data Provider
- Binance Spot REST API
Project Structure
KUNORA/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── providers/
│   │   └── services/
│   └── tests/
│       ├── unit/
│       └── integration/
│
├── web/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── public/
│
└── README.md

Running Locally
Backend
cd backend

Create and activate a virtual environment.
Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:
python -m pip install -r requirements.txt

Start the API:
uvicorn app.main:app --reload

The API will be available at:
http://127.0.0.1:8000

Swagger documentation:
http://127.0.0.1:8000/docs

Frontend
cd web
npm install

Create:
.env.local

with:
KUNORA_API_URL=http://127.0.0.1:8000

Start the development server:
npm run dev

Open:
http://localhost:3000

Tests
Install development dependencies:
cd backend
python -m pip install -r requirements-dev.txt

Run unit tests:
python -m pytest tests\unit -q

Run live integration tests:
python -m pytest tests\integration -m integration -q

Integration tests require network access to the external market data provider.
API
Current market endpoints:
GET /api/v1/market/instruments/{instrument_id}

GET /api/v1/market/quotes/{instrument_id}

GET /api/v1/market/candles/{instrument_id}

Example:
GET /api/v1/market/quotes/BTC-USDT

Roadmap
Planned development includes:
- Realtime WebSocket market streams
- Live candle updates
- Bid/ask market data
- Trade streams
- Instrument search and discovery
- Additional cryptocurrency providers
- Equity market data
- Forex market data
- Commodities
- Technical indicators
- Market screening
- Portfolio analytics
- Alerting
- Persistent historical data
- Provider failover and aggregation
- Automated CI testing
The long-term goal is for KUNORA to provide a provider-independent financial analysis engine rather than being tied to a single exchange or asset class.
Status
KUNORA is currently in early development.
The present implementation establishes the core market-data architecture, Binance integration, REST API, automated testing foundation, and the first interactive market dashboard.
Realtime streaming and broader market coverage are the next major milestones.