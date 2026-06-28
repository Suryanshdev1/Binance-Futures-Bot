"""
Streamlit Web Demo for Binance Futures Trading Bot

A clean web interface that wraps the existing CLI bot logic.
Place this file inside a `web_demo/` folder in your project.

Run locally:
    streamlit run web_demo/app.py

Deploy to Render/Railway:
    Set start command: streamlit run web_demo/app.py --server.port $PORT
"""

import sys
import os

# Add parent directory to path so we can import the bot package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.validators import validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price
from bot.logging_config import setup_logging
from bot.exceptions import TradingBotError

# Page config
st.set_page_config(
    page_title="Binance Futures Trading Bot",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for a polished look
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F0B90B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #F0B90B;
        color: #1a1a1a;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #d4a009;
        color: #1a1a1a;
    }
    .success-box {
        background-color: #1a2f1a;
        border-left: 4px solid #00C851;
        padding: 1rem;
        border-radius: 4px;
    }
    .error-box {
        background-color: #2f1a1a;
        border-left: 4px solid #ff4444;
        padding: 1rem;
        border-radius: 4px;
    }
    .info-box {
        background-color: #1a1a2f;
        border-left: 4px solid #33b5e5;
        padding: 1rem;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📈 Binance Futures Trading Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">USDT-M Futures Testnet | Web Demo</div>', unsafe_allow_html=True)

st.divider()

# Initialize logging
setup_logging()

# Session state for order history
if "order_history" not in st.session_state:
    st.session_state.order_history = []

# --- ORDER FORM ---
st.subheader("🚀 Place Order")

col1, col2 = st.columns(2)

with col1:
    symbol = st.text_input("Symbol", value="BTCUSDT", placeholder="e.g. BTCUSDT, ETHUSDT").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])

with col2:
    quantity = st.text_input("Quantity", value="0.001", placeholder="e.g. 0.001")
    price = st.text_input("Price (Limit Only)", value="", placeholder="Required for LIMIT orders")
    price_disabled = order_type == "MARKET"

st.divider()

# Place Order Button
if st.button("📤 Send Order", type="primary"):
    try:
        # Validate inputs
        validate_symbol(symbol)
        validate_side(side)
        validate_order_type(order_type)
        qty_float = validate_quantity(quantity)

        price_float = None
        if order_type == "LIMIT":
            if not price or not price.strip():
                raise TradingBotError("Price is required for LIMIT orders.")
            price_float = validate_price(price)

        # Show order summary
        st.markdown("""
            <div class="info-box">
                <b>📝 Order Summary</b><br>
                Symbol: <code>{}</code> &nbsp;|&nbsp;
                Side: <code>{}</code> &nbsp;|&nbsp;
                Type: <code>{}</code> &nbsp;|&nbsp;
                Qty: <code>{}</code>
            </div>
        """.format(symbol, side, order_type, qty_float), unsafe_allow_html=True)

        with st.spinner("Connecting to Binance Testnet..."):
            client = BinanceFuturesClient()
            response = place_order(
                client=client,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=qty_float,
                price=price_float,
            )

        # Success response
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", "N/A")
        avg_price = response.get("avgPrice", "N/A")
        total_value = float(executed_qty) * float(avg_price) if executed_qty != "N/A" and avg_price != "N/A" else 0

        st.markdown(f"""
            <div class="success-box">
                <b>✅ Order Placed Successfully</b><br><br>
                <b>Order ID:</b> <code>{order_id}</code><br>
                <b>Status:</b> <code>{status}</code><br>
                <b>Executed Qty:</b> <code>{executed_qty}</code><br>
                <b>Average Price:</b> <code>{avg_price}</code> USDT<br>
                <b>Total Value:</b> <code>{total_value:.2f}</code> USDT
            </div>
        """, unsafe_allow_html=True)

        # Add to history
        st.session_state.order_history.insert(0, {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": qty_float,
            "price": price_float if price_float else "Market",
            "status": status,
            "order_id": order_id,
        })

    except TradingBotError as e:
        st.markdown(f"""
            <div class="error-box">
                <b>❌ Order Failed</b><br><br>
                {e}
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
            <div class="error-box">
                <b>❌ Unexpected Error</b><br><br>
                {e}
            </div>
        """, unsafe_allow_html=True)

# --- ORDER HISTORY ---
if st.session_state.order_history:
    st.divider()
    st.subheader("📊 Recent Orders")

    for i, order in enumerate(st.session_state.order_history[:10]):
        with st.container():
            cols = st.columns([2, 1, 1, 1, 2])
            cols[0].markdown(f"**#{order['order_id']}** — `{order['symbol']}`")
            cols[1].markdown(f"`{order['side']}`")
            cols[2].markdown(f"`{order['type']}`")
            cols[3].markdown(f"`{order['status']}`")
            cols[4].markdown(f"Qty: `{order['qty']}` | Price: `{order['price']}`")
            st.divider()

# --- FOOTER ---
st.divider()
st.caption("""
    💡 This is a **Testnet** demo. No real money is used.  
    🔒 API keys are loaded from your `.env` file and never exposed in the UI.
""")
