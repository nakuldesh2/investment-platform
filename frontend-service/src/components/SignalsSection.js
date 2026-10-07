import React, { useState } from 'react';
import axios from 'axios';
import { AlertCircle, Loader, TrendingUp, TrendingDown } from 'lucide-react';
import './SignalsSection.css';

function SignalsSection({ apiKeys, backendUrl, selectedStock }) {
  const [symbol, setSymbol] = useState(selectedStock || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [signal, setSignal] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setSignal(null);

    try {
      const response = await axios.post(`${backendUrl}/signals/${symbol.toUpperCase()}`, {}, {
        headers: {
          'X-Alpha-Vantage-Key': apiKeys.alphaVantageKey,
          'Content-Type': 'application/json'
        }
      });

      setSignal(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate signal. Please try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSignalColor = (sig) => {
    if (sig === 'BUY') return 'buy';
    if (sig === 'SELL') return 'sell';
    return 'hold';
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 75) return 'high';
    if (confidence >= 50) return 'medium';
    return 'low';
  };

  return (
    <div className="signals-section">
      <div className="signals-header">
        <form onSubmit={handleSearch} className="signals-search-form">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol for AI signal"
            className="signals-search-input"
          />
          <button type="submit" className="signals-search-btn" disabled={loading}>
            {loading ? <Loader className="spinner" size={18} /> : 'Generate Signal'}
          </button>
        </form>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          <Loader className="spinner" size={32} />
          <p>Analyzing market data and generating signal...</p>
        </div>
      )}

      {signal && (
        <div className="signal-card">
          <div className={`signal-result ${getSignalColor(signal.signal)}`}>
            <div className="signal-main">
              <h2>{signal.symbol}</h2>
              <div className="signal-badge">
                {signal.signal === 'BUY' && <TrendingUp size={24} />}
                {signal.signal === 'SELL' && <TrendingDown size={24} />}
                <span className="signal-text">{signal.signal}</span>
              </div>
            </div>

            <div className={`confidence-meter ${getConfidenceClass(signal.confidence)}`}>
              <div className="confidence-label">Confidence</div>
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${signal.confidence}%` }}
                ></div>
              </div>
              <div className="confidence-value">{signal.confidence}%</div>
            </div>
          </div>

          <div className="technical-indicators">
            <h3>Technical Indicators</h3>
            <div className="indicators-grid">
              {signal.technical_indicators?.rsi !== undefined && (
                <div className="indicator">
                  <span className="indicator-label">RSI</span>
                  <span className="indicator-value">{signal.technical_indicators.rsi?.toFixed(2)}</span>
                </div>
              )}
              {signal.technical_indicators?.macd !== undefined && (
                <div className="indicator">
                  <span className="indicator-label">MACD</span>
                  <span className="indicator-value">{signal.technical_indicators.macd?.toFixed(2)}</span>
                </div>
              )}
              {signal.technical_indicators?.sma_50 !== undefined && (
                <div className="indicator">
                  <span className="indicator-label">SMA 50</span>
                  <span className="indicator-value">${signal.technical_indicators.sma_50?.toFixed(2)}</span>
                </div>
              )}
              {signal.technical_indicators?.sma_200 !== undefined && (
                <div className="indicator">
                  <span className="indicator-label">SMA 200</span>
                  <span className="indicator-value">${signal.technical_indicators.sma_200?.toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>

          {signal.risk_score !== undefined && (
            <div className="risk-assessment">
              <h3>Risk Score</h3>
              <div className="risk-meter">
                <div className="risk-bar">
                  <div
                    className="risk-fill"
                    style={{ width: `${signal.risk_score}%` }}
                  ></div>
                </div>
                <span className="risk-value">{signal.risk_score}/100</span>
              </div>
              <small>{signal.risk_score < 33 ? 'Low Risk' : signal.risk_score < 66 ? 'Medium Risk' : 'High Risk'}</small>
            </div>
          )}

          <div className="signal-footer">
            <p>Generated: {new Date(signal.generated_at).toLocaleString()}</p>
            <p className="disclaimer">⚠️ For educational purposes. Not financial advice.</p>
          </div>
        </div>
      )}

      {!signal && !error && !loading && (
        <div className="empty-state">
          <p>Enter a stock symbol to generate AI trading signals</p>
          <small>Uses machine learning to analyze market data and technical indicators</small>
        </div>
      )}
    </div>
  );
}

export default SignalsSection;
