"""Market Data Service configuration"""

from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field


class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Market Data Service settings"""

    # Core
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    service_name: str = Field(default="market-data-service")
    service_port: int = Field(default=8001)

    # Timeouts
    request_timeout_seconds: int = Field(default=20)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://investment_user:investment_pass@postgres:5432/investment_platform"
    )
    database_echo: bool = Field(default=False)

    # Redis
    redis_url: str = Field(default="redis://redis:6379/0")

    # Logging
    log_level: str = Field(default="INFO")

    # External APIs
    alpha_vantage_api_key: str = Field(default="demo")
    alpha_vantage_url: str = Field(default="https://www.alphavantage.co/query")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    def __init__(self, **data):
        super().__init__(**data)
        if self.is_production:
            self.debug = False
