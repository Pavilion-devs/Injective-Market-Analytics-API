#!/usr/bin/env python3
"""
Example Python client for Injective Market Analytics API

This script demonstrates how to use the API endpoints.
"""
import requests
from typing import List, Dict, Any
import json


class InjectiveAPIClient:
    """Simple client for the Injective Market Analytics API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def get_health(self) -> Dict[str, Any]:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_markets(self, market_type: str = None) -> List[Dict[str, Any]]:
        """Get all markets, optionally filtered by type"""
        params = {"market_type": market_type} if market_type else {}
        response = requests.get(f"{self.api_base}/markets", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_market_summary(self, market_id: str) -> Dict[str, Any]:
        """Get summary for a specific market"""
        response = requests.get(f"{self.api_base}/markets/{market_id}/summary")
        response.raise_for_status()
        return response.json()
    
    def get_orderbook(self, market_id: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook for a market"""
        response = requests.get(
            f"{self.api_base}/markets/{market_id}/orderbook",
            params={"depth": depth}
        )
        response.raise_for_status()
        return response.json()
    
    def get_trades(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades for a market"""
        response = requests.get(
            f"{self.api_base}/markets/{market_id}/trades",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self, market_id: str) -> Dict[str, Any]:
        """Get derived metrics for a market"""
        response = requests.get(f"{self.api_base}/metrics/{market_id}")
        response.raise_for_status()
        return response.json()
    
    def get_trending_markets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending markets"""
        response = requests.get(
            f"{self.api_base}/metrics/trending/markets",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_signals(self, market_id: str) -> Dict[str, Any]:
        """Get trading signals for a market"""
        response = requests.get(f"{self.api_base}/metrics/{market_id}/signals")
        response.raise_for_status()
        return response.json()
    
    def compare_markets(self, market_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple markets"""
        response = requests.get(
            f"{self.api_base}/compare",
            params={"market_ids": market_ids}
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the API client"""
    
    # Initialize client
    client = InjectiveAPIClient()
    
    # Check API health
    print("=== API Health Check ===")
    health = client.get_health()
    print(json.dumps(health, indent=2))
    print()
    
    # Get all markets
    print("=== Available Markets ===")
    markets = client.get_markets()
    print(f"Found {len(markets)} markets")
    for market in markets[:5]:  # Show first 5
        print(f"  - {market['ticker']} ({market['type']})")
    print()
    
    if not markets:
        print("No markets available. Make sure the API is connected to Injective network.")
        return
    
    # Get market summary
    market_id = markets[0]['market_id']
    print(f"=== Market Summary: {markets[0]['ticker']} ===")
    try:
        summary = client.get_market_summary(market_id)
        print(json.dumps(summary, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Get orderbook
    print(f"=== Orderbook: {markets[0]['ticker']} (Top 5 levels) ===")
    try:
        orderbook = client.get_orderbook(market_id, depth=5)
        print(f"Bids: {len(orderbook['bids'])} levels")
        for bid in orderbook['bids'][:3]:
            print(f"  {bid['price']} @ {bid['quantity']}")
        print(f"Asks: {len(orderbook['asks'])} levels")
        for ask in orderbook['asks'][:3]:
            print(f"  {ask['price']} @ {ask['quantity']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Get metrics
    print(f"=== Market Metrics: {markets[0]['ticker']} ===")
    try:
        metrics = client.get_metrics(market_id)
        print(json.dumps(metrics, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Get trading signals
    print(f"=== Trading Signals: {markets[0]['ticker']} ===")
    try:
        signals = client.get_signals(market_id)
        print(f"Signal: {signals['signal'].upper()}")
        print(f"Strength: {signals['strength']}/100")
        print(f"Indicators: {json.dumps(signals['indicators'], indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Get trending markets
    print("=== Trending Markets ===")
    try:
        trending = client.get_trending_markets(limit=5)
        for market in trending:
            print(f"#{market['rank']} {market['ticker']}: "
                  f"{market['price_change_24h']:+.2f}% | "
                  f"Vol: {market['volume_24h']:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Compare markets
    if len(markets) >= 2:
        print("=== Market Comparison ===")
        try:
            market_ids = [m['market_id'] for m in markets[:3]]
            comparison = client.compare_markets(market_ids)
            print(f"Best Performer: {comparison['best_performer']}")
            print(f"Worst Performer: {comparison['worst_performer']}")
            print(f"Average Volume: {comparison['average_volume']:.2f}")
            print(f"Average Price Change: {comparison['average_price_change']:.2f}%")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
