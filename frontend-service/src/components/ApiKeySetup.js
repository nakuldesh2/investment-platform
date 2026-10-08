import React, { useState, useEffect } from 'react';
import { AlertCircle, ExternalLink, CheckCircle } from 'lucide-react';
import './ApiKeySetup.css';

function ApiKeySetup({ onComplete, userId, backendUrl }) {
  const [formData, setFormData] = useState({
    alpha_vantage: '',
    news_api: '',
    finnhub: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const apiBase = backendUrl || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  // Load existing API keys on mount
  useEffect(() => {
    const loadExistingKeys = async () => {
      try {
        const response = await fetch(`${apiBase}/auth/user-keys`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          if (data.api_keys && Object.keys(data.api_keys).length > 0) {
            setFormData(data.api_keys);
          }
        }
      } catch (err) {
        console.error('Failed to load existing API keys:', err);
      }
    };

    loadExistingKeys();
  }, [apiBase]);

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
    if (!formData.alpha_vantage.trim()) {
      newErrors.alpha_vantage = 'Alpha Vantage API key is required';
    }
    if (!formData.news_api.trim()) {
      newErrors.news_api = 'NewsAPI key is required';
    }
    if (!formData.finnhub.trim()) {
      newErrors.finnhub = 'Finnhub API key is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setSuccess(false);
    setErrors({});

    try {
      const response = await fetch(`${apiBase}/auth/user-keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save API keys');
      }

      const data = await response.json();
      setSuccess(true);
      setSuccessMessage(`✅ API keys saved! (${data.keys_stored.join(', ')})`);

      // Call completion callback if provided
      if (onComplete) {
        setTimeout(() => onComplete(), 1500);
      }
    } catch (err) {
      setErrors({ submit: err.message || 'Failed to save API keys' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-key-setup">
      <div className="setup-container">
        <div className="setup-header">
          <h1>Configure API Keys</h1>
          <p>Enter your API keys to access real market data</p>
        </div>

        <div className="setup-content">
          {success && (
            <div className="success-box">
              <CheckCircle size={20} />
              <p>{successMessage}</p>
            </div>
          )}

          {errors.submit && (
            <div className="error-box">
              <AlertCircle size={20} />
              <p>{errors.submit}</p>
            </div>
          )}

          <div className="info-box">
            <AlertCircle size={20} />
            <p>Your API keys are stored securely in our database and never exposed to the browser.</p>
          </div>

          <form onSubmit={handleSubmit} className="api-key-form">
            <div className="form-section">
              <h2>Step 1: Get Free API Keys</h2>
              <p>Sign up for free accounts and get your API keys:</p>
            </div>

            <div className="form-group">
              <label htmlFor="alpha_vantage">
                <span>Alpha Vantage API Key *</span>
                <a href="https://www.alphavantage.co/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="alpha_vantage"
                type="password"
                name="alpha_vantage"
                value={formData.alpha_vantage}
                onChange={handleChange}
                placeholder="Enter your Alpha Vantage API key"
                className={errors.alpha_vantage ? 'error' : ''}
              />
              {errors.alpha_vantage && <span className="error-text">{errors.alpha_vantage}</span>}
              <small>Free tier: 5 calls/min, 500/day | Used for real-time stock quotes</small>
            </div>

            <div className="form-group">
              <label htmlFor="news_api">
                <span>NewsAPI Key *</span>
                <a href="https://newsapi.org/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="news_api"
                type="password"
                name="news_api"
                value={formData.news_api}
                onChange={handleChange}
                placeholder="Enter your NewsAPI key"
                className={errors.news_api ? 'error' : ''}
              />
              {errors.news_api && <span className="error-text">{errors.news_api}</span>}
              <small>Free tier: 100 requests/day | Used for financial news</small>
            </div>

            <div className="form-group">
              <label htmlFor="finnhub">
                <span>Finnhub API Key *</span>
                <a href="https://finnhub.io/" target="_blank" rel="noopener noreferrer">
                  Get Free Key <ExternalLink size={14} />
                </a>
              </label>
              <input
                id="finnhub"
                type="password"
                name="finnhub"
                value={formData.finnhub}
                onChange={handleChange}
                placeholder="Enter your Finnhub API key"
                className={errors.finnhub ? 'error' : ''}
              />
              {errors.finnhub && <span className="error-text">{errors.finnhub}</span>}
              <small>Free tier: 60 calls/min | Used for company data</small>
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Saving...' : 'Save API Keys'}
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
            <h4>Security</h4>
            <p>Your API keys are stored securely in our database with encryption. Only you can retrieve your own keys. We never expose your keys to the browser or third parties.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ApiKeySetup;
