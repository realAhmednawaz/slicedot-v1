import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import os

# --- 1. TERMINAL ARCHITECTURE ---
st.set_page_config(layout="wide", page_title="AXIANT | Institutional Grade", page_icon="⚡")

# Institutional Neon-Dark CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #010101; color: #d1d5db; font-family: 'JetBrains Mono', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f2937; width: 280px !important; }
    
    /* Density Overhaul */
    .block-container { padding: 1rem 2rem !important; }
    .terminal-row { display: flex; justify-content: space-between; border-bottom: 1px solid #1f2937; padding: 4px 0; font-size: 0.8rem; }
    .impact-high { color: #ef4444; font-weight: bold; }
    .impact-low { color: #10b981; font-weight: bold; }
    
    /* Ticker Tape Neon Pulse */
    .tape-item { border-left: 2px solid #00f2ff; padding-left: 10px; margin-right: 20px; }
    
    /* Branding */
    .brand-header { font-size: 2rem; font-weight: 900; color: #00f2ff; letter-spacing: -2px; line-height: 1; }
    
    /* Clutter Removal */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ORCHESTRATION ---
@st.cache_data(ttl=30)
def get_institutional_data():
    assets = {
        "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD",
        "DOW 30": "^DJI", "NASDAQ 100": "^IXIC",
        "SENSEX": "^BSESN", "NSE: RELIANCE": "RELIANCE.NS",
        "GOLD": "GC=F", "BRENT CRUDE": "BZ=F"
    }
    data = []
    for name, ticker in assets.items():
        try:
            t = yf.Ticker(ticker).fast_info
            change = ((t['last_price'] - t['previous_close']) / t['previous_close']) * 100
            data.append({"Name": name, "Price": t['last_price'], "Change": change})
        except: continue
    return data

# --- 3. GLOBAL HEADER (LOGO & TAPE) ---
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    logo_path = "image_611249.png" # Path to your logo
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=180)
    else:
        st.markdown("<div class='brand-header'>AXIANT</div>", unsafe_allow_html=True)

with h_col2:
    m_data = get_institutional_data()
    tape_cols = st.columns(len(m_data))
    for i, m in enumerate(m_data):
        c = "#10b981" if m['Change'] > 0 else "#ef4444"
        tape_cols[i].markdown(f"""<div class='tape-item'><small>{m['Name']}</small><br><strong style='color:{c}'>{m['Price']:,.2f}</strong></div>""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 0.5rem 0; border-color: #1f2937;'>", unsafe_allow_html=True)

# --- 4. SIDEBAR COMMANDS ---
with st.sidebar:
    st.markdown("### 🖥️ TERMINAL CTRL")
    st.caption("NODE_ID: AX-PRIME-01")
    
    with st.expander("💼 PORTFOLIO CONFIG", expanded=True):
        p_input = st.text_area("DEPLOY TICKERS", "NVDA, TSLA, BTC-USD, AAPL, MSFT", height=100)
        p_list = [x.strip() for x in p_input.split(",")]
    
    st.divider()
    st.subheader("⚡ SIMULATION ENGINE")
    scenario = st.select_slider("RISK LEVEL", ["MINIMAL", "ELEVATED", "BLACK SWAN", "TOTAL COLLAPSE"])
    st.button("EXECUTE SCENARIO", use_container_width=True)
    
    st.divider()
    st.markdown("### 🛠️ SUPPORT")
    st.info("Direct line to Axiant Quant Desk: +1-800-AXI-DATA")

# --- 5. THE WORKSPACE (TRIPLE COLUMN) ---
c1, c2, c3 = st.columns([1, 2, 0.8])

with c1:
    st.markdown("#### 📡 THE WIRE")
    wire_data = [
        ("MACRO", "Fed signals pause in rate hikes", "HIGH"),
        ("TECH", "Nvidia Blackwell production ramped", "MED"),
        ("CRYPTO", "SEC reviews spot ETH staking", "HIGH"),
        ("NSE", "Reliance Retail IPO rumors", "MED"),
        ("GEO", "Trade corridor stabilization", "LOW")
    ]
    for tag, msg, imp in wire_data:
        color = "#ef4444" if imp == "HIGH" else "#f59e0b" if imp == "MED" else "#10b981"
        st.markdown(f"""
            <div class='terminal-row'>
                <span><span style='color:{color}'>●</span> {tag}</span>
                <span style='color:#6b7280;'>{msg}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### 🧠 AI SUGGESTIONS")
    st.success("HEDGE: BUY GLD (GOLD) TO OFFSET TECH")
    st.warning("REDUCE: OVEREXPOSURE IN SEMICONDUCTORS")

with c2:
    st.markdown("#### 📊 PERFORMANCE ANALYTICS")
    try:
        hist = yf.download(p_list, period="1mo")['Close']
        fig = go.Figure()
        for t in p_list:
            if t in hist:
                y_norm = (hist[t] / hist[t].dropna().iloc[0]) * 100
                fig.add_trace(go.Scatter(x=hist.index, y=y_norm, name=t, line=dict(width=1.5)))
        
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=400, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("DATA SYNC ERROR")
    
    st.markdown(f"#### ⚠️ RISK REPORT: {scenario}")
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("PORTFOLIO BETA", "1.42", "+0.05")
    r_col2.metric("VaR (95%)", "-4.1%", "-0.2%")
    r_col3.metric("SHARPE RATIO", "2.1", "STABLE")

with c3:
    st.markdown("#### 🌍 MARKET DESK")
    for m in m_data:
        color = "ticker-up" if m['Change'] > 0 else "ticker-down"
        st.markdown(f"""
            <div class='terminal-row'>
                <span style='color:#9ca3af;'>{m['Name']}</span>
                <span class='{color}'>{m['Price']:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🔮 AI FORECAST")
    st.markdown("BTC Target (7D): **$78,500**")
    st.markdown("NVDA Target (7D): **$920.00**")

# --- 6. SYSTEM FOOTER ---
st.markdown("<hr style='border-color: #1f2937;'>", unsafe_allow_html=True)
st.caption("AXIANT v6.0 // SECURE NODE ACTIVE // PROPRIETARY INFRASTRUCTURE")







