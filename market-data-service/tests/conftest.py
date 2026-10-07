"""Pytest configuration for market data service tests"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings


@pytest.fixture
def test_settings():
    """Create test settings"""
    return Settings(
        environment="testing",
        debug=True,
        alpha_vantage_api_key="demo",
        request_timeout_seconds=20,
    )


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_alpha_vantage_response():
    """Mock Alpha Vantage API response"""
    return {
        "Global Quote": {
            "01. symbol": "AAPL",
            "05. price": "150.25",
            "06. volume": "52341000",
            "08. previous close": "149.80",
            "10. change percent": "+0.30%",
        }
    }
