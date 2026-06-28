"""
Custom exception classes for the trading bot.

Provides a hierarchy of exceptions for different error scenarios,
enabling precise error handling and user-friendly error messages.
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class ValidationError(TradingBotError):
    """Raised when user input validation fails."""

    def __init__(self, field: str, message: str, details: str = "") -> None:
        self.field = field
        super().__init__(message, details)


class APIError(TradingBotError):
    """Raised when Binance API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str = ""
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, response_body)


class AuthenticationError(APIError):
    """Raised when API authentication fails (invalid API key/secret)."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class NetworkError(TradingBotError):
    """Raised when network-related errors occur (timeout, connection failure)."""

    def __init__(self, message: str = "Network error occurred") -> None:
        super().__init__(message)


class OrderError(TradingBotError):
    """Raised when order placement fails due to exchange rejection."""

    def __init__(
        self,
        message: str,
        order_id: str | None = None
    ) -> None:
        self.order_id = order_id
        super().__init__(message)
