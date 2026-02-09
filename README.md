# 🥷 Injective Market Analytics API

A comprehensive, developer-friendly API for accessing and analyzing Injective blockchain market data. Built for the Ninja API Forge hackathon.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com)

## 🎯 Overview

This API provides real-time market data aggregation, derived trading metrics, and developer utilities for the Injective ecosystem. It abstracts the complexity of raw blockchain data into clean, easy-to-use REST endpoints.

### Key Features

- **📊 Market Data Aggregation** - Unified access to spot and derivative markets
- **📈 Derived Metrics** - Pre-calculated volatility, liquidity, and trading signals
- **⚡ Performance** - Built-in caching for fast responses
- **🔄 Real-time Data** - Direct integration with Injective network
- **📚 Auto-generated Docs** - Interactive OpenAPI/Swagger documentation
- **🐳 Docker Support** - One-command deployment
- **🎨 Developer-Friendly** - Clean endpoints with clear response schemas

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd ninjaapi

# Start the API
docker-compose up -d

# Access the API
open http://localhost:8000/docs
```

### Option 2: Local Python

```bash
# Clone and setup
git clone <your-repo-url>
cd ninjaapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the API
python main.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 🏥 Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health status and cache info |
| `/cache/clear` | POST | Clear cached data |

#### 📊 Market Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/markets` | GET | List all available markets |
| `/markets/{market_id}/summary` | GET | Market price, volume, 24h change |
| `/markets/{market_id}/orderbook` | GET | Current bid/ask levels |
| `/markets/{market_id}/trades` | GET | Recent trades history |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/markets
```

**Example Response:**
```json
[
  {
    "market_id": "0x123...",
    "ticker": "INJ/USDT",
    "base_denom": "inj",
    "quote_denom": "usdt",
    "type": "spot"
  }
]
```

#### 📈 Metrics & Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics/{market_id}` | GET | Volatility, spread, liquidity scores |
| `/metrics/trending/markets` | GET | Top markets by volume/change |
| `/metrics/{market_id}/signals` | GET | Buy/sell/hold signals |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/metrics/{market_id}
```

**Example Response:**
```json
{
  "market_id": "0x123...",
  "ticker": "INJ/USDT",
  "volatility": 0.0234,
  "spread_percentage": 0.15,
  "liquidity_score": 85.5,
  "volume_trend": "increasing",
  "price_momentum": "bullish",
  "timestamp": "2026-02-10T12:00:00"
}
```

#### 🔄 Multi-Market Comparison

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/compare` | GET | Compare multiple markets side-by-side |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/compare?market_ids=market1&market_ids=market2"
```

## 🛠️ Technical Architecture

### Tech Stack

- **Framework**: FastAPI (high-performance async Python framework)
- **Blockchain SDK**: injective-py (official Injective Python SDK)
- **Caching**: TTLCache (in-memory caching for performance)
- **Validation**: Pydantic (data validation and serialization)
- **Container**: Docker & Docker Compose

### Project Structure

```
ninjaapi/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container orchestration
│
├── api/                  # API endpoint modules
│   ├── health.py        # Health check endpoints
│   ├── markets.py       # Market data endpoints
│   ├── metrics.py       # Analytics endpoints
│   └── compare.py       # Comparison endpoints
│
├── services/            # Business logic layer
│   ├── __init__.py
│   └── injective_client.py  # Injective blockchain client
│
└── examples/            # Example client scripts
    ├── python_client.py
    └── javascript_client.js
```

### Key Design Decisions

1. **Separation of Concerns**: Clean separation between API routes, business logic, and data access
2. **Caching Strategy**: TTL-based caching reduces blockchain queries while maintaining fresh data
3. **Async Architecture**: Fully async implementation for maximum throughput
4. **Type Safety**: Pydantic models ensure data validation and clear contracts
5. **Auto Documentation**: OpenAPI schema automatically generated from code

## 📊 Data Sources

This API uses official Injective data sources:

- **Derivative Markets**: Perpetual and futures contract data
- **Spot Markets**: Token pair trading data
- **Orderbooks**: Real-time bid/ask depth
- **Trade History**: Executed trades with timestamps
- **Oracle Data**: Price feed information

## 🎨 Developer Experience Features

### 1. Interactive Documentation

Visit `/docs` for Swagger UI where you can:
- Explore all endpoints
- Try requests directly in browser
- See request/response schemas
- Copy curl commands

### 2. Type-Safe Responses

All responses follow consistent Pydantic models with:
- Clear field descriptions
- Type annotations
- Validation rules
- Example values

### 3. Error Handling

Consistent error responses with:
- HTTP status codes
- Detailed error messages
- Request context

### 4. Performance Optimization

- Built-in caching (default 60s TTL)
- Async/await throughout
- Connection pooling
- Batch operations where possible

## 🔧 Configuration

Edit `.env` file to customize:

```bash
# Network selection
NETWORK=testnet  # or mainnet

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# Cache settings
CACHE_TTL_SECONDS=60
MAX_CACHE_SIZE=1000

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

## 📝 Example Usage

### Python Client

```python
import requests

# Get all markets
response = requests.get("http://localhost:8000/api/v1/markets")
markets = response.json()

# Get specific market metrics
market_id = markets[0]["market_id"]
metrics = requests.get(f"http://localhost:8000/api/v1/metrics/{market_id}")
print(metrics.json())
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

// Get trending markets
const response = await axios.get('http://localhost:8000/api/v1/metrics/trending/markets');
console.log(response.data);

// Compare markets
const comparison = await axios.get('http://localhost:8000/api/v1/compare', {
  params: { market_ids: ['market1', 'market2'] }
});
console.log(comparison.data);
```

### cURL Examples

```bash
# List all markets
curl http://localhost:8000/api/v1/markets

# Get market summary
curl http://localhost:8000/api/v1/markets/{market_id}/summary

# Get orderbook
curl http://localhost:8000/api/v1/markets/{market_id}/orderbook?depth=10

# Get trading signals
curl http://localhost:8000/api/v1/metrics/{market_id}/signals

# Compare markets
curl "http://localhost:8000/api/v1/compare?market_ids=market1&market_ids=market2"

# Check health
curl http://localhost:8000/health
```

## 🧪 Testing

### Test the API is running:
```bash
curl http://localhost:8000/health
```

### Test market endpoints:
```bash
# List markets
curl http://localhost:8000/api/v1/markets | jq

# Get first market ID and query it
MARKET_ID=$(curl -s http://localhost:8000/api/v1/markets | jq -r '.[0].market_id')
curl http://localhost:8000/api/v1/markets/$MARKET_ID/summary | jq
```

## 🚀 Deployment

### Docker Production Deployment

```bash
# Build production image
docker build -t injective-api:latest .

# Run in production mode
docker run -d \
  -p 8000:8000 \
  -e NETWORK=mainnet \
  --name injective-api \
  injective-api:latest
```

### Cloud Deployment

This API can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Heroku Container Registry

## 🎯 Use Cases

This API is perfect for:

1. **Trading Dashboards** - Display real-time market data and metrics
2. **Trading Bots** - Access signals and orderbook data for automated trading
3. **Analytics Tools** - Build market analysis and visualization tools
4. **Mobile Apps** - Lightweight API for mobile Injective applications
5. **Research Platforms** - Historical data and metric analysis
6. **Portfolio Trackers** - Monitor multiple markets simultaneously

## 🤝 Contributing

Contributions are welcome! This project is built for the developer community.

## 📄 License

MIT License - feel free to use this in your own projects.

## 🏆 Hackathon Submission

**Event**: Ninja API Forge (Jan 28 - Feb 15, 2026)

**What This API Offers**:
- Clean, RESTful endpoints following best practices
- Comprehensive market data coverage (spot + derivatives)
- Value-added metrics (volatility, liquidity, signals)
- Production-ready code with proper error handling
- Developer experience focused (docs, examples, Docker)
- Extensible architecture for future enhancements

**Why Developers Will Love It**:
- Saves hours of integration work
- No need to understand complex blockchain queries
- Consistent, predictable responses
- Ready to use in production
- One command to run locally

## 📞 Contact

For questions about this API or the Ninja API Forge hackathon:
- Twitter: [@injective](https://twitter.com/injective) [@NinjaLabsHQ](https://twitter.com/NinjaLabsHQ)

---

Built with ❤️ for the Injective ecosystem
