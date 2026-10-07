import React, { useState, useEffect } from 'react';
import './App.css';
import ApiKeySetup from './components/ApiKeySetup';
import Dashboard from './components/Dashboard';

function App() {
  const [apiKeys, setApiKeys] = useState(null);
  const [backendUrl, setBackendUrl] = useState(
    process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'
  );

  useEffect(() => {
    const savedKeys = localStorage.getItem('investmentApiKeys');
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys));
      } catch (e) {
        console.error('Failed to parse saved API keys');
      }
    }
  }, []);

  const handleApiKeysSubmit = (keys) => {
    setApiKeys(keys);
    localStorage.setItem('investmentApiKeys', JSON.stringify(keys));
  };

  const handleLogout = () => {
    setApiKeys(null);
    localStorage.removeItem('investmentApiKeys');
  };

  return (
    <div className="App">
      {!apiKeys ? (
        <ApiKeySetup onSubmit={handleApiKeysSubmit} />
      ) : (
        <Dashboard
          apiKeys={apiKeys}
          onLogout={handleLogout}
          backendUrl={backendUrl}
        />
      )}
    </div>
  );
}

export default App;
