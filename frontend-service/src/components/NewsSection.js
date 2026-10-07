import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ExternalLink, AlertCircle, Loader, ThumbsUp, ThumbsDown } from 'lucide-react';
import './NewsSection.css';

function NewsSection({ apiKeys, backendUrl, selectedStock }) {
  const [news, setNews] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchSymbol, setSearchSymbol] = useState(selectedStock || '');

  const fetchNews = async (symbol) => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setNews([]);
    setSentiment(null);

    try {
      // Fetch news
      const newsResponse = await axios.get(`${backendUrl}/news/${symbol.toUpperCase()}`, {
        headers: {
          'X-News-API-Key': apiKeys.newsApiKey,
          'X-Finnhub-API-Key': apiKeys.finnhubKey
        }
      });
      setNews(newsResponse.data.articles || []);

      // Fetch sentiment
      try {
        const sentimentResponse = await axios.get(`${backendUrl}/sentiment/${symbol.toUpperCase()}`, {
          headers: {
            'X-News-API-Key': apiKeys.newsApiKey,
            'X-Finnhub-API-Key': apiKeys.finnhubKey
          }
        });
        setSentiment(sentimentResponse.data);
      } catch (err) {
        console.log('Sentiment data not available');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch news. Please try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchNews(searchSymbol);
  };

  const getSentimentColor = (score) => {
    if (score > 0.5) return 'positive';
    if (score < -0.5) return 'negative';
    return 'neutral';
  };

  return (
    <div className="news-section">
      <div className="news-header">
        <form onSubmit={handleSearch} className="news-search-form">
          <input
            type="text"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol to get news"
            className="news-search-input"
          />
          <button type="submit" className="news-search-btn" disabled={loading}>
            {loading ? <Loader className="spinner" size={18} /> : 'Search News'}
          </button>
        </form>

        {sentiment && (
          <div className={`sentiment-card ${getSentimentColor(sentiment.sentiment_score)}`}>
            <div className="sentiment-header">
              <h3>Market Sentiment</h3>
              <div className="sentiment-score">{(sentiment.sentiment_score * 100)?.toFixed(1)}%</div>
            </div>
            <div className="sentiment-breakdown">
              <div className="breakdown-item positive">
                <ThumbsUp size={16} />
                <span>{sentiment.sentiment_breakdown?.positive || 0} Positive</span>
              </div>
              <div className="breakdown-item neutral">
                <span>{sentiment.sentiment_breakdown?.neutral || 0} Neutral</span>
              </div>
              <div className="breakdown-item negative">
                <ThumbsDown size={16} />
                <span>{sentiment.sentiment_breakdown?.negative || 0} Negative</span>
              </div>
            </div>
          </div>
        )}
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
          <p>Fetching news...</p>
        </div>
      )}

      <div className="news-list">
        {news.length > 0 ? (
          news.map((article, index) => (
            <div key={index} className="news-item">
              <div className="news-content">
                <h4>{article.title}</h4>
                <p className="news-source">
                  <span className="source">{article.source}</span>
                  <span className="date">{new Date(article.published_at).toLocaleDateString()}</span>
                </p>
                <p className="news-summary">{article.summary}</p>
              </div>
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">
                Read More <ExternalLink size={14} />
              </a>
            </div>
          ))
        ) : !loading && searchSymbol ? (
          <div className="empty-state">
            <p>No news found for {searchSymbol}</p>
          </div>
        ) : (
          <div className="empty-state">
            <p>Search for a stock symbol to view related news</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default NewsSection;
