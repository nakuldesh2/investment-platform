import React, { useState } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, AlertCircle, Loader } from 'lucide-react';
import './StockSearch.css';

function StockSearch({ apiKeys, backendUrl, onStockSelect }) {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quoteData, setQuoteData] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setQuoteData(null);

    try {
      const response = await axios.get(`${backendUrl}/market-data/quote/${symbol.toUpperCase()}`, {
        headers: {
          'X-Alpha-Vantage-Key': apiKeys.alphaVantageKey,
          'Content-Type': 'application/json'
        }
      });

      setQuoteData(response.data);
      onStockSelect(symbol.toUpperCase());
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch stock data. Please check your API key and try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const isPositive = quoteData?.change_percent >= 0;

  return (
    <div className="stock-search">
      <div className="search-container">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)"
            className="search-input"
          />
          <button type="submit" className="search-btn" disabled={loading}>
            {loading ? <Loader className="spinner" size={18} /> : 'Search'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {quoteData && (
          <div className="quote-card">
            <div className="quote-header">
              <div className="quote-symbol">
                <h2>{quoteData.symbol}</h2>
              </div>
              <div className={`quote-price ${isPositive ? 'positive' : 'negative'}`}>
                <div className="price">${quoteData.price?.toFixed(2)}</div>
                <div className="change">
                  {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                  <span>{Math.abs(quoteData.change_percent || 0)?.toFixed(2)}%</span>
                </div>
              </div>
            </div>

            <div className="quote-details">
              <div className="detail-item">
                <span className="label">Previous Close</span>
                <span className="value">${quoteData.previous_close?.toFixed(2)}</span>
              </div>
              <div className="detail-item">
                <span className="label">Volume</span>
                <span className="value">{(quoteData.volume / 1000000)?.toFixed(2)}M</span>
              </div>
              <div className="detail-item">
                <span className="label">Data Source</span>
                <span className="value">{quoteData.source}</span>
              </div>
            </div>

            <div className="quote-footer">
              <p>Last updated: {new Date().toLocaleString()}</p>
            </div>
          </div>
        )}

        {!quoteData && !error && !loading && (
          <div className="empty-state">
            <p>Enter a stock symbol to get started</p>
            <small>Popular: AAPL, MSFT, GOOGL, TSLA, AMZN</small>
          </div>
        )}
      </div>
    </div>
  );
}

export default StockSearch;
