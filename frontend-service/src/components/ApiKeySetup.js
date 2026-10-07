import React, { useState } from 'react';
import { AlertCircle, ExternalLink } from 'lucide-react';
import './ApiKeySetup.css';

function ApiKeySetup({ onSubmit }) {
  const [formData, setFormData] = useState({
    alphaVantageKey: '',
    newsApiKey: '',
    finnhubKey: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.alphaVantageKey.trim()) {
      newErrors.alphaVantageKey = 'Alpha Vantage API key is required';
    }
    if (!formData.newsApiKey.trim()) {
      newErrors.newsApiKey = 'NewsAPI key is required';
    }
    if (!formData.finnhubKey.trim()) {
      newErrors.finnhubKey = 'Finnhub API key is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit({
        alphaVantageKey: formData.alphaVantageKey,
        newsApiKey: formData.newsApiKey,
        finnhubKey: formData.finnhubKey
      });
    }
  };

  return (
    <div className="api-key-setup">
      <div className="setup-container">
        <div className="setup-header">
          <h1>Investment Platform</h1>
          <p>Real-time Market Data, News & AI Trading Signals</p>
        </div>

        <div className="setup-content">
          <div className="info-box">
            <AlertCircle size={20} />
            <p>Your API keys are stored only in your browser. We don't store or access any of your data.</p>
          </div>

          <form onSubmit={handleSubmit} className="api-key-form">
            <div className="form-section">
              <h2>Step 1: Get Your API Keys</h2>
              <p>Sign up for free accounts and get your API keys:</p>
            </div>

            <div className="form-group">
              <label htmlFor="alphaVantageKey">
                <span>Alpha Vantage API Key</span>
                <a href="https://www.alphavantage.co/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="alphaVantageKey"
                type="password"
                name="alphaVantageKey"
                value={formData.alphaVantageKey}
                onChange={handleChange}
                placeholder="Enter your Alpha Vantage API key"
                className={errors.alphaVantageKey ? 'error' : ''}
              />
              {errors.alphaVantageKey && <span className="error-text">{errors.alphaVantageKey}</span>}
              <small>Used for real-time stock quotes and market data</small>
            </div>

            <div className="form-group">
              <label htmlFor="newsApiKey">
                <span>NewsAPI Key</span>
                <a href="https://newsapi.org/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="newsApiKey"
                type="password"
                name="newsApiKey"
                value={formData.newsApiKey}
                onChange={handleChange}
                placeholder="Enter your NewsAPI key"
                className={errors.newsApiKey ? 'error' : ''}
              />
              {errors.newsApiKey && <span className="error-text">{errors.newsApiKey}</span>}
              <small>Used for financial news and market updates</small>
            </div>

            <div className="form-group">
              <label htmlFor="finnhubKey">
                <span>Finnhub API Key</span>
                <a href="https://finnhub.io/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="finnhubKey"
                type="password"
                name="finnhubKey"
                value={formData.finnhubKey}
                onChange={handleChange}
                placeholder="Enter your Finnhub API key"
                className={errors.finnhubKey ? 'error' : ''}
              />
              {errors.finnhubKey && <span className="error-text">{errors.finnhubKey}</span>}
              <small>Used for company data and fundamentals</small>
            </div>

            <button type="submit" className="submit-btn">
              Continue to Dashboard
            </button>
          </form>

          <div className="features-section">
            <h3>What You Can Do:</h3>
            <ul>
              <li>📊 Real-time stock quotes and market data</li>
              <li>📰 Latest financial news and sentiment analysis</li>
              <li>🤖 AI-powered trading signals and recommendations</li>
              <li>💼 Portfolio tracking and analysis</li>
              <li>📈 Technical indicators and charts</li>
            </ul>
          </div>

          <div className="privacy-notice">
            <h4>Privacy Notice</h4>
            <p>This platform does not store any of your data. Your API keys and search history are stored only in your browser's local storage. Each session is independent and we cannot access any of your information.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ApiKeySetup;
