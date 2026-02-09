"""
Configuration management for the Injective Market Analytics API
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Injective Network
    network: Literal["mainnet", "testnet"] = "testnet"
    grpc_endpoint: str = ""
    lcd_endpoint: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Injective Market Analytics API"
    api_version: str = "1.0.0"
    api_description: str = """
    A comprehensive API for Injective blockchain market data and analytics.
    
    This API provides:
    - Real-time market data aggregation
    - Derived trading metrics and signals
    - Developer-friendly utilities with caching
    - Multi-market comparison tools
    """
    
    # Cache Configuration
    cache_ttl_seconds: int = 60
    max_cache_size: int = 1000
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
