import React, { useState } from 'react';
import { LogOut, Search, TrendingUp, Newspaper, Zap } from 'lucide-react';
import './Dashboard.css';
import StockSearch from './StockSearch';
import NewsSection from './NewsSection';
import SignalsSection from './SignalsSection';

function Dashboard({ apiKeys, onLogout, backendUrl }) {
  const [activeTab, setActiveTab] = useState('search');
  const [selectedStock, setSelectedStock] = useState(null);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Investment Platform</h1>
          <p>Real-time Market Data, News & AI Signals</p>
        </div>
        <button onClick={onLogout} className="logout-btn">
          <LogOut size={18} />
          Logout
        </button>
      </header>

      <nav className="dashboard-nav">
        <button
          className={`nav-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <Search size={18} />
          Market Data
        </button>
        <button
          className={`nav-btn ${activeTab === 'news' ? 'active' : ''}`}
          onClick={() => setActiveTab('news')}
        >
          <Newspaper size={18} />
          News & Sentiment
        </button>
        <button
          className={`nav-btn ${activeTab === 'signals' ? 'active' : ''}`}
          onClick={() => setActiveTab('signals')}
        >
          <Zap size={18} />
          AI Signals
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'search' && (
          <StockSearch
            apiKeys={apiKeys}
            backendUrl={backendUrl}
            onStockSelect={setSelectedStock}
          />
        )}
        {activeTab === 'news' && (
          <NewsSection
            apiKeys={apiKeys}
            backendUrl={backendUrl}
            selectedStock={selectedStock}
          />
        )}
        {activeTab === 'signals' && (
          <SignalsSection
            apiKeys={apiKeys}
            backendUrl={backendUrl}
            selectedStock={selectedStock}
          />
        )}
      </main>
    </div>
  );
}

export default Dashboard;
