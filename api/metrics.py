"""
Market metrics and analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import MarketMetrics, TrendingMarket, MarketSignal
from services import injective_service
import statistics

router = APIRouter()


async def calculate_volatility(trades: List[dict]) -> float:
    """Calculate price volatility from recent trades"""
    if len(trades) < 2:
        return 0.0
    
    prices = [trade["price"] for trade in trades if trade["price"] > 0]
    if len(prices) < 2:
        return 0.0
    
    try:
        return statistics.stdev(prices)
    except:
        return 0.0


async def calculate_spread(orderbook: dict) -> float:
    """Calculate bid-ask spread percentage"""
    if not orderbook or not orderbook.get("bids") or not orderbook.get("asks"):
        return 0.0
    
    try:
        best_bid = orderbook["bids"][0]["price"]
        best_ask = orderbook["asks"][0]["price"]
        
        if best_bid <= 0 or best_ask <= 0:
            return 0.0
        
        spread = ((best_ask - best_bid) / best_ask) * 100
        return round(spread, 4)
    except:
        return 0.0


async def calculate_liquidity_score(orderbook: dict) -> float:
    """Calculate liquidity score based on orderbook depth"""
    if not orderbook:
        return 0.0
    
    try:
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        
        # Calculate total volume in top 10 levels
        bid_volume = sum(level["quantity"] for level in bids[:10])
        ask_volume = sum(level["quantity"] for level in asks[:10])
        total_volume = bid_volume + ask_volume
        
        # Normalize to 0-100 scale (arbitrary scaling)
        score = min(total_volume / 1000, 100)
        return round(score, 2)
    except:
        return 0.0


@router.get("/{market_id}", response_model=MarketMetrics)
async def get_market_metrics(market_id: str):
    """
    Get derived market metrics
    
    Returns calculated metrics including volatility, spread, liquidity score,
    and trading signals for a specific market.
    """
    # Fetch data
    summary = await injective_service.get_market_summary(market_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    orderbook = await injective_service.get_orderbook(market_id)
    trades = await injective_service.get_recent_trades(market_id, 100)
    
    # Calculate metrics
    volatility = await calculate_volatility(trades)
    spread = await calculate_spread(orderbook) if orderbook else 0.0
    liquidity = await calculate_liquidity_score(orderbook) if orderbook else 0.0
    
    # Determine trends
    volume_trend = "stable"
    if summary["volume_24h"] > 1000000:
        volume_trend = "increasing"
    elif summary["volume_24h"] < 100000:
        volume_trend = "decreasing"
    
    price_momentum = "neutral"
    if summary["price_change_24h"] > 5:
        price_momentum = "bullish"
    elif summary["price_change_24h"] < -5:
        price_momentum = "bearish"
    
    return MarketMetrics(
        market_id=market_id,
        ticker=summary["ticker"],
        volatility=round(volatility, 4),
        spread_percentage=spread,
        liquidity_score=liquidity,
        volume_trend=volume_trend,
        price_momentum=price_momentum,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/trending/markets", response_model=List[TrendingMarket])
async def get_trending_markets(
    limit: int = Query(10, ge=1, le=50, description="Number of markets to return")
):
    """
    Get trending markets
    
    Returns top markets sorted by volume and price change.
    Useful for discovering active trading opportunities.
    """
    markets = await injective_service.get_all_markets()
    
    trending = []
    for market in markets[:50]:  # Limit API calls
        try:
            summary = await injective_service.get_market_summary(market["market_id"])
            if summary and summary["volume_24h"] > 0:
                trending.append(TrendingMarket(
                    market_id=market["market_id"],
                    ticker=market["ticker"],
                    type=market["type"],
                    price_change_24h=summary["price_change_24h"],
                    volume_24h=summary["volume_24h"],
                    rank=0,
                ))
        except:
            continue
    
    # Sort by volume
    trending.sort(key=lambda x: x.volume_24h, reverse=True)
    
    # Assign ranks
    for i, market in enumerate(trending[:limit]):
        market.rank = i + 1
    
    return trending[:limit]


@router.get("/{market_id}/signals", response_model=MarketSignal)
async def get_market_signals(market_id: str):
    """
    Get trading signals
    
    Returns simple buy/sell/hold signals based on technical indicators.
    This is for informational purposes only and not financial advice.
    """
    summary = await injective_service.get_market_summary(market_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    orderbook = await injective_service.get_orderbook(market_id)
    trades = await injective_service.get_recent_trades(market_id, 100)
    
    # Simple signal calculation
    indicators = {
        "price_change_24h": summary["price_change_24h"],
        "volume_24h": summary["volume_24h"],
        "spread": await calculate_spread(orderbook) if orderbook else 0.0,
        "volatility": await calculate_volatility(trades),
    }
    
    # Determine signal
    signal = "hold"
    strength = 50.0
    
    if indicators["price_change_24h"] > 10 and indicators["volume_24h"] > 500000:
        signal = "buy"
        strength = min(70 + indicators["price_change_24h"], 100)
    elif indicators["price_change_24h"] < -10 and indicators["volume_24h"] > 500000:
        signal = "sell"
        strength = min(70 + abs(indicators["price_change_24h"]), 100)
    
    return MarketSignal(
        market_id=market_id,
        ticker=summary["ticker"],
        signal=signal,
        strength=round(strength, 2),
        indicators=indicators,
        timestamp=datetime.utcnow().isoformat(),
    )
