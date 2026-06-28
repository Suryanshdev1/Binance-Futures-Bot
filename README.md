# Binance Futures Trading Bot

A production-quality Python CLI application for placing Market and Limit orders on the Binance USDT-M Futures Testnet.

## Overview

This trading bot provides a clean, modular, and reusable interface for executing cryptocurrency futures trades on the Binance Testnet environment. Built with professional software engineering practices including SOLID principles, comprehensive logging, robust exception handling, and an enhanced CLI experience with colored output.

## Features

- **Market Orders**: Place instant BUY/SELL market orders at the current market price
- **Limit Orders**: Place BUY/SELL limit orders at a specified price
- **Input Validation**: Comprehensive validation of all user inputs with meaningful error messages
- **Enhanced CLI**: Beautiful colored output with progress indicators and formatted tables using Rich
- **Comprehensive Logging**: Full audit trail of all operations stored in rotating log files
- **Robust Error Handling**: Graceful handling of API errors, network failures, and invalid inputs
- **Secure Configuration**: API credentials loaded from environment variables via `.env` file
- **Type Hints**: Full type annotation throughout the codebase
- **Modular Architecture**: Clean separation of concerns with reusable components

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Binance Testnet API credentials

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd trading_bot
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Step 1: Create Environment File

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

### Step 2: Add Your Binance Testnet API Keys

Edit the `.env` file and add your API credentials:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
```

### Getting Testnet API Keys

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com/en/register)
2. Register or log in to your account
3. Generate API keys from your profile settings
4. Copy the API Key and Secret Key to your `.env` file

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE_PATH` | `logs/trading_bot.log` | Path to log file |
| `MAX_RETRIES` | `3` | Maximum API retry attempts |

## 🌐 Live Demo

**Demo Website:** https://binance-futures-bot-ilvanpqwt4jgqrjnxdhuuz.streamlit.app/

> **Note:** The live web demo runs on **Streamlit Cloud** (US-based servers). Due to Binance's geographic restrictions, the web version **cannot connect to the Binance Testnet API** from the hosting server.  
>  
> **The web interface works perfectly** — you can explore the UI, form validation, and order summary flow. However, actual order placement requires running the app locally or via VPN.

---

## 🖥️ How to Use This Project

### Option A: CLI (Recommended — Works Everywhere)

The **command-line version** runs on your local machine and connects directly to Binance Testnet. This works regardless of your location because it uses your own internet connection.

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

After placing an order, you can verify it on testnet.binancefuture.com under Futures → Orders → Order History.

### Option B: Web Interface (Requires Local Run or VPN)

To use the web interface with real API calls:

#### 1. Local run (uses your own network — works without VPN):

- bash
```bash
streamlit run web_demo/app.py
```
- Then open http://localhost:8501 in your browser.

#### 2. Deployed version (Streamlit Cloud):

- The deployed website uses cloud servers located in the US.
- Binance blocks API requests from these data center IP addresses.
- If you are in a Binance-supported region or use a VPN, the deployed website will work with real API calls.
- Otherwise, use the local run method above.

## Usage

### Command-Line Syntax

```bash
python cli.py --symbol <SYMBOL> --side <SIDE> --type <TYPE> --quantity <QTY> [--price <PRICE>]
```

### Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--symbol` | `-s` | Yes | Trading pair (e.g., BTCUSDT, ETHUSDT) |
| `--side` | - | Yes | Order side: `BUY` or `SELL` |
| `--type` | `-t` | Yes | Order type: `MARKET` or `LIMIT` |
| `--quantity` | `-q` | Yes | Order quantity (e.g., 0.001) |
| `--price` | `-p` | No* | Limit price (required for LIMIT orders) |
| `--verbose` | - | No | Enable debug logging |
| `--version` | `-v` | No | Show version and exit |

\* Required when `--type` is `LIMIT`, ignored when `--type` is `MARKET`

### Examples

#### Market BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

#### Market SELL Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01
```

#### Limit BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 95000
```

#### Limit SELL Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 105000
```

#### Verbose Mode (Debug Logging)

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --verbose
```

## Example Output

### Market Order

```
╔═══════════════════════════════════════════╗
║    Binance Futures Trading Bot            ║
║    v1.0.0 | Binance USDT-M Futures Testnet ║
╚═══════════════════════════════════════════╝

ℹ Validating inputs...
✓ Inputs validated successfully

====================================
ORDER SUMMARY
====================================

Symbol      : BTCUSDT
Side        : BUY
Order Type  : MARKET
Quantity    : 0.001
Price       : Market Price

====================================

ℹ Initializing Binance Futures client...
✓ Client initialized successfully

ℹ Sending MARKET BUY order...
Placing BUY order for BTCUSDT... 

====================================
ORDER RESPONSE
====================================

Order ID       : 123456789
Status         : FILLED
Executed Qty   : 0.001
Average Price  : 104235.50
Total Value    : 104.24 USDT

====================================
✓ Order placed and filled successfully.
```

### Validation Error

```
╔═══════════════════════════════════════════╗
║    Binance Futures Trading Bot            ║
║    v1.0.0 | Binance USDT-M Futures Testnet ║
╚═══════════════════════════════════════════╝

ℹ Validating inputs...
✗ Invalid quantity format: 'abc'.

Details:
Quantity must be a valid positive number.
```

### API Error

```
====================================
ORDER FAILED
====================================

✗ Authentication failed

Details:
Invalid API key or permissions

====================================

Tip: Make sure your .env file contains valid API credentials.
     Copy .env.example to .env and fill in your Binance Testnet API keys.
```

## Project Structure

```
trading_bot/
│
├── bot/                          # Core application package
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Environment variable loading and validation
│   ├── exceptions.py             # Custom exception hierarchy
│   ├── logging_config.py         # Logging setup and configuration
│   ├── validators.py             # Input validation functions
│   ├── client.py                 # Binance API client wrapper
│   └── orders.py                 # Order placement and formatting logic
│
├── logs/                         # Log files directory (auto-created)
│   └── trading_bot.log           # Application logs
│
├── cli.py                        # Main CLI entry point
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### File Descriptions

| File | Responsibility |
|------|---------------|
| `cli.py` | Main entry point: parses arguments, validates inputs, executes orders, prints output |
| `bot/__init__.py` | Package initialization with version info |
| `bot/config.py` | Loads environment variables, validates configuration |
| `bot/exceptions.py` | Custom exception hierarchy for precise error handling |
| `bot/logging_config.py` | Configures rotating file and console logging |
| `bot/validators.py` | Validates all CLI inputs (symbol, side, type, quantity, price) |
| `bot/client.py` | Binance API client: authentication, order placement |
| `bot/orders.py` | Order execution logic and output formatting |
| `.env.example` | Template showing required environment variables |
| `.gitignore` | Excludes sensitive files and cache from version control |
| `requirements.txt` | Project dependencies with pinned versions |

## Architecture

The application follows clean architecture principles:

```
CLI Layer (cli.py)
    ↓
Validation Layer (validators.py)
    ↓
Service Layer (orders.py)
    ↓
Client Layer (client.py)
    ↓
External API (Binance Futures Testnet)
```

### Key Design Decisions

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: The client is passed to order functions for testability
3. **Custom Exceptions**: Hierarchical exceptions enable precise error handling
4. **Logging Integration**: All modules use a shared logger for consistency
5. **Type Safety**: Full type hints improve code clarity and enable static analysis

## Assumptions

1. **Testnet Only**: This application is designed for Binance Futures Testnet (`testnet.binancefuture.com`)
2. **USDT-Margined**: Only USDT-margined futures are supported (symbols ending in USDT)
3. **API Keys Required**: Valid Binance Testnet API credentials are required for operation
4. **Network Access**: Internet connectivity is required to reach the Binance API
5. **Python 3.8+**: The application requires Python 3.8 or newer for type hint support
6. **Not for Production Trading**: This is a demonstration/testnet application, not production trading software

## Error Handling

The application handles the following error scenarios gracefully:

| Error Type | User Message | Logged Information |
|------------|-------------|-------------------|
| Invalid Input | Clear validation message | Field name, invalid value, reason |
| Missing Credentials | Setup instructions | ConfigError with missing variables |
| API Authentication | Authentication failed | Status code, response body |
| Network Timeout | Connection failed | Timeout details, retry attempts |
| Order Rejection | Order rejected | Error code, rejection reason |
| Unexpected Error | Generic error message | Full exception traceback |

## Logging

Logs are stored in `logs/trading_bot.log` with the following format:

```
2026-06-27 10:22:01 | INFO     | trading_bot | Sending MARKET BUY order | Symbol: BTCUSDT | Qty=0.001
2026-06-27 10:22:02 | INFO     | trading_bot | Response received | Order ID: 123456789 | Status: FILLED
2026-06-27 10:22:02 | INFO     | trading_bot | Order Filled | Qty: 0.001 | AvgPrice: 104235.50
```

Log files are automatically rotated at 5MB, keeping up to 3 backup files.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-binance | 1.0.27 | Binance API client |
| python-dotenv | 1.0.1 | Environment variable management |
| rich | 13.9.4 | Enhanced CLI output |
| requests | 2.32.3 | HTTP client |
| urllib3 | 2.3.0 | HTTP client dependency |

## License

This project is for educational and assessment purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

## Author

Suryansh Dev
