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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging

st.set_page_config(page_title="Binance Futures Bot", page_icon="📈", layout="centered")

st.title("📈 Binance Futures Trading Bot")
st.caption("USDT-M Futures Testnet | Web Demo")

setup_logging()

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("order_form"):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Symbol", value="BTCUSDT").upper().strip()
        side = st.selectbox("Side", ["BUY", "SELL"])
    with col2:
        order_type = st.selectbox("Type", ["MARKET", "LIMIT"])
        quantity = st.text_input("Quantity", value="0.001")

    price = None
    if order_type == "LIMIT":
        price = st.text_input("Limit Price", value="90000")

    submitted = st.form_submit_button("📤 Send Order")

if submitted:
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        limit_price = None
        if order_type == "LIMIT":
            if not price or not price.strip():
                raise ValueError("Price required for LIMIT orders")
            limit_price = float(price)
            if limit_price <= 0:
                raise ValueError("Price must be positive")

        with st.spinner("Placing order..."):
            client = BinanceFuturesClient()
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": qty,
            }
            if limit_price:
                params["price"] = limit_price

            response = client.client.futures_create_order(**params)

        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        exec_qty = response.get("executedQty", "0")
        avg_price = response.get("avgPrice", "0")

        st.success(f"""
        ✅ Order Placed!
        
        **Order ID:** {order_id}
        **Status:** {status}
        **Qty:** {exec_qty}
        **Avg Price:** {avg_price} USDT
        """)

        st.session_state.history.insert(0, {
            "id": order_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": qty,
            "status": status,
        })

    except ValueError as e:
        st.error(f"❌ Validation Error: {e}")
    except Exception as e:
        st.error(f"❌ Error: {e}")

if st.session_state.history:
    st.divider()
    st.subheader("📊 Recent Orders")
    for h in st.session_state.history[:10]:
        st.write(f"**#{h['id']}** | `{h['symbol']}` | {h['side']} {h['type']} | Status: `{h['status']}`")

st.divider()
st.caption("🔒 Testnet only. API keys from Streamlit Secrets.")