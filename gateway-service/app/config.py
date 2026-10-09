"""Application configuration management using pydantic-settings"""

import os
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field


class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class BaseAppSettings(BaseSettings):
    """Base settings for all services"""

    # Core
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    service_name: str = Field(default="gateway-service", description="Service name for logging")
    service_port: int = Field(default=8000, description="Service port")

    # Timeouts and limits
    request_timeout_seconds: int = Field(default=20, description="HTTP request timeout in seconds")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://investment_user:investment_pass@postgres:5432/investment_platform",
        description="PostgreSQL database URL"
    )
    database_echo: bool = Field(default=False, description="Enable SQLAlchemy echo for debugging")

    # Redis
    redis_url: str = Field(default="redis://redis:6379/0", description="Redis connection URL")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for service-specific settings

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == Environment.TESTING


class GatewaySettings(BaseAppSettings):
    """Gateway service specific settings"""

    # Auth
    secret_key: str = Field(default="your_super_secret_key_change_this_in_production", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration in hours")

    # User allowlist
    allowlist_emails: str = Field(
        default="admin@example.com",
        description="Comma-separated emails auto-approved without admin review"
    )

    @property
    def allowlisted_emails(self) -> set[str]:
        return {e.strip().lower() for e in self.allowlist_emails.split(",") if e.strip()}

    def __init__(self, **data):
        super().__init__(**data)
        self.service_name = "gateway-service"
        # In production, debug should be False
        if self.is_production:
            self.debug = False


class MarketDataSettings(BaseAppSettings):
    """Market Data Service specific settings"""

    # External API
    alpha_vantage_api_key: str = Field(default="demo", description="Alpha Vantage API key")
    alpha_vantage_url: str = Field(
        default="https://www.alphavantage.co/query",
        description="Alpha Vantage API endpoint"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.service_name = "market-data-service"
        self.service_port = 8001
        if self.is_production:
            self.debug = False


class NewsSettings(BaseAppSettings):
    """News Service specific settings"""

    # External APIs
    news_api_key: str = Field(default="replace_me", description="NewsAPI key")
    finnhub_api_key: str = Field(default="replace_me", description="Finnhub API key")
    marketaux_api_token: str = Field(default="replace_me", description="MarketAux API token")
    marketaux_url: str = Field(
        default="https://api.marketaux.com/v1/news/all",
        description="MarketAux API endpoint"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.service_name = "news-service"
        self.service_port = 8002
        if self.is_production:
            self.debug = False


class MLSignalSettings(BaseAppSettings):
    """ML Signal Service specific settings"""

    # Service URLs
    market_data_base_url: str = Field(default="http://market-data-service:8001", description="Market Data Service URL")
    news_service_base_url: str = Field(default="http://news-service:8002", description="News Service URL")

    def __init__(self, **data):
        super().__init__(**data)
        self.service_name = "ml-signal-service"
        self.service_port = 8003
        if self.is_production:
            self.debug = False


# Load settings from environment
def get_settings(service_class: type[BaseAppSettings] = GatewaySettings) -> BaseAppSettings:
    """Factory function to get settings instance"""
    return service_class()
