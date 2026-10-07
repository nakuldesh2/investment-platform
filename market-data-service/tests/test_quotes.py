"""Tests for quote endpoints"""

import pytest


class TestQuoteEndpoints:
    """Market data quote endpoint tests"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "market-data-service"

    def test_quote_mock_mode(self, client):
        """Test getting quote with mock data"""
        response = client.get("/quote/AAPL?mock=true")
        assert response.status_code == 200
        data = response.json()

        assert data["symbol"] == "AAPL"
        assert data["source"] == "mock"
        assert data["price"] == 187.42
        assert data["volume"] == 52341000
        assert "previous_close" in data
        assert "change_percent" in data

    def test_quote_symbol_normalization(self, client):
        """Test that symbols are normalized to uppercase"""
        response = client.get("/quote/aapl?mock=true")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"  # Should be uppercase

    def test_quote_response_schema(self, client):
        """Test quote response has correct schema"""
        response = client.get("/quote/MSFT?mock=true")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "symbol" in data
        assert "price" in data
        assert "source" in data

        # Check types
        assert isinstance(data["symbol"], str)
        assert isinstance(data["price"], (int, float))

    def test_quote_missing_symbol(self, client):
        """Test quote endpoint with missing symbol"""
        response = client.get("/quote/?mock=true")
        assert response.status_code == 404  # Or 422 depending on FastAPI

    def test_mock_data_consistency(self, client):
        """Test that mock data is consistent across requests"""
        response1 = client.get("/quote/AAPL?mock=true")
        response2 = client.get("/quote/AAPL?mock=true")

        data1 = response1.json()
        data2 = response2.json()

        # Mock data should be consistent
        assert data1["price"] == data2["price"]
        assert data1["volume"] == data2["volume"]
