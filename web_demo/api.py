"""
FastAPI Web Demo for Binance Futures Trading Bot

A REST API that wraps the existing CLI bot logic.
Place this file inside a `web_demo/` folder in your project.

Run locally:
    uvicorn web_demo.api:app --reload --port 8000

Deploy to Render/Railway:
    Set start command: uvicorn web_demo.api:app --host 0.0.0.0 --port $PORT
"""

import sys
import os

# Add parent directory to path so we can import the bot package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal

from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.validators import validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price
from bot.logging_config import setup_logging
from bot.exceptions import TradingBotError

# Setup logging
setup_logging()

app = FastAPI(
    title="Binance Futures Trading Bot API",
    description="REST API wrapper for the Binance USDT-M Futures Testnet Trading Bot",
    version="1.0.0",
)

# CORS (allow all for demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------- MODELS -------------------

class OrderRequest(BaseModel):
    symbol: str = Field(..., example="BTCUSDT", description="Trading pair symbol")
    side: Literal["BUY", "SELL"] = Field(..., example="BUY", description="Order side")
    order_type: Literal["MARKET", "LIMIT"] = Field(..., example="MARKET", description="Order type")
    quantity: float = Field(..., gt=0, example=0.001, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, example=95000, description="Limit price (required for LIMIT orders)")


class OrderResponse(BaseModel):
    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    total_value: Optional[float] = None
    message: str


# ------------------- ENDPOINTS -------------------

@app.get("/")
def root():
    return {
        "name": "Binance Futures Trading Bot API",
        "version": "1.0.0",
        "environment": "Binance USDT-M Futures Testnet",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/order", response_model=OrderResponse)
def create_order(order: OrderRequest):
    """Place a new futures order on the Binance Testnet."""
    try:
        # Validate inputs
        validate_symbol(order.symbol)
        validate_side(order.side)
        validate_order_type(order.order_type)
        qty_float = validate_quantity(str(order.quantity))

        price_float = None
        if order.order_type == "LIMIT":
            if order.price is None:
                raise TradingBotError("Price is required for LIMIT orders.")
            price_float = validate_price(str(order.price))

        # Place order
        client = BinanceFuturesClient()
        response = place_order(
            client=client,
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=qty_float,
            price=price_float,
        )

        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", "0")
        avg_price = response.get("avgPrice", "0")
        total_value = float(executed_qty) * float(avg_price) if executed_qty and avg_price else 0

        return OrderResponse(
            success=True,
            order_id=order_id,
            status=status,
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=qty_float,
            price=price_float,
            executed_qty=executed_qty,
            avg_price=avg_price,
            total_value=round(total_value, 2) if total_value else None,
            message=f"Order placed successfully. Status: {status}",
        )

    except TradingBotError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
