import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import os

# --- 1. ARCHITECTURAL CONFIG ---
st.set_page_config(layout="wide", page_title="AXIANT | Institutional Terminal", page_icon="⚡")

# Institutional "Glass-Dark" UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background: #020203; color: #d1d5db; font-family: 'JetBrains Mono', monospace; }
    header {visibility: hidden;}
    
    /* Terminal Components */
    .terminal-card { background: #0a0b0d; border: 1px solid #1f2937; padding: 10px; border-radius: 2px; margin-bottom: 10px; }
    .status-tag { color: #00f2ff; font-size: 0.7rem; border: 1px solid #00f2ff; padding: 1px 4px; border-radius: 2px; }
    .price-up { color: #10b981; } .price-down { color: #ef4444; }
    
    /* Sidebar Overhaul */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #1f2937; width: 300px !important; }
    
    /* Hide scrollbars for true terminal feel */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: #1f2937; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (High-Frequency Simulation) ---
def get_market_snapshot():
    tickers = {
        "BTC-USD": "CRYPTO", "ETH-USD": "CRYPTO", 
        "^DJI": "DOW", "^IXIC": "NASDAQ", 
        "GC=F": "GOLD", "RELIANCE.NS": "NSE"
    }
    data = []
    for t, cat in tickers.items():
        try:
            tick = yf.Ticker(t).fast_info
            data.append({"Asset": t.replace("^", ""), "Price": tick['last_price'], "Change": ((tick['last_price'] - tick['previous_close'])/tick['previous_close'])*100, "Type": cat})
        except: continue
    return pd.DataFrame(data)

# --- 3. THE COMMAND SIDEBAR (AXIANT CORE) ---
with st.sidebar:
    # AXIANT BRANDING - ZERO COMPROMISE
    logo_path = "image_611249.png" # Path to your uploaded logo
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), use_container_width=True)
    else:
        st.markdown("<h1 style='color:#00f2ff; margin:0;'>AXIANT</h1>", unsafe_allow_html=True)
    
    st.markdown("<small>INSTITUTIONAL NODE: 0x882A</small>", unsafe_allow_html=True)
    st.divider()
    
    # AUTH & SIMULATION
    with st.expander("👤 USER ACCESS", expanded=False):
        st.text_input("NODE ID", value="ADMIN_77")
        st.button("ENCRYPT SESSION", use_container_width=True)
    
    st.divider()
    st.subheader("PORTFOLIO DEPLOYMENT")
    user_input = st.text_area("TICKER STACK", value="NVDA, TSLA, BTC-USD, RELIANCE.NS", height=100)
    portfolio_list = [x.strip() for x in user_input.split(",")]
    
    st.subheader("SIMULATION PARAMETERS")
    stress_test = st.select_slider("STRESS LEVEL", options=["BASE", "BULL", "BEAR", "BLACK_SWAN"])
    st.button("RUN MONTE CARLO", use_container_width=True)

# --- 4. MAIN TERMINAL LAYOUT ---
# TOP RIBBON: GLOBAL TICKER TAPE
m_data = get_market_snapshot()
tape_cols = st.columns(len(m_data))
for i, row in m_data.iterrows():
    color = "#10b981" if row['Change'] > 0 else "#ef4444"
    tape_cols[i].markdown(f"""
        <div style='border-bottom: 2px solid {color}; padding: 5px;'>
            <small>{row['Asset']}</small><br>
            <strong style='color:{color}'>{row['Price']:,.2f}</strong>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# THREE COLUMN ARCHITECTURE
col_news, col_chart, col_market = st.columns([1, 2, 0.8])

with col_news:
    st.markdown("### 📡 THE WIRE")
    news_items = [
        ("MACRO", "FED DOT PLOT SHIFTS TO HAWKISH", "92%"),
        ("CRYPTO", "SEC APPROVES ETHEREUM STAKING DERIVATIVES", "74%"),
        ("TECH", "AXIANT AI PREDICTS NVDA EARNINGS BEAT", "88%"),
        ("GEO", "OIL PRICES SPIKE ON STRAIT OF HORMUZ TENSION", "51%"),
        ("CORP", "RELIANCE ANNOUNCES NEW GREEN HYDROGEN HUB", "60%")
    ]
    for tag, text, prob in news_items:
        st.markdown(f"""
            <div class="terminal-card">
                <span class="status-tag">{tag}</span> <small>{prob} PROBABILITY</small><br>
                <div style="margin-top:5px; font-weight:bold;">{text}</div>
            </div>
        """, unsafe_allow_html=True)

with col_chart:
    st.markdown("### 📊 PORTFOLIO INTELLIGENCE")
    try:
        hist_data = yf.download(portfolio_list, period="1mo")['Close']
        fig = go.Figure()
        for col in hist_data.columns:
            # Normalized to 100 for institutional comparison
            y_norm = (hist_data[col] / hist_data[col].dropna().iloc[0]) * 100
            fig.add_trace(go.Scatter(x=hist_data.index, y=y_norm, name=col, line=dict(width=1.5)))
        
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=400, margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=1.1),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1f2937")
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("DATA OVERLOAD: CHECK TICKER STRINGS")

    st.markdown("### ⚠️ RISK ANALYSIS")
    st.info(f"SIMULATION MODE: {stress_test} | PORTFOLIO BETA: 1.42 | VAR (95%): -4.1%")

with col_market:
    st.markdown("### 🌍 MARKET DESK")
    st.dataframe(
        m_data.style.applymap(lambda x: 'color: #10b981' if isinstance(x, float) and x > 0 else 'color: #ef4444', subset=['Change']),
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    st.subheader("AXIANT SUGGESTS")
    st.success("HEDGE INITIATED: BUY GLD (GOLD) TO OFFSET TECH VOLATILITY")
    st.error("SELL ALERT: SELL TSLA ON WEAKENING RSI TREND")

# FOOTER
st.markdown("---")
st.caption("AXIANT SYSTEMS // PROPRIETARY INFRASTRUCTURE // UNENCRYPTED ACCESS IS A VIOLATION OF PROTOCOL")







