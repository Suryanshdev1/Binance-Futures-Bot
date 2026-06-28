"""
Order management module for the trading bot.

Provides high-level functions for placing market and limit orders,
formatting order summaries and responses, and handling order-related operations.
Acts as the service layer between the CLI and the Binance API client.
"""

import logging
from decimal import Decimal
from typing import Any

from bot.client import BinanceFuturesClient
from bot.exceptions import OrderError, TradingBotError

logger = logging.getLogger("trading_bot")


def format_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Decimal | None = None
) -> str:
    """
    Format an order summary for display before submission.

    Args:
        symbol: The trading pair symbol (e.g., BTCUSDT).
        side: The order side (BUY or SELL).
        order_type: The order type (MARKET or LIMIT).
        quantity: The order quantity.
        price: The order price (None for market orders).

    Returns:
        str: Formatted order summary string.

    Example:
        >>> print(format_order_summary("BTCUSDT", "BUY", "MARKET", Decimal("0.001")))
    """
    price_display = f"{price:,.2f}" if price else "Market Price"

    summary = f"""
====================================
ORDER SUMMARY
====================================

Symbol      : {symbol}
Side        : {side}
Order Type  : {order_type}
Quantity    : {quantity}
Price       : {price_display}

===================================="""

    return summary


def format_order_response(order: dict[str, Any]) -> str:
    """
    Format an order response from the Binance API for display.

    Args:
        order: The order response dictionary from the API.

    Returns:
        str: Formatted order response string.

    Example:
        >>> print(format_order_response({"orderId": 123, "status": "FILLED", ...}))
    """
    order_id = order.get("orderId", "N/A")
    status = order.get("status", "UNKNOWN")
    executed_qty = order.get("executedQty", "0")
    avg_price = order.get("avgPrice", "0")

    # Calculate total value if available
    try:
        total = float(executed_qty) * float(avg_price)
        total_str = f"{total:,.2f}"
    except (ValueError, TypeError):
        total_str = "N/A"

    # Determine status display
    status_display = status
    if status == "FILLED":
        status_display = "[green]FILLED[/green]"
    elif status == "PARTIALLY_FILLED":
        status_display = "[yellow]PARTIALLY FILLED[/yellow]"
    elif status == "NEW":
        status_display = "[blue]NEW (Open)[/blue]"
    elif status in ("CANCELED", "REJECTED", "EXPIRED"):
        status_display = f"[red]{status}[/red]"

    response = f"""
====================================
ORDER RESPONSE
====================================

Order ID       : {order_id}
Status         : {status_display}
Executed Qty   : {executed_qty}
Average Price  : {avg_price}
Total Value    : {total_str} USDT

===================================="""

    # Add success/failure message
    if status == "FILLED":
        response += "\n[bold green]✓[/bold green] Order placed and filled successfully.\n"
    elif status == "NEW":
        response += "\n[bold blue]ℹ[/bold blue] Order placed successfully and is now open.\n"
    elif status == "PARTIALLY_FILLED":
        response += "\n[bold yellow]⚠[/bold yellow] Order partially filled.\n"
    else:
        response += f"\n[bold red]✗[/bold red] Order status: {status}\n"

    return response


def format_order_error(error: TradingBotError) -> str:
    """
    Format an order error for user-friendly display.

    Args:
        error: The trading bot error that occurred.

    Returns:
        str: Formatted error message.
    """
    error_message = f"""
====================================
ORDER FAILED
====================================

[bold red]✗[/bold red] {error.message}
"""

    if error.details:
        error_message += f"\nDetails:\n{error.details}\n"

    error_message += "\n====================================\n"

    return error_message


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal
) -> dict[str, Any]:
    """
    Place a market order using the provided client.

    Args:
        client: The Binance Futures client instance.
        symbol: The validated trading pair symbol.
        side: The validated order side (BUY or SELL).
        quantity: The validated order quantity.

    Returns:
        dict: The API order response.

    Raises:
        OrderError: If the order is rejected by the exchange.
        TradingBotError: If an unexpected error occurs.

    Example:
        >>> client = BinanceFuturesClient()
        >>> response = place_market_order(client, "BTCUSDT", "BUY", Decimal("0.001"))
    """
    try:
        logger.info(
            "Sending MARKET %s order | Symbol: %s | Qty=%s",
            side, symbol, quantity
        )

        response = client.place_market_order(
            symbol=symbol,
            side=side,
            quantity=str(quantity)
        )

        logger.info(
            "Response received | Order ID: %s | Status: %s",
            response.get("orderId", "N/A"),
            response.get("status", "UNKNOWN")
        )

        if response.get("status") == "FILLED":
            logger.info("Order Filled | Qty: %s | AvgPrice: %s",
                        response.get("executedQty"),
                        response.get("avgPrice", "N/A"))
        elif response.get("status") == "NEW":
            logger.info("Order Created | Order ID: %s", response.get("orderId"))

        return response

    except TradingBotError:
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error("Unexpected error in place_market_order: %s", e)
        raise TradingBotError(
            message="An unexpected error occurred while placing the market order.",
            details=str(e)
        )


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal
) -> dict[str, Any]:
    """
    Place a limit order using the provided client.

    Args:
        client: The Binance Futures client instance.
        symbol: The validated trading pair symbol.
        side: The validated order side (BUY or SELL).
        quantity: The validated order quantity.
        price: The validated limit price.

    Returns:
        dict: The API order response.

    Raises:
        OrderError: If the order is rejected by the exchange.
        TradingBotError: If an unexpected error occurs.

    Example:
        >>> client = BinanceFuturesClient()
        >>> response = place_limit_order(client, "BTCUSDT", "BUY", Decimal("0.001"), Decimal("95000"))
    """
    try:
        logger.info(
            "Sending LIMIT %s order | Symbol: %s | Qty=%s | Price=%s",
            side, symbol, quantity, price
        )

        response = client.place_limit_order(
            symbol=symbol,
            side=side,
            quantity=str(quantity),
            price=str(price)
        )

        logger.info(
            "Response received | Order ID: %s | Status: %s",
            response.get("orderId", "N/A"),
            response.get("status", "UNKNOWN")
        )

        if response.get("status") == "FILLED":
            logger.info("Order Filled | Qty: %s | AvgPrice: %s",
                        response.get("executedQty"),
                        response.get("avgPrice", "N/A"))
        elif response.get("status") == "NEW":
            logger.info("Order Created | Order ID: %s", response.get("orderId"))

        return response

    except TradingBotError:
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error("Unexpected error in place_limit_order: %s", e)
        raise TradingBotError(
            message="An unexpected error occurred while placing the limit order.",
            details=str(e)
        )


def execute_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Decimal | None = None
) -> dict[str, Any]:
    """
    Execute an order based on the order type.

    Routes to the appropriate order placement function based on order type.

    Args:
        client: The Binance Futures client instance.
        symbol: The validated trading pair symbol.
        side: The validated order side (BUY or SELL).
        order_type: The validated order type (MARKET or LIMIT).
        quantity: The validated order quantity.
        price: The validated limit price (None for market orders).

    Returns:
        dict: The API order response.

    Raises:
        OrderError: If the order is rejected.
        TradingBotError: If an unexpected error occurs.

    Example:
        >>> client = BinanceFuturesClient()
        >>> # Market order
        >>> response = execute_order(client, "BTCUSDT", "BUY", "MARKET", Decimal("0.001"))
        >>> # Limit order
        >>> response = execute_order(client, "BTCUSDT", "BUY", "LIMIT", Decimal("0.001"), Decimal("95000"))
    """
    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)
    elif order_type == "LIMIT":
        if price is None:
            raise OrderError(
                message="Price is required for LIMIT orders.",
                order_id=None
            )
        return place_limit_order(client, symbol, side, quantity, price)
    else:
        raise OrderError(
            message=f"Unsupported order type: {order_type}",
            order_id=None
        )
