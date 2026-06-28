#!/usr/bin/env python3
"""
Trading Bot CLI - Main entry point for the Binance Futures Testnet Trading Bot.

A professional command-line interface for placing Market and Limit orders
on the Binance USDT-M Futures Testnet with colored output, comprehensive
logging, and robust error handling.

Usage:
    # Market BUY order
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    # Market SELL order
    python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01

    # Limit BUY order
    python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 95000

    # Limit SELL order
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 105000
"""

import argparse
import logging
import sys
from typing import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from bot import config
from bot.client import BinanceFuturesClient
from bot.exceptions import TradingBotError
from bot.logging_config import setup_logging
from bot.orders import (
    execute_order,
    format_order_error,
    format_order_response,
    format_order_summary,
)
from bot.validators import validate_order_inputs

# Initialize Rich console for beautiful output
console = Console()

# Application metadata
APP_NAME = "Binance Futures Trading Bot"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional trading bot for Binance USDT-M Futures Testnet"


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description=f"{APP_NAME} v{APP_VERSION}\n{APP_DESCRIPTION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY order
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Market SELL order
  python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01

  # Limit BUY order
  python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 95000

  # Limit SELL order
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 105000
        """
    )

    parser.add_argument(
        "--symbol", "-s",
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT, ETHUSDT)"
    )

    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL"
    )

    parser.add_argument(
        "--type", "-t",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT"
    )

    parser.add_argument(
        "--quantity", "-q",
        required=True,
        help="Order quantity (e.g., 0.001)"
    )

    parser.add_argument(
        "--price", "-p",
        required=False,
        default=None,
        help="Limit price (required for LIMIT orders, ignored for MARKET)"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {APP_VERSION}"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (DEBUG logging)"
    )

    return parser


def print_banner() -> None:
    """Print the application banner with styled output."""
    banner_text = Text()
    banner_text.append(f"{APP_NAME}\n", style="bold cyan")
    banner_text.append(f"v{APP_VERSION} | ", style="dim")
    banner_text.append("Binance USDT-M Futures Testnet", style="dim")

    console.print(Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()


def print_success(message: str) -> None:
    """Print a success message with styling."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message with styling."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with styling."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print an informational message with styling."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for the trading bot CLI.

    Parses command-line arguments, validates inputs, initializes the
    Binance client, executes the order, and displays formatted output.

    Args:
        argv: Optional command-line arguments for testing.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    # Print application banner
    print_banner()

    # Parse CLI arguments
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging with verbose support
    log_level = "DEBUG" if args.verbose else config.LOG_LEVEL
    logger = setup_logging(log_level=log_level)

    # Log application startup
    logger.info("=" * 50)
    logger.info("Trading Bot Started")
    logger.info("Application version: %s", APP_VERSION)
    logger.info("CLI Arguments: symbol=%s, side=%s, type=%s, quantity=%s, price=%s",
                args.symbol, args.side, args.order_type, args.quantity, args.price)

    try:
        # Step 1: Validate all inputs
        print_info("Validating inputs...")
        logger.info("Validating order inputs")

        validated = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price
        )

        logger.info(
            "Validation passed: symbol=%s, side=%s, type=%s, quantity=%s, price=%s",
            validated["symbol"],
            validated["side"],
            validated["order_type"],
            validated["quantity"],
            validated["price"]
        )
        print_success("Inputs validated successfully")
        console.print()

        # Step 2: Display order summary
        summary = format_order_summary(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"]
        )
        console.print(summary)
        console.print()

        # Step 3: Initialize Binance client
        print_info("Initializing Binance Futures client...")
        logger.info("Initializing Binance Futures client")

        client = BinanceFuturesClient()

        print_success("Client initialized successfully")
        console.print()

        # Step 4: Execute the order
        print_info(
            f"Sending {validated['order_type']} {validated['side']} order..."
        )

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(
                description=f"Placing {validated['side']} order for {validated['symbol']}...",
                total=None
            )

            response = execute_order(
                client=client,
                symbol=validated["symbol"],
                side=validated["side"],
                order_type=validated["order_type"],
                quantity=validated["quantity"],
                price=validated["price"]
            )

        # Step 5: Display order response
        console.print()
        response_text = format_order_response(response)
        console.print(response_text)

        logger.info("Order execution completed successfully")
        return 0

    except TradingBotError as e:
        # Handle known application errors
        logger.error("TradingBotError: %s | Details: %s", e.message, e.details)

        console.print()
        error_text = format_order_error(e)
        console.print(error_text)

        # Provide helpful guidance based on error type
        if "BINANCE_API_KEY" in str(e.message):
            console.print("[yellow]Tip:[/yellow] Make sure your .env file contains valid API credentials.")
            console.print("      Copy .env.example to .env and fill in your Binance Testnet API keys.")

        return 1

    except KeyboardInterrupt:
        console.print("\n")
        print_warning("Operation cancelled by user.")
        logger.info("Operation cancelled by user (KeyboardInterrupt)")
        return 130  # Standard exit code for Ctrl+C

    except Exception as e:
        # Handle unexpected errors
        logger.exception("Unexpected error: %s", e)

        console.print()
        console.print(Panel(
            f"[bold red]Unexpected Error[/bold red]\n\n"
            f"An unexpected error occurred:\n{e}",
            border_style="red",
            padding=(1, 2)
        ))

        return 1

    finally:
        # Ensure client is properly closed
        try:
            if "client" in locals():
                client.close()
        except Exception:
            pass

        logger.info("Trading Bot Finished")
        logger.info("=" * 50)


if __name__ == "__main__":
    sys.exit(main())
