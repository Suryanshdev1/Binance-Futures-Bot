"""
Configuration module for loading environment variables and settings.

Loads sensitive credentials and API configuration from .env file.
Provides centralized configuration management for the trading bot.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigError(Exception):
    """Raised when a required configuration variable is missing or invalid."""


# Binance API Configuration
BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "")

# Base URL for Binance Futures Testnet
BINANCE_BASE_URL: str = "https://testnet.binancefuture.com"

# API Timeouts (in seconds)
CONNECT_TIMEOUT: float = 10.0
READ_TIMEOUT: float = 30.0

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/trading_bot.log")

# Maximum retries for API calls
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))


def validate_config() -> None:
    """
    Validate that all required configuration variables are set.

    Raises:
        ConfigError: If API key or secret is missing.

    Example:
        >>> validate_config()
        ConfigError: BINANCE_API_KEY is required but not set.
    """
    missing = []

    if not BINANCE_API_KEY:
        missing.append("BINANCE_API_KEY")
    if not BINANCE_SECRET_KEY:
        missing.append("BINANCE_SECRET_KEY")

    if missing:
        raise ConfigError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please set them in your .env file. "
            f"See .env.example for reference."
        )
