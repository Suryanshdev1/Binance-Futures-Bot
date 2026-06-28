"""
Input validation module for the trading bot CLI.

Provides comprehensive validation for all user inputs including
symbol format, order side, order type, quantity, and price.
Ensures all inputs meet Binance API requirements before submission.
"""

import re
from decimal import Decimal, InvalidOperation

from bot.exceptions import ValidationError

# Valid order sides
VALID_SIDES: set[str] = {"BUY", "SELL"}

# Valid order types
VALID_ORDER_TYPES: set[str] = {"MARKET", "LIMIT"}

# Symbol format: uppercase letters/digits ending with USDT
# Examples: BTCUSDT, ETHUSDT, BNBUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]+USDT$")

# Maximum allowed decimal places for quantity
MAX_QUANTITY_PRECISION: int = 8

# Maximum allowed decimal places for price
MAX_PRICE_PRECISION: int = 8


def validate_symbol(symbol: str) -> str:
    """
    Validate the trading symbol format.

    Args:
        symbol: The trading pair symbol (e.g., BTCUSDT).

    Returns:
        str: The validated uppercase symbol.

    Raises:
        ValidationError: If the symbol is empty, malformed, or unsupported.

    Example:
        >>> validate_symbol("BTCUSDT")
        'BTCUSDT'
        >>> validate_symbol("")
        ValidationError: Symbol cannot be empty.
    """
    if not symbol or not symbol.strip():
        raise ValidationError(
            field="symbol",
            message="Symbol cannot be empty.",
            details="Please provide a valid trading pair symbol (e.g., BTCUSDT)."
        )

    cleaned = symbol.strip().upper()

    if not SYMBOL_PATTERN.match(cleaned):
        raise ValidationError(
            field="symbol",
            message=f"Invalid symbol format: '{symbol}'.",
            details="Symbol must be uppercase and end with 'USDT' (e.g., BTCUSDT, ETHUSDT)."
        )

    return cleaned


def validate_side(side: str) -> str:
    """
    Validate the order side.

    Args:
        side: The order side (BUY or SELL).

    Returns:
        str: The validated uppercase side.

    Raises:
        ValidationError: If the side is not BUY or SELL.

    Example:
        >>> validate_side("buy")
        'BUY'
        >>> validate_side("HOLD")
        ValidationError: Invalid order side: 'HOLD'.
    """
    if not side or not side.strip():
        raise ValidationError(
            field="side",
            message="Order side cannot be empty.",
            details="Please specify 'BUY' or 'SELL'."
        )

    cleaned = side.strip().upper()

    if cleaned not in VALID_SIDES:
        raise ValidationError(
            field="side",
            message=f"Invalid order side: '{side}'.",
            details=f"Supported sides: {', '.join(sorted(VALID_SIDES))}."
        )

    return cleaned


def validate_order_type(order_type: str) -> str:
    """
    Validate the order type.

    Args:
        order_type: The order type (MARKET or LIMIT).

    Returns:
        str: The validated uppercase order type.

    Raises:
        ValidationError: If the order type is not MARKET or LIMIT.

    Example:
        >>> validate_order_type("market")
        'MARKET'
        >>> validate_order_type("STOP")
        ValidationError: Invalid order type: 'STOP'.
    """
    if not order_type or not order_type.strip():
        raise ValidationError(
            field="order_type",
            message="Order type cannot be empty.",
            details="Please specify 'MARKET' or 'LIMIT'."
        )

    cleaned = order_type.strip().upper()

    if cleaned not in VALID_ORDER_TYPES:
        raise ValidationError(
            field="order_type",
            message=f"Invalid order type: '{order_type}'.",
            details=f"Supported types: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    return cleaned


def validate_quantity(quantity: str) -> Decimal:
    """
    Validate the order quantity.

    Args:
        quantity: The order quantity as a string.

    Returns:
        Decimal: The validated positive quantity.

    Raises:
        ValidationError: If the quantity is not a positive number.

    Example:
        >>> validate_quantity("0.001")
        Decimal('0.001')
        >>> validate_quantity("-0.5")
        ValidationError: Quantity must be greater than 0.
    """
    if not quantity or not quantity.strip():
        raise ValidationError(
            field="quantity",
            message="Quantity cannot be empty.",
            details="Please provide a positive quantity (e.g., 0.001)."
        )

    try:
        value = Decimal(quantity.strip())
    except InvalidOperation:
        raise ValidationError(
            field="quantity",
            message=f"Invalid quantity format: '{quantity}'.",
            details="Quantity must be a valid positive number."
        )

    if value <= 0:
        raise ValidationError(
            field="quantity",
            message="Quantity must be greater than 0.",
            details=f"Provided value: {value}."
        )

    # Check precision
    sign, digits, exponent = value.as_tuple()
    if abs(exponent) > MAX_QUANTITY_PRECISION:
        raise ValidationError(
            field="quantity",
            message=f"Quantity exceeds maximum precision of {MAX_QUANTITY_PRECISION} decimal places.",
            details=f"Provided value: {value}."
        )

    return value


def validate_price(price: str | None, order_type: str) -> Decimal | None:
    """
    Validate the order price based on order type.

    For LIMIT orders, price is required and must be positive.
    For MARKET orders, price should be None (a warning is logged if provided).

    Args:
        price: The order price as a string, or None for market orders.
        order_type: The validated order type (MARKET or LIMIT).

    Returns:
        Decimal | None: The validated price for limit orders, None for market orders.

    Raises:
        ValidationError: If price is missing for LIMIT orders or invalid.

    Example:
        >>> validate_price("95000", "LIMIT")
        Decimal('95000')
        >>> validate_price(None, "MARKET")
        None
        >>> validate_price(None, "LIMIT")
        ValidationError: Price is required for LIMIT orders.
    """
    if order_type == "MARKET":
        if price is not None and price.strip():
            # Market order with price - warn but proceed
            return None
        return None

    # LIMIT order - price is required
    if price is None or not price.strip():
        raise ValidationError(
            field="price",
            message="Price is required for LIMIT orders.",
            details="Please provide a positive price (e.g., 95000)."
        )

    try:
        value = Decimal(price.strip())
    except InvalidOperation:
        raise ValidationError(
            field="price",
            message=f"Invalid price format: '{price}'.",
            details="Price must be a valid positive number."
        )

    if value <= 0:
        raise ValidationError(
            field="price",
            message="Price must be greater than 0.",
            details=f"Provided value: {value}."
        )

    # Check precision
    sign, digits, exponent = value.as_tuple()
    if abs(exponent) > MAX_PRICE_PRECISION:
        raise ValidationError(
            field="price",
            message=f"Price exceeds maximum precision of {MAX_PRICE_PRECISION} decimal places.",
            details=f"Provided value: {value}."
        )

    return value


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None
) -> dict[str, str | Decimal | None]:
    """
    Validate all order inputs and return the cleaned values.

    This is the main validation entry point that validates all inputs
    in the correct order and returns a dictionary of validated values.

    Args:
        symbol: The trading pair symbol.
        side: The order side (BUY or SELL).
        order_type: The order type (MARKET or LIMIT).
        quantity: The order quantity.
        price: The order price (required for LIMIT, optional for MARKET).

    Returns:
        dict: Dictionary containing validated values:
              - symbol (str): Uppercase symbol
              - side (str): Uppercase side
              - order_type (str): Uppercase order type
              - quantity (Decimal): Validated quantity
              - price (Decimal | None): Validated price or None

    Raises:
        ValidationError: If any input fails validation.

    Example:
        >>> validate_order_inputs("BTCUSDT", "BUY", "MARKET", "0.001")
        {'symbol': 'BTCUSDT', 'side': 'BUY', 'order_type': 'MARKET',
         'quantity': Decimal('0.001'), 'price': None}
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    validated_price = validate_price(price, validated_order_type)

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_order_type,
        "quantity": validated_quantity,
        "price": validated_price
    }
