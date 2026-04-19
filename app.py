import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import os

# --- 1. SETTINGS & THEME ---
st.set_page_config(layout="wide", page_title="AXIANT | Institutional Intelligence", page_icon="⚡")

# Direct CSS Injection for a Professional Terminal Aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap');
    
    .stApp { background-color: #050505; color: #d1d5db; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f2937; }
    
    /* Terminal UI Components */
    .market-card { background: #111827; border: 1px solid #1f2937; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
    .ticker-up { color: #10b981; font-weight: bold; }
    .ticker-down { color: #ef4444; font-weight: bold; }
    .axiant-header { color: #00f2ff; font-weight: 800; font-size: 1.5rem; letter-spacing: -1px; margin-bottom: 0; }
    
    /* Clean up Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def fetch_terminal_data():
    # Proper Market Names Mapping
    market_map = {
        "BTC-USD": "BITCOIN / USD",
        "ETH-USD": "ETHEREUM / USD",
        "^DJI": "DOW JONES IND.",
        "^IXIC": "NASDAQ COMPOSITE",
        "RELIANCE.NS": "NSE: RELIANCE",
        "GC=F": "COMEX GOLD"
    }
    results = []
    for ticker, name in market_map.items():
        try:
            t = yf.Ticker(ticker).fast_info
            change = ((t['last_price'] - t['previous_close']) / t['previous_close']) * 100
            results.append({
                "Market": name,
                "Price": f"{t['last_price']:,.2f}",
                "Change": change,
                "RawPrice": t['last_price']
            })
        except: continue
    return results

# --- 3. SIDEBAR (BRANDING & COMMANDS) ---
with st.sidebar:
    # 1. LOGO INTEGRATION
    logo_path = "image_611249.png" # Path from your previous successful upload
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), use_container_width=True)
    else:
        st.markdown("<p class='axiant-header'>AXIANT</p>", unsafe_allow_html=True)
    
    st.caption("v5.0 Stable MVP | Institutional Node")
    st.divider()
    
    # 4. BRANDING & SUPPORT
    with st.expander("🛠️ SUPPORT & SYSTEM", expanded=False):
        st.markdown("""
        **System Status:** 🟢 Operational
        **Help:** support@axiant.systems
        **Terminal ID:** AX-77-PRIME
        """)
    
    st.divider()
    st.subheader("Portfolio Control")
    portfolio_input = st.text_area("Tickers", "NVDA, TSLA, BTC-USD", height=70)
    user_portfolio = [x.strip() for x in portfolio_input.split(",")]
    
    st.divider()
    st.subheader("Simulation Engine")
    sim_mode = st.selectbox("Scenario", ["Baseline", "High Volatility", "Market Crash", "Bull Rally"])
    st.button("Run Axiant Simulation", use_container_width=True)

# --- 4. MAIN INTERFACE ---

# TOP MARKET TAPE (Proper Names)
markets = fetch_terminal_data()
tape_cols = st.columns(len(markets))
for i, m in enumerate(markets):
    color_class = "ticker-up" if m['Change'] > 0 else "ticker-down"
    tape_cols[i].markdown(f"""
        <small>{m['Market']}</small><br>
        <span class="{color_class}">{m['Price']}</span>
    """, unsafe_allow_html=True)

st.divider()

col_wire, col_main = st.columns([1, 2], gap="large")

# LEFT: THE WIRE (News/Kalshi Style)
with col_wire:
    st.subheader("📡 Event Wire")
    events = [
        ("MACRO", "Fed signals pause in rate hikes", "88%"),
        ("NSE", "Reliance hits new 52-week high", "92%"),
        ("CRYPTO", "BTC Institutional inflow exceeds $2B", "75%"),
        ("TECH", "AI Hardware demand remains inelastic", "60%")
    ]
    for tag, msg, prob in events:
        st.markdown(f"""
            <div class="market-card">
                <small style="color:#00f2ff; font-weight:bold;">[{tag}]</small> 
                <span style="float:right; font-size:0.7rem;">Likelihood: {prob}</span><br>
                <strong>{msg}</strong>
            </div>
        """, unsafe_allow_html=True)

# RIGHT: ANALYTICS
with col_main:
    st.subheader("📊 Performance & Forecast")
    try:
        hist = yf.download(user_portfolio, period="1mo", interval="1d")['Close']
        fig = go.Figure()
        for ticker in user_portfolio:
            if ticker in hist:
                # Normalization for comparative analysis
                y = hist[ticker].dropna()
                y_norm = (y / y.iloc[0]) * 100
                fig.add_trace(go.Scatter(x=y.index, y=y_norm, name=ticker))
        
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=400, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Data Sync Interrupted. Check Ticker Syntax.")

    # 3. NO BREAKING LINES - Static Risk Summary
    st.markdown(f"### ⚠️ RISK ANALYSIS: {sim_mode.upper()}")
    st.markdown("""
    | Metric | Value | Status |
    | :--- | :--- | :--- |
    | **Portfolio Beta** | 1.24 | High Sensitivity |
    | **VaR (95%)** | -3.8% | Within Limits |
    | **Correlation** | 0.82 | High |
    """)

# --- 5. FOOTER ---
st.markdown("---")
st.caption("AXIANT SYSTEMS // PROPRIETARY INFRASTRUCTURE // SECURE ACCESS ONLY")







