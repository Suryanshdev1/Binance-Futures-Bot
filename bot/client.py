"""
Binance API client module for the trading bot.

Handles all communication with the Binance USDT-M Futures Testnet API,
including authentication, request signing, and error handling.
Uses the python-binance library for robust API interactions.
"""

import logging
from typing import Any

from binance.client import Client
from binance.exceptions import (
    BinanceAPIException,
    BinanceOrderException,
    BinanceRequestException,
)

from bot import config
from bot.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    OrderError,
)

logger = logging.getLogger("trading_bot")


class BinanceFuturesClient:
    """
    A client for interacting with the Binance USDT-M Futures Testnet API.

    This class wraps the python-binance library to provide a clean interface
    for placing orders with proper error handling and logging.

    Attributes:
        client (Client): The underlying python-binance client instance.
        testnet (bool): Whether using the testnet environment.

    Example:
        >>> from bot.client import BinanceFuturesClient
        >>> client = BinanceFuturesClient()
        >>> client.ping()
    """

    def __init__(self) -> None:
        """
        Initialize the Binance Futures client.

        Loads API credentials from environment variables and creates
        an authenticated client instance connected to the testnet.

        Raises:
            AuthenticationError: If API credentials are invalid or missing.
            NetworkError: If unable to connect to the API.
        """
        try:
            # Validate configuration before creating client
            config.validate_config()

            logger.info(
                "Initializing Binance Futures client (Testnet: %s)",
                config.BINANCE_BASE_URL
            )

            self.client = Client(
                api_key=config.BINANCE_API_KEY,
                api_secret=config.BINANCE_SECRET_KEY,
                testnet=True,
            )
            self.testnet = True

            # Override the base URL to ensure we're using testnet
            self.client.FUTURES_URL = config.BINANCE_BASE_URL

            logger.info("Binance Futures client initialized successfully")

        except config.ConfigError as e:
            logger.error("Configuration error: %s", e)
            raise AuthenticationError(str(e))
        except Exception as e:
            logger.error("Failed to initialize client: %s", e)
            raise NetworkError(f"Failed to connect to Binance API: {e}")

    def ping(self) -> bool:
        """
        Test connectivity to the Binance API.

        Returns:
            bool: True if the API is reachable, False otherwise.
        """
        try:
            self.client.ping()
            logger.debug("API ping successful")
            return True
        except Exception as e:
            logger.warning("API ping failed: %s", e)
            return False

    def get_account_info(self) -> dict[str, Any]:
        """
        Retrieve account information from the futures account.

        Returns:
            dict: Account information including balances and positions.

        Raises:
            APIError: If the API request fails.
            AuthenticationError: If authentication fails.
        """
        try:
            logger.info("Fetching account information")
            account = self.client.futures_account()
            logger.info("Account information retrieved successfully")
            return account
        except BinanceAPIException as e:
            logger.error("API error fetching account: %s", e)
            if e.code == -2015:
                raise AuthenticationError("Invalid API key or permissions")
            raise APIError(
                message=f"Failed to fetch account: {e.message}",
                status_code=e.status_code,
                response_body=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error fetching account: %s", e)
            raise APIError(message=f"Unexpected error: {e}")

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: str | float
    ) -> dict[str, Any]:
        """
        Place a market order on Binance Futures.

        Args:
            symbol: The trading pair symbol (e.g., BTCUSDT).
            side: The order side (BUY or SELL).
            quantity: The order quantity.

        Returns:
            dict: The order response from the API.

        Raises:
            OrderError: If the order is rejected by the exchange.
            APIError: If the API request fails.
            AuthenticationError: If authentication fails.

        Example:
            >>> client = BinanceFuturesClient()
            >>> response = client.place_market_order("BTCUSDT", "BUY", 0.001)
        """
        try:
            logger.info(
                "Placing MARKET %s order | Symbol: %s | Quantity: %s",
                side, symbol, quantity
            )

            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=float(quantity)
            )

            logger.info(
                "MARKET %s order placed successfully | Order ID: %s",
                side, order.get("orderId", "N/A")
            )
            return order

        except BinanceOrderException as e:
            logger.error("Order rejected: %s", e)
            raise OrderError(
                message=f"Order rejected: {e.message}",
                order_id=str(e.code) if hasattr(e, "code") else None
            )
        except BinanceAPIException as e:
            logger.error("API error placing market order: %s", e)
            if e.code == -2015:
                raise AuthenticationError("Invalid API key or permissions")
            raise APIError(
                message=f"API error: {e.message}",
                status_code=e.status_code,
                response_body=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error placing market order: %s", e)
            raise APIError(message=f"Unexpected error: {e}")

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: str | float,
        price: str | float,
        time_in_force: str = "GTC"
    ) -> dict[str, Any]:
        """
        Place a limit order on Binance Futures.

        Args:
            symbol: The trading pair symbol (e.g., BTCUSDT).
            side: The order side (BUY or SELL).
            quantity: The order quantity.
            price: The limit price.
            time_in_force: Time in force policy (default: GTC - Good Till Cancel).

        Returns:
            dict: The order response from the API.

        Raises:
            OrderError: If the order is rejected by the exchange.
            APIError: If the API request fails.
            AuthenticationError: If authentication fails.

        Example:
            >>> client = BinanceFuturesClient()
            >>> response = client.place_limit_order("BTCUSDT", "BUY", 0.001, 95000)
        """
        try:
            logger.info(
                "Placing LIMIT %s order | Symbol: %s | Quantity: %s | Price: %s | TIF: %s",
                side, symbol, quantity, price, time_in_force
            )

            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce=time_in_force,
                quantity=float(quantity),
                price=float(price)
            )

            logger.info(
                "LIMIT %s order placed successfully | Order ID: %s",
                side, order.get("orderId", "N/A")
            )
            return order

        except BinanceOrderException as e:
            logger.error("Order rejected: %s", e)
            raise OrderError(
                message=f"Order rejected: {e.message}",
                order_id=str(e.code) if hasattr(e, "code") else None
            )
        except BinanceAPIException as e:
            logger.error("API error placing limit order: %s", e)
            if e.code == -2015:
                raise AuthenticationError("Invalid API key or permissions")
            raise APIError(
                message=f"API error: {e.message}",
                status_code=e.status_code,
                response_body=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error placing limit order: %s", e)
            raise APIError(message=f"Unexpected error: {e}")

    def close(self) -> None:
        """
        Close the client session and clean up resources.
        """
        logger.info("Closing Binance Futures client")
        # The python-binance client doesn't have an explicit close method,
        # but we keep this for future compatibility and clean architecture
        pass

    def __enter__(self) -> "BinanceFuturesClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup."""
        self.close()
