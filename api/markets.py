"""
Market data endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import MarketInfo, MarketSummary, Orderbook, Trade
from services import injective_service

router = APIRouter()


@router.get("", response_model=List[MarketInfo])
async def list_markets(
    market_type: Optional[str] = Query(None, description="Filter by market type: spot or derivative")
):
    """
    List all available markets
    
    Returns a list of all spot and derivative markets on Injective.
    Optionally filter by market type.
    """
    markets = await injective_service.get_all_markets()
    
    if market_type:
        markets = [m for m in markets if m["type"] == market_type]
    
    return markets


@router.get("/{market_id}/summary", response_model=MarketSummary)
async def get_market_summary(market_id: str):
    """
    Get market summary
    
    Returns current price, 24h volume, and price change for a specific market.
    """
    summary = await injective_service.get_market_summary(market_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    return summary


@router.get("/{market_id}/orderbook", response_model=Orderbook)
async def get_orderbook(
    market_id: str,
    depth: int = Query(20, ge=1, le=100, description="Number of price levels to return")
):
    """
    Get current orderbook
    
    Returns the current bid and ask levels for a market.
    Default depth is 20 levels, maximum is 100.
    """
    orderbook = await injective_service.get_orderbook(market_id)
    
    if not orderbook:
        raise HTTPException(status_code=404, detail=f"Orderbook for market {market_id} not found")
    
    # Limit depth
    orderbook["bids"] = orderbook["bids"][:depth]
    orderbook["asks"] = orderbook["asks"][:depth]
    
    return orderbook


@router.get("/{market_id}/trades", response_model=List[Trade])
async def get_recent_trades(
    market_id: str,
    limit: int = Query(50, ge=1, le=500, description="Number of trades to return")
):
    """
    Get recent trades
    
    Returns the most recent trades for a market.
    Default limit is 50 trades, maximum is 500.
    """
    trades = await injective_service.get_recent_trades(market_id, limit)
    
    if not trades:
        # Return empty list instead of 404 for consistency
        return []
    
    return trades
