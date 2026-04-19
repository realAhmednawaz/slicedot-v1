import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- 1. SESSION STATE & AUTH INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_portfolio' not in st.session_state:
    st.session_state.user_portfolio = ["AAPL", "BTC-USD", "RELIANCE.NS"]
if 'currency' not in st.session_state:
    st.session_state.currency = "USD"
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

# --- 2. THEME & UI INJECTION ---
def apply_theme():
    if st.session_state.theme == "Dark":
        bg, text, accent = "#05070a", "#e0e0e0", "#00f2ff"
    else:
        bg, text, accent = "#ffffff", "#121212", "#005a8d"
    
    st.markdown(f"""
        <style>
        .stApp {{ background: {bg}; color: {text}; }}
        h1, h2, h3 {{ color: {accent} !important; }}
        .stButton>button {{ width: 100%; border-radius: 5px; }}
        .market-card {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border: 1px solid {accent}33; }}
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- 3. LOGIN / SIGNUP OVERLAY ---
if not st.session_state.logged_in:
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.title("AXIANT")
        st.subheader("Institutional Intelligence System")
        st.write("Access the high-frequency terminal for predictive analytics.")
    with col_r:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Enter Terminal"):
                st.session_state.logged_in = True
                st.rerun()
        with tab2:
            st.text_input("Email")
            st.text_input("Set Password", type="password")
            st.button("Create Account")
    st.stop()

# --- 4. NAVIGATION & GLOBAL CONTROLS ---
with st.sidebar:
    st.title("AXIANT")
    st.write(f"User: **Authorized_Node_01**")
    
    # Theme Toggle
    if st.button(f"Switch to {'Light' if st.session_state.theme == 'Dark' else 'Dark'} Mode"):
        st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
        st.rerun()

    # Currency Switcher
    st.session_state.currency = st.selectbox("Base Currency", ["USD", "INR", "EUR", "GBP"])
    
    st.divider()
    
    # Portfolio Management
    st.subheader("Manage Portfolio")
    new_stock = st.text_input("Add Ticker (e.g. TSLA, ETH-USD)")
    if st.button("Add to Axiant"):
        if new_stock and new_stock.upper() not in st.session_state.user_portfolio:
            st.session_state.user_portfolio.append(new_stock.upper())
            st.success(f"Added {new_stock}")
    
    if st.button("Clear Portfolio"):
        st.session_state.user_portfolio = []
        st.rerun()

# --- 5. GLOBAL MARKET TICKERS ---
indices = {
    "DOW JONES": "^DJI", "NASDAQ": "^IXIC", 
    "SENSEX": "^BSESN", "BTC": "BTC-USD"
}
m_cols = st.columns(len(indices))
for i, (name, ticker) in enumerate(indices.items()):
    try:
        val = yf.Ticker(ticker).fast_info['last_price']
        m_cols[i].metric(name, f"{val:,.0f}")
    except:
        m_cols[i].metric(name, "Offline")

st.divider()

# --- 6. PREDICTIVE ANALYTICS & MAIN VIEW ---
col_main, col_intel = st.columns([2, 1])

with col_main:
    st.subheader("Active Portfolio Intelligence")
    if st.session_state.user_portfolio:
        data = yf.download(st.session_state.user_portfolio, period="1mo")['Close']
        fig = go.Figure()
        for stock in st.session_state.user_portfolio:
            if stock in data:
                # Prediction Logic (Linear Projection)
                y = data[stock].dropna()
                if not y.empty:
                    fig.add_trace(go.Scatter(x=y.index, y=y, name=f"{stock} (Actual)"))
                    
                    # Simple Trend Prediction
                    z = np.polyfit(range(len(y)), y, 1)
                    p = np.poly1d(z)
                    future_dates = [y.index[-1] + timedelta(days=i) for i in range(1, 6)]
                    future_preds = [p(len(y) + i) for i in range(1, 6)]
                    fig.add_trace(go.Scatter(x=future_dates, y=future_preds, name=f"{stock} (AI Forecast)", line=dict(dash='dot')))
        
        fig.update_layout(template="plotly_dark" if st.session_state.theme == "Dark" else "plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add stocks in the sidebar to begin analysis.")

with col_intel:
    st.subheader("Axiant Suggestions")
    # Basic Recommendation Engine based on Portfolio
    st.warning("⚠️ DISCLAIMER: Axiant AI predictions are for simulation only. Not financial advice.")
    
    if "NVDA" in st.session_state.user_portfolio or "AAPL" in st.session_state.user_portfolio:
        st.info("💡 **Tech Heavy detected.** Suggesting Diversification: **GLD (Gold)** or **JPM (Financials)**")
    elif "BTC-USD" in st.session_state.user_portfolio:
        st.info("💡 **Crypto exposure.** Suggesting: **COIN** or **MARA** for proxy equity.")
    else:
        st.write("Add assets to generate AI suggestions.")

    st.subheader("Market Status")
    st.write("🟢 NYSE: Open")
    st.write("🔴 NSE: Closed")
    st.write("🟢 CRYPTO: 24/7")

# --- 7. FOOTER ---
st.markdown("---")
st.caption("AXIANT V2.0 // SECURE TERMINAL // UNAUTHORIZED REPLICATION PROHIBITED")









