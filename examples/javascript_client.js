/**
 * Example JavaScript/Node.js client for Injective Market Analytics API
 * 
 * Install dependencies: npm install axios
 * Run: node javascript_client.js
 */

const axios = require('axios');

class InjectiveAPIClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.apiBase = `${baseUrl}/api/v1`;
  }

  async getHealth() {
    const response = await axios.get(`${this.baseUrl}/health`);
    return response.data;
  }

  async getMarkets(marketType = null) {
    const params = marketType ? { market_type: marketType } : {};
    const response = await axios.get(`${this.apiBase}/markets`, { params });
    return response.data;
  }

  async getMarketSummary(marketId) {
    const response = await axios.get(`${this.apiBase}/markets/${marketId}/summary`);
    return response.data;
  }

  async getOrderbook(marketId, depth = 20) {
    const response = await axios.get(`${this.apiBase}/markets/${marketId}/orderbook`, {
      params: { depth }
    });
    return response.data;
  }

  async getTrades(marketId, limit = 50) {
    const response = await axios.get(`${this.apiBase}/markets/${marketId}/trades`, {
      params: { limit }
    });
    return response.data;
  }

  async getMetrics(marketId) {
    const response = await axios.get(`${this.apiBase}/metrics/${marketId}`);
    return response.data;
  }

  async getTrendingMarkets(limit = 10) {
    const response = await axios.get(`${this.apiBase}/metrics/trending/markets`, {
      params: { limit }
    });
    return response.data;
  }

  async getSignals(marketId) {
    const response = await axios.get(`${this.apiBase}/metrics/${marketId}/signals`);
    return response.data;
  }

  async compareMarkets(marketIds) {
    const response = await axios.get(`${this.apiBase}/compare`, {
      params: { market_ids: marketIds }
    });
    return response.data;
  }
}

async function main() {
  const client = new InjectiveAPIClient();

  try {
    // Check API health
    console.log('=== API Health Check ===');
    const health = await client.getHealth();
    console.log(JSON.stringify(health, null, 2));
    console.log();

    // Get all markets
    console.log('=== Available Markets ===');
    const markets = await client.getMarkets();
    console.log(`Found ${markets.length} markets`);
    markets.slice(0, 5).forEach(market => {
      console.log(`  - ${market.ticker} (${market.type})`);
    });
    console.log();

    if (markets.length === 0) {
      console.log('No markets available. Make sure the API is connected to Injective network.');
      return;
    }

    const marketId = markets[0].market_id;
    const ticker = markets[0].ticker;

    // Get market summary
    console.log(`=== Market Summary: ${ticker} ===`);
    try {
      const summary = await client.getMarketSummary(marketId);
      console.log(JSON.stringify(summary, null, 2));
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
    console.log();

    // Get orderbook
    console.log(`=== Orderbook: ${ticker} (Top 5 levels) ===`);
    try {
      const orderbook = await client.getOrderbook(marketId, 5);
      console.log(`Bids: ${orderbook.bids.length} levels`);
      orderbook.bids.slice(0, 3).forEach(bid => {
        console.log(`  ${bid.price} @ ${bid.quantity}`);
      });
      console.log(`Asks: ${orderbook.asks.length} levels`);
      orderbook.asks.slice(0, 3).forEach(ask => {
        console.log(`  ${ask.price} @ ${ask.quantity}`);
      });
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
    console.log();

    // Get metrics
    console.log(`=== Market Metrics: ${ticker} ===`);
    try {
      const metrics = await client.getMetrics(marketId);
      console.log(JSON.stringify(metrics, null, 2));
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
    console.log();

    // Get trading signals
    console.log(`=== Trading Signals: ${ticker} ===`);
    try {
      const signals = await client.getSignals(marketId);
      console.log(`Signal: ${signals.signal.toUpperCase()}`);
      console.log(`Strength: ${signals.strength}/100`);
      console.log(`Indicators: ${JSON.stringify(signals.indicators, null, 2)}`);
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
    console.log();

    // Get trending markets
    console.log('=== Trending Markets ===');
    try {
      const trending = await client.getTrendingMarkets(5);
      trending.forEach(market => {
        console.log(
          `#${market.rank} ${market.ticker}: ` +
          `${market.price_change_24h > 0 ? '+' : ''}${market.price_change_24h.toFixed(2)}% | ` +
          `Vol: ${market.volume_24h.toFixed(2)}`
        );
      });
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
    console.log();

    // Compare markets
    if (markets.length >= 2) {
      console.log('=== Market Comparison ===');
      try {
        const marketIds = markets.slice(0, 3).map(m => m.market_id);
        const comparison = await client.compareMarkets(marketIds);
        console.log(`Best Performer: ${comparison.best_performer}`);
        console.log(`Worst Performer: ${comparison.worst_performer}`);
        console.log(`Average Volume: ${comparison.average_volume.toFixed(2)}`);
        console.log(`Average Price Change: ${comparison.average_price_change.toFixed(2)}%`);
      } catch (error) {
        console.log(`Error: ${error.message}`);
      }
    }

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = InjectiveAPIClient;
