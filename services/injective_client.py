"""
Injective blockchain client service
Handles all interactions with Injective network
"""
from typing import List, Dict, Any, Optional
from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network
from config import settings
from cachetools import TTLCache
from datetime import datetime
import asyncio


class InjectiveService:
    """Service for interacting with Injective blockchain"""
    
    def __init__(self):
        self.network = Network.testnet() if settings.network == "testnet" else Network.mainnet()
        self.client: Optional[AsyncClient] = None
        self._cache = TTLCache(maxsize=settings.max_cache_size, ttl=settings.cache_ttl_seconds)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Injective client"""
        if not self._initialized:
            self.client = AsyncClient(self.network)
            self._initialized = True
    
    async def ensure_initialized(self):
        """Ensure client is initialized before use"""
        if not self._initialized:
            await self.initialize()
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        return f"{prefix}:{'_'.join(map(str, args))}"
    
    def _parse_price(self, price_str: str, decimals: int = 6) -> float:
        """Parse price string to float - Injective typically uses 6 decimals for prices"""
        try:
            return float(price_str) / (10 ** decimals)
        except:
            return 0.0
    
    def _parse_quantity(self, quantity_str: str, decimals: int = 18) -> float:
        """Parse quantity string to float - Injective typically uses 18 decimals for quantities"""
        try:
            return float(quantity_str) / (10 ** decimals)
        except:
            return 0.0
    
    async def get_all_markets(self) -> List[Dict[str, Any]]:
        """Get all derivative and spot markets"""
        await self.ensure_initialized()
        
        cache_key = self._get_cache_key("all_markets")
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            markets = []
            
            # Get derivative markets
            try:
                derivative_result = await self.client.fetch_chain_derivative_markets()
                if 'markets' in derivative_result:
                    for item in derivative_result['markets']:
                        if 'market' in item:
                            market = item['market']
                            markets.append({
                                "market_id": market.get('marketId', ''),
                                "ticker": market.get('ticker', ''),
                                "base_denom": market.get('quoteDenom', ''),
                                "quote_denom": market.get('quoteDenom', ''),
                                "type": "derivative",
                                "oracle_base": market.get('oracleBase', ''),
                                "oracle_quote": market.get('oracleQuote', ''),
                                "oracle_type": market.get('oracleType', ''),
                            })
            except Exception as e:
                print(f"Error fetching derivative markets: {e}")
            
            # Get spot markets
            try:
                spot_result = await self.client.fetch_chain_spot_markets()
                if 'markets' in spot_result:
                    for item in spot_result['markets']:
                        if 'market' in item:
                            market = item['market']
                            markets.append({
                                "market_id": market.get('marketId', ''),
                                "ticker": market.get('ticker', ''),
                                "base_denom": market.get('baseDenom', ''),
                                "quote_denom": market.get('quoteDenom', ''),
                                "type": "spot",
                            })
            except Exception as e:
                print(f"Error fetching spot markets: {e}")
            
            self._cache[cache_key] = markets
            return markets
        
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    async def get_market_summary(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market summary with price, volume, and 24h change"""
        await self.ensure_initialized()
        
        cache_key = self._get_cache_key("market_summary", market_id)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Try derivative market first
            try:
                result = await self.client.fetch_derivative_market(market_id=market_id)
                if 'market' in result:
                    market_data = result['market']
                    
                    # Get mark price if available
                    mark_price = 0.0
                    if 'markPrice' in result:
                        mark_price = self._parse_price(result['markPrice'])
                    
                    # Get mid price from TOB if available
                    mid_price = mark_price
                    if 'midPriceAndTob' in result and 'midPrice' in result['midPriceAndTob']:
                        mid_price = self._parse_price(result['midPriceAndTob']['midPrice'])
                    
                    summary = {
                        "market_id": market_id,
                        "ticker": market_data.get('ticker', ''),
                        "type": "derivative",
                        "last_price": mid_price,
                        "volume_24h": 0,  # Need to fetch from trades
                        "price_change_24h": 0,  # Would need historical data
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    self._cache[cache_key] = summary
                    return summary
            except Exception as e:
                print(f"Derivative market error: {e}")
            
            # Try spot market
            try:
                result = await self.client.fetch_spot_market(market_id=market_id)
                if 'market' in result:
                    market_data = result['market']
                    
                    # Get mid price from TOB if available
                    mid_price = 0.0
                    if 'midPriceAndTob' in result and 'midPrice' in result['midPriceAndTob']:
                        mid_price = self._parse_price(result['midPriceAndTob']['midPrice'])
                    
                    summary = {
                        "market_id": market_id,
                        "ticker": market_data.get('ticker', ''),
                        "type": "spot",
                        "last_price": mid_price,
                        "volume_24h": 0,  # Need to fetch from trades
                        "price_change_24h": 0,  # Would need historical data
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    self._cache[cache_key] = summary
                    return summary
            except Exception as e:
                print(f"Spot market error: {e}")
            
            return None
        
        except Exception as e:
            print(f"Error fetching market summary: {e}")
            return None
    
    async def get_orderbook(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get current orderbook for a market"""
        await self.ensure_initialized()
        
        cache_key = self._get_cache_key("orderbook", market_id)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Try derivative orderbook
            try:
                result = await self.client.fetch_derivative_orderbook_v2(market_id=market_id)
                if 'orderbook' in result:
                    ob = result['orderbook']
                    
                    bids = []
                    for bid in ob.get('buys', [])[:100]:
                        bids.append({
                            "price": self._parse_price(bid.get('price', '0')),
                            "quantity": self._parse_quantity(bid.get('quantity', '0'))
                        })
                    
                    asks = []
                    for ask in ob.get('sells', [])[:100]:
                        asks.append({
                            "price": self._parse_price(ask.get('price', '0')),
                            "quantity": self._parse_quantity(ask.get('quantity', '0'))
                        })
                    
                    orderbook_data = {
                        "market_id": market_id,
                        "type": "derivative",
                        "bids": bids,
                        "asks": asks,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    self._cache[cache_key] = orderbook_data
                    return orderbook_data
            except Exception as e:
                print(f"Derivative orderbook error: {e}")
            
            # Try spot orderbook
            try:
                result = await self.client.fetch_spot_orderbook_v2(market_id=market_id)
                if 'orderbook' in result:
                    ob = result['orderbook']
                    
                    bids = []
                    for bid in ob.get('buys', [])[:100]:
                        bids.append({
                            "price": self._parse_price(bid.get('price', '0')),
                            "quantity": self._parse_quantity(bid.get('quantity', '0'))
                        })
                    
                    asks = []
                    for ask in ob.get('sells', [])[:100]:
                        asks.append({
                            "price": self._parse_price(ask.get('price', '0')),
                            "quantity": self._parse_quantity(ask.get('quantity', '0'))
                        })
                    
                    orderbook_data = {
                        "market_id": market_id,
                        "type": "spot",
                        "bids": bids,
                        "asks": asks,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    self._cache[cache_key] = orderbook_data
                    return orderbook_data
            except Exception as e:
                print(f"Spot orderbook error: {e}")
            
            return None
        
        except Exception as e:
            print(f"Error fetching orderbook: {e}")
            return None
    
    async def get_recent_trades(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades for a market"""
        await self.ensure_initialized()
        
        cache_key = self._get_cache_key("trades", market_id, limit)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            trades = []
            
            # Try derivative trades
            try:
                result = await self.client.fetch_derivative_trades(market_ids=[market_id])
                if 'trades' in result:
                    for trade in result['trades'][:limit]:
                        # Extract price from positionDelta
                        price = 0.0
                        quantity = 0.0
                        if 'positionDelta' in trade:
                            delta = trade['positionDelta']
                            if 'executionPrice' in delta:
                                price = self._parse_price(delta['executionPrice'])
                            if 'executionQuantity' in delta:
                                quantity = self._parse_quantity(delta['executionQuantity'])
                        
                        trades.append({
                            "price": price,
                            "quantity": quantity,
                            "timestamp": str(trade.get('executedAt', '')),
                            "side": trade.get('executionSide', 'unknown'),
                        })
            except Exception as e:
                print(f"Derivative trades error: {e}")
            
            # Try spot trades if no derivative trades
            if not trades:
                try:
                    result = await self.client.fetch_spot_trades(market_ids=[market_id])
                    if 'trades' in result:
                        for trade in result['trades'][:limit]:
                            price = self._parse_price(trade.get('price', {}).get('price', '0'))
                            quantity = self._parse_quantity(trade.get('price', {}).get('quantity', '0'))
                            
                            trades.append({
                                "price": price,
                                "quantity": quantity,
                                "timestamp": str(trade.get('executedAt', '')),
                                "side": trade.get('tradeDirection', 'unknown'),
                            })
                except Exception as e:
                    print(f"Spot trades error: {e}")
            
            self._cache[cache_key] = trades
            return trades
        
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return []
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()


# Global service instance
injective_service = InjectiveService()
