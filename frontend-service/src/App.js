import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import RequestAccess from './components/RequestAccess';
import ApiKeySetup from './components/ApiKeySetup';
import Dashboard from './components/Dashboard';

function App() {
  const [authState, setAuthState] = useState('loading'); // loading, login, request_access, setup, dashboard
  const [user, setUser] = useState(null);
  const [backendUrl] = useState(
    process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'
  );

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/auth/me`, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);

        // Check if user has API keys setup
        const keysResponse = await fetch(`${backendUrl}/auth/user-keys`, {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });

        if (keysResponse.ok) {
          const keysData = await keysResponse.json();
          if (keysData.api_keys && Object.keys(keysData.api_keys).length > 0) {
            setAuthState('dashboard');
          } else {
            setAuthState('setup');
          }
        } else {
          setAuthState('setup');
        }
      } else {
        setAuthState('login');
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
      setAuthState('login');
    }
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setAuthState('setup');
  };

  const handleAccessRequested = (email) => {
    setAuthState('request_access');
  };

  const handleApiKeysSetup = () => {
    setAuthState('dashboard');
  };

  const handleLogout = async () => {
    try {
      await fetch(`${backendUrl}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    }

    setUser(null);
    setAuthState('login');
  };

  return (
    <div className="App">
      {authState === 'loading' && (
        <div className="loading">
          <p>Loading...</p>
        </div>
      )}

      {authState === 'login' && (
        <Login
          onLoginSuccess={handleLoginSuccess}
          onAccessRequested={handleAccessRequested}
          backendUrl={backendUrl}
        />
      )}

      {authState === 'request_access' && (
        <RequestAccess email={user?.email} />
      )}

      {authState === 'setup' && user && (
        <ApiKeySetup
          onComplete={handleApiKeysSetup}
          userId={user.id}
          backendUrl={backendUrl}
        />
      )}

      {authState === 'dashboard' && user && (
        <Dashboard
          user={user}
          onLogout={handleLogout}
          backendUrl={backendUrl}
        />
      )}
    </div>
  );
}

export default App;
