"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class MarketInfo(BaseModel):
    """Basic market information"""
    market_id: str
    ticker: str
    base_denom: str
    quote_denom: str
    type: Literal["spot", "derivative"]
    oracle_base: Optional[str] = None
    oracle_quote: Optional[str] = None
    oracle_type: Optional[str] = None


class MarketSummary(BaseModel):
    """Market summary with price and volume"""
    market_id: str
    ticker: str
    type: Literal["spot", "derivative"]
    last_price: float
    volume_24h: float
    price_change_24h: float
    timestamp: str


class OrderbookLevel(BaseModel):
    """Single orderbook level"""
    price: float
    quantity: float


class Orderbook(BaseModel):
    """Orderbook data"""
    market_id: str
    type: Literal["spot", "derivative"]
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    timestamp: str


class Trade(BaseModel):
    """Trade data"""
    price: float
    quantity: float
    timestamp: Optional[str]
    side: str


class MarketMetrics(BaseModel):
    """Derived market metrics"""
    market_id: str
    ticker: str
    volatility: float = Field(description="Price volatility (standard deviation)")
    spread_percentage: float = Field(description="Bid-ask spread as percentage")
    liquidity_score: float = Field(description="Liquidity depth score (0-100)")
    volume_trend: str = Field(description="Volume trend: increasing, decreasing, stable")
    price_momentum: str = Field(description="Price momentum: bullish, bearish, neutral")
    timestamp: str


class TrendingMarket(BaseModel):
    """Trending market information"""
    market_id: str
    ticker: str
    type: Literal["spot", "derivative"]
    price_change_24h: float
    volume_24h: float
    rank: int


class MarketSignal(BaseModel):
    """Trading signal for a market"""
    market_id: str
    ticker: str
    signal: Literal["buy", "sell", "hold"]
    strength: float = Field(ge=0, le=100, description="Signal strength (0-100)")
    indicators: dict = Field(description="Individual indicator values")
    timestamp: str


class MarketComparison(BaseModel):
    """Comparison between multiple markets"""
    markets: List[str]
    best_performer: str
    worst_performer: str
    average_volume: float
    average_price_change: float
    data: List[MarketSummary]
    timestamp: str


class HealthStatus(BaseModel):
    """API health status"""
    status: str
    version: str
    network: str
    timestamp: str
    cache_size: int
