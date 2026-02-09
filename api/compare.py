"""
Multi-market comparison endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import MarketComparison, MarketSummary
from services import injective_service

router = APIRouter()


@router.get("", response_model=MarketComparison)
async def compare_markets(
    market_ids: List[str] = Query(..., description="List of market IDs to compare")
):
    """
    Compare multiple markets
    
    Returns comparative analysis of multiple markets including:
    - Best and worst performers
    - Average volume and price changes
    - Individual market summaries
    
    Example: /api/v1/compare?market_ids=market1&market_ids=market2&market_ids=market3
    """
    if len(market_ids) < 2:
        raise HTTPException(
            status_code=400, 
            detail="At least 2 market IDs required for comparison"
        )
    
    if len(market_ids) > 10:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 10 markets can be compared at once"
        )
    
    # Fetch summaries for all markets
    summaries = []
    for market_id in market_ids:
        try:
            summary = await injective_service.get_market_summary(market_id)
            if summary:
                summaries.append(MarketSummary(**summary))
        except:
            continue
    
    if not summaries:
        raise HTTPException(
            status_code=404, 
            detail="No valid markets found"
        )
    
    # Find best and worst performers
    best = max(summaries, key=lambda x: x.price_change_24h)
    worst = min(summaries, key=lambda x: x.price_change_24h)
    
    # Calculate averages
    avg_volume = sum(s.volume_24h for s in summaries) / len(summaries)
    avg_price_change = sum(s.price_change_24h for s in summaries) / len(summaries)
    
    return MarketComparison(
        markets=market_ids,
        best_performer=f"{best.ticker} ({best.price_change_24h:+.2f}%)",
        worst_performer=f"{worst.ticker} ({worst.price_change_24h:+.2f}%)",
        average_volume=round(avg_volume, 2),
        average_price_change=round(avg_price_change, 2),
        data=summaries,
        timestamp=datetime.utcnow().isoformat(),
    )
