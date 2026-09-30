# KUNORA

**KUNORA** is a modular financial market intelligence platform built around a provider-independent market data architecture.

The project currently supports cryptocurrency market data through Binance and is being designed to expand toward equities, forex, commodities, and additional market data providers.

> KUNORA is under active development.

---

## Overview

KUNORA separates external market data providers from the application's internal financial domain.

Instead of exposing provider-specific payloads directly to the frontend, external data is normalized into KUNORA's own models for instruments, quotes, and candles.

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
```

This architecture allows additional providers and asset classes to be added without tightly coupling the application to a single exchange or API.

---

## Current Features

### Market Data

- Binance Spot market integration
- Instrument normalization
- Latest market quotes
- Historical OHLCV candles
- Multiple candle intervals
- 24-hour price and volume statistics
- Open/closed candle detection
- Decimal-safe financial data models
- BTC/USDT and ETH/USDT market selection
- URL-based timeframe selection

### Backend

- FastAPI REST API
- Provider abstraction layer
- Market data service layer
- Stable domain error boundaries
- Binance-specific network and response error translation
- Shared asynchronous HTTP client lifecycle
- API versioning under `/api/v1`
- Health endpoint for backend availability checks

### Frontend

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- Candlestick charts powered by Lightweight Charts
- Instrument selector
- Timeframe selector
- URL-based market state
- Price, percentage, and volume formatting
- Loading states
- Backend availability handling
- Retry and recovery flow
- Graceful market-unavailable state without treating provider outages as application crashes

### Testing

- Unit tests for Binance mapping
- Unit tests for provider error boundaries
- HTTP client failure tests using mocked transports
- FastAPI API contract tests
- Live Binance integration tests
- pytest and pytest-asyncio test foundation

---

## Architecture

```text
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
```

The provider layer is intentionally isolated from the domain layer.

For example:

```text
BTCUSDT
   ↓
Binance Mapper
   ↓
BTC-USDT
   ↓
KUNORA Instrument
```

The rest of the application does not need to know how Binance represents or identifies an instrument.

---

## Data Flow

A typical market-data request currently follows this path:

```text
Browser
  ↓
Next.js
  ↓
KUNORA REST API
  ↓
MarketDataService
  ↓
MarketDataProvider
  ↓
Binance Client
  ↓
Binance REST API
```

The response travels back through the same layers after being normalized into KUNORA domain models.

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- httpx
- Uvicorn
- pytest
- pytest-asyncio

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Lightweight Charts

### Data Provider

- Binance Spot REST API

---

## Project Structure

```text
KUNORA/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── providers/
│   │   └── services/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── web/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   │
│   ├── public/
│   ├── .env.example
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/ducanhlv142/KUNORA.git
cd KUNORA
```

### 2. Backend

Move into the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install runtime dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

### 3. Frontend

Open another terminal and move into the frontend directory:

```powershell
cd web
```

Install dependencies:

```powershell
npm install
```

Create:

```text
.env.local
```

with:

```env
KUNORA_API_URL=http://127.0.0.1:8000
```

You can use the provided `.env.example` as a reference.

Start the frontend:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## Tests

Install development dependencies:

```powershell
cd backend
python -m pip install -r requirements-dev.txt
```

Run unit tests:

```powershell
python -m pytest tests\unit -q
```

Run live integration tests:

```powershell
python -m pytest tests\integration -m integration -q
```

Integration tests require network access to the external market data provider.

---

## API

Current market endpoints:

```text
GET /api/v1/market/instruments/{instrument_id}

GET /api/v1/market/quotes/{instrument_id}

GET /api/v1/market/candles/{instrument_id}
```

Example quote request:

```text
GET /api/v1/market/quotes/BTC-USDT
```

Example candles request:

```text
GET /api/v1/market/candles/BTC-USDT?interval=1h&limit=200
```

---

## Current UI

The current market screen provides:

- Instrument selection
- Timeframe selection
- Latest price
- 24-hour percentage change
- 24-hour high
- 24-hour low
- 24-hour base volume
- Historical candlestick chart
- Loading feedback
- Backend outage handling
- Retry/recovery behavior

The interface is intentionally minimal while the core market-data architecture is being established.

---

## Error Handling

KUNORA translates provider-specific failures into stable application-level errors.

```text
Network / HTTP Failure
        ↓
Binance Client
        ↓
Binance Error
        ↓
Market Data Provider
        ↓
KUNORA Market Error
        ↓
API / UI Recovery State
```

Expected provider outages are treated as recoverable application states rather than frontend crashes.

---

## Roadmap

Planned development includes:

- Realtime WebSocket market streams
- Live candle updates
- Bid/ask market data
- Trade streams
- Instrument search and discovery
- Market shell and navigation
- Additional cryptocurrency providers
- Equity market data
- Forex market data
- Commodities market data
- Technical indicators
- Market screening
- Portfolio analytics
- Alerting
- Persistent historical data
- Provider failover and aggregation
- Automated CI testing
- Deployment and environment configuration

The long-term goal is for KUNORA to become a provider-independent financial analysis engine rather than an application tied to a single exchange or asset class.

---

## Development Status

KUNORA is currently in early development.

The present implementation establishes:

- Core market domain models
- Binance REST integration
- Provider abstraction
- Service layer
- Versioned FastAPI endpoints
- Automated unit and integration testing
- Next.js market dashboard
- Candlestick charting
- Market controls
- Loading and recovery states

Realtime streaming and broader market coverage are the next major milestones.

---

## Disclaimer

KUNORA is currently a software development and market-analysis project.

It does not provide financial advice, investment recommendations, or guarantees regarding market performance.
