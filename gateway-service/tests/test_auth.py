"""Tests for authentication endpoints"""

import pytest
from sqlalchemy.future import select
from app.models import User


class TestAuthEndpoints:
    """Authentication endpoint tests"""

    def test_health_endpoint(self, client):
        """Test health check endpoint is accessible without auth"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration fails with duplicate email"""
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "anotherpassword123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["error"]

    def test_register_weak_password(self, client):
        """Test registration fails with weak password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak"  # Less than 8 characters
            }
        )
        assert response.status_code == 422  # Validation error

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        # Check token is set in httpOnly cookie
        assert "access_token" in client.cookies

    def test_login_invalid_password(self, client, test_user):
        """Test login fails with invalid password"""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login fails with nonexistent email"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword123"
            }
        )
        assert response.status_code == 401

    def test_logout(self, client, authenticated_client):
        """Test logout clears token cookie"""
        response = authenticated_client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
        # Check token cookie is cleared
        assert "access_token" not in authenticated_client.cookies or \
               authenticated_client.cookies.get("access_token") == ""

    def test_get_current_user(self, client, authenticated_client, test_user):
        """Test getting current user info when authenticated"""
        response = authenticated_client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user fails without authentication"""
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestAuthTokens:
    """JWT token tests"""

    def test_token_refresh(self, client, authenticated_client, test_settings, test_user):
        """Test refreshing an access token"""
        # Get original token from cookie
        original_token = authenticated_client.cookies.get("access_token")

        response = authenticated_client.post(
            "/auth/refresh",
            json={
                "access_token": original_token,
                "token_type": "bearer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        # New token should be different
        assert data["access_token"] != original_token

    def test_invalid_token_denied(self, client):
        """Test that invalid tokens are rejected"""
        client.cookies.set("access_token", "invalid.token.here")
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication"""

    def test_protected_endpoint_requires_auth(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/market/quote/AAPL")
        assert response.status_code == 401

    def test_protected_endpoint_with_auth(self, client, authenticated_client):
        """Test accessing protected endpoint with valid token"""
        # This will fail because market data service isn't running in tests,
        # but demonstrates the auth middleware is working
        response = authenticated_client.get("/api/market/quote/AAPL")
        # Should not be 401, might be 502 if upstream is down
        assert response.status_code != 401
