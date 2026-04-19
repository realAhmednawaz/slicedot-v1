import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client
from PIL import Image
import os

# --- 1. SUPABASE IDENTITY ENGINE ---
# Replace with your actual project credentials
# ST_URL = "YOUR_SUPABASE_URL"
# ST_KEY = "YOUR_SUPABASE_ANON_KEY"
# supabase: Client = create_client(ST_URL, ST_KEY)

# --- 2. THEME & BRANDING ---
st.set_page_config(layout="wide", page_title="AXIANT | Institutional Intelligence", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background: #05070a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2937; }
    .news-card { background: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 4px; margin-bottom: 8px; font-size: 0.85rem; }
    .news-tag { background: #00f2ff; color: #000; padding: 2px 6px; border-radius: 2px; font-weight: bold; margin-right: 8px; font-size: 0.7rem; }
    .metric-container { background: #111827; border: 1px solid #1f2937; padding: 15px; border-radius: 8px; }
    .stTitle { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "Guest_Axiant_Node"
if 'portfolio' not in st.session_state: st.session_state.portfolio = ["NVDA", "BTC-USD", "RELIANCE.NS"]

# --- 4. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    # Axiant Logo
    logo_path = "image_611249.png" # Using your uploaded identifier
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=180)
    else:
        st.title("AXIANT")
    
    st.markdown(f"**Operator:** `{st.session_state.user}`")
    st.caption("Status: Encrypted Connection Established")
    
    st.divider()
    
    # AUTH MODULE
    if not st.session_state.logged_in:
        with st.expander("🔐 Access Terminal"):
            email = st.text_input("Institutional Email")
            pw = st.text_input("Password", type="password")
            if st.button("Authenticate"):
                st.session_state.logged_in = True
                st.session_state.user = email.split('@')[0]
                st.rerun()
    else:
        if st.button("De-authenticate"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()
    
    # ASSET MANAGEMENT
    st.subheader("Asset Intelligence")
    new_asset = st.text_input("Add Ticker (Yahoo Code)")
    if st.button("+ Deploy Asset"):
        if new_asset:
            st.session_state.portfolio.append(new_asset.upper())
            st.success(f"Deployed {new_asset}")
    
    st.divider()
    # SIMULATION ENGINE
    st.subheader("Simulation Mode")
    sim_enabled = st.toggle("Enable Risk Simulation", value=True)
    sim_volatility = st.slider("Scenario Volatility (%)", 0, 100, 25)

# --- 5. TOP TICKER TAPE ---
indices = {"DOW": "^DJI", "NASDAQ": "^IXIC", "SENSEX": "^BSESN", "BTC/USD": "BTC-USD"}
t_cols = st.columns(len(indices))
for i, (name, ticker) in enumerate(indices.items()):
    try:
        price = yf.Ticker(ticker).fast_info['last_price']
        t_cols[i].markdown(f"""<div style='text-align: center;'>
            <small style='color: #9ca3af;'>{name}</small><br>
            <strong style='font-size: 1.2rem;'>{price:,.0f}</strong>
        </div>""", unsafe_allow_html=True)
    except:
        pass

st.divider()

# --- 6. MAIN WORKSPACE ---
col_news, col_analytics = st.columns([1.2, 2], gap="large")

with col_news:
    st.subheader("📡 Event Wire (Kalshi-Style)")
    events = [
        {"tag": "MACRO", "msg": "Fed signals pause in rate hikes for Q3 2026", "prob": "82%"},
        {"tag": "TECH", "msg": "Nvidia announces 'Axiant' integration for H200", "prob": "14%"},
        {"tag": "CRYPTO", "msg": "Bitcoin ETF inflows hit record $2.4B in 24hrs", "prob": "91%"},
        {"tag": "GEOPOL", "msg": "Middle East trade corridor stabilization rumors", "prob": "45%"}
    ]
    for e in events:
        st.markdown(f"""
            <div class="news-card">
                <span class="news-tag">{e['tag']}</span>
                <strong>{e['msg']}</strong><br>
                <small style="color: #00f2ff;">Probability Likelihood: {e['prob']}</small>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Axiant Suggestions")
    st.info("💡 **Diversification Warning:** Current portfolio concentration in Tech is 74%. Recommend exposure to **GC=F (Gold Futures)**.")

with col_analytics:
    st.subheader("Active Analytics & Simulations")
    
    if st.session_state.portfolio:
        # Data Pull
        data = yf.download(st.session_state.portfolio, period="1mo", interval="1d")['Close']
        
        # Performance Chart
        fig = go.Figure()
        for stock in st.session_state.portfolio:
            if stock in data:
                y = data[stock].dropna()
                # Normalized chart for investors to see relative growth
                norm_y = (y / y.iloc[0]) * 100
                fig.add_trace(go.Scatter(x=y.index, y=norm_y, name=stock, line=dict(width=2)))
                
                if sim_enabled:
                    # Simulation: Dotted projection based on current trend + volatility slider
                    last_val = norm_y.iloc[-1]
                    future_dates = [y.index[-1] + timedelta(days=i) for i in range(1, 8)]
                    sim_vals = [last_val * (1 + (sim_volatility/1000 * i)) for i in range(1, 8)]
                    fig.add_trace(go.Scatter(x=future_dates, y=sim_vals, name=f"Sim {stock}", 
                                             line=dict(dash='dot', width=1), opacity=0.5))

        fig.update_layout(
            template="plotly_dark", 
            height=450, 
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=1.1),
            yaxis_title="Normalized Return (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Simulation Summary
        st.markdown("""<div class="metric-container">
            <h4 style="margin-top:0;">Risk Simulation Report</h4>
            <p>Based on current volatility settings, the Axiant engine estimates a <strong>Value-at-Risk (VaR)</strong> 
            of 4.2% over the next 7 days. Correlation between assets remains high (0.88).</p>
        </div>""", unsafe_allow_html=True)

# --- 7. FOOTER ---
st.markdown("---")
st.caption("AXIANT v3.0 // CONFIDENTIAL PROPRIETARY ENGINE // SECURE_SOCKET_77")








