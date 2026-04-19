import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os

# --- AXIANT ENGINE CONFIG ---
st.set_page_config(layout="wide", page_title="AXIANT | Terminal", page_icon="📈")

# Advanced UI Styling
st.markdown("""
    <style>
    .stApp { background: #05070a; color: #e0e0e0; }
    h1, h2, h3 { color: #00f2ff !important; font-family: 'Inter', sans-serif; font-weight: 800; }
    
    /* Glassmorphism News Cards */
    .news-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #00f2ff;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 4px;
        transition: 0.3s;
    }
    .news-card:hover { background: rgba(0, 242, 255, 0.08); }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 5])
with col_logo:
    # Set this to the exact name of your uploaded logo
    logo_file = "image_609d48.png" 
    if os.path.exists(logo_file):
        st.image(Image.open(logo_file), width=100)
    else:
        st.write("### AXIANT")

with col_text:
    st.title("AXIANT INTELLIGENCE")
    st.caption(f"QUANTITATIVE TERMINAL // SESSION ACTIVE: {datetime.now().strftime('%H:%M:%S')} UTC")

st.divider()

# --- DATA FETCHING ---
def get_safe_news():
    try:
        # Using a backup RSS feed for reliability
        r = requests.get("https://news.google.com/rss/search?q=finance+markets", timeout=10)
        soup = BeautifulSoup(r.content, features="xml")
        return [{"t": i.title.text, "l": i.link.text, "d": i.pubDate.text[5:16]} for i in soup.findAll('item')[:10]]
    except:
        return []

# --- MAIN INTERFACE ---
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📡 Live News Wire")
    news = get_safe_news()
    if news:
        for n in news:
            st.markdown(f"""<div class="news-card">
                <a href="{n['l']}" style="color:white; text-decoration:none;"><strong>{n['t']}</strong></a><br>
                <small style="color:#00f2ff;">{n['d']}</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Re-synchronizing News Feed...")

with col_right:
    st.subheader("📊 Portfolio Analysis")
    watch = ["BTC-USD", "NVDA", "AAPL", "RELIANCE.NS"]
    
    try:
        # Use a longer period to avoid 'NaN' on weekends
        raw_data = yf.download(watch, period="7d", interval="1h")['Close']
        
        # Display Metrics
        m_cols = st.columns(len(watch))
        for idx, ticker in enumerate(watch):
            # Clean out NaNs for calculation
            clean_series = raw_data[ticker].dropna()
            if not clean_series.empty:
                current = clean_series.iloc[-1]
                prev = clean_series.iloc[-2]
                change = ((current - prev) / prev) * 100
                m_cols[idx].metric(ticker, f"${current:,.2f}", f"{change:+.2f}%")
            else:
                m_cols[idx].metric(ticker, "Market Closed")

        # Portfolio Chart (Normalized for comparison)
        fig = go.Figure()
        for ticker in watch:
            t_data = raw_data[ticker].dropna()
            if not t_data.empty:
                # Normalize data to start at 100 for better comparison
                norm = (t_data / t_data.iloc[0]) * 100
                fig.add_trace(go.Scatter(x=norm.index, y=norm, name=ticker, line=dict(width=2)))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=450,
            legend=dict(orientation="h", y=1.1),
            yaxis_title="Relative Performance (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Data Sync Error: {e}")

st.markdown("---")
st.caption("AXIANT SYSTEMS // NODE: GLOBAL-01 // ENCRYPTED CONNECTION")









