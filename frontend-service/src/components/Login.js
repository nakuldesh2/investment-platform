import React, { useState } from "react";
import "./Login.css";

export default function Login({ onLoginSuccess, onAccessRequested, backendUrl }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || data.error || "Authentication failed");
        return;
      }

      if (isLogin) {
        // Login successful - token is in httpOnly cookie
        const userResponse = await fetch(`${backendUrl}/auth/me`, {
          headers: { "Content-Type": "application/json" },
          credentials: "include",
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          onLoginSuccess(userData);
        }
      } else {
        // Registration successful
        const status = data.status || "pending";
        if (status === "approved") {
          setSuccess("Account created and approved! Logging you in...");
          setTimeout(() => {
            setIsLogin(true);
            setPassword("");
          }, 1500);
        } else {
          setSuccess("Account created! Please wait for admin approval.");
          onAccessRequested(email);
        }
      }
    } catch (error) {
      console.error("Auth error:", error);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>{isLogin ? "Sign In" : "Create Account"}</h1>
          <p className="subtitle">
            {isLogin
              ? "Access your investment research dashboard"
              : "Join the investment research platform"}
          </p>
        </div>

        {error && <div className="error-box">{error}</div>}
        {success && <div className="success-box">{success}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            {" "}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
                setSuccess("");
                setPassword("");
              }}
              className="toggle-button"
              disabled={loading}
            >
              {isLogin ? "Create one" : "Sign in"}
            </button>
          </p>
        </div>

        <div className="login-info">
          <p>
            <strong>Demo Access:</strong> Use any email with allowlisted domain
            or contact the administrator for approval.
          </p>
        </div>
      </div>
    </div>
  );
}
