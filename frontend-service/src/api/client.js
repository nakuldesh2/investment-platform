"""Axios client with JWT token support and interceptors"""

import axios from "axios";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Include cookies (httpOnly JWT) with requests
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor to handle auth errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  register: (email, password) =>
    client.post("/auth/register", { email, password }),
  login: (email, password) =>
    client.post("/auth/login", { email, password }),
  logout: () => client.post("/auth/logout"),
  refresh: (token) =>
    client.post("/auth/refresh", { access_token: token, token_type: "bearer" }),
  getCurrentUser: () => client.get("/auth/me"),
};

// Market Data APIs
export const marketAPI = {
  getQuote: (symbol) => client.get(`/api/market/quote/${symbol}`),
  getCachedQuote: (symbol) => client.get(`/api/market/quote/${symbol}`),
};

// News APIs
export const newsAPI = {
  getSentiment: (symbol) => client.get(`/api/news/sentiment/${symbol}`),
  getNews: (symbol) => client.get(`/api/news/${symbol}`),
};

// Signal APIs
export const signalAPI = {
  getTopIdeas: (symbols) =>
    client.get(`/api/ideas/top?symbols=${symbols.join(",")}`),
};

export default client;
