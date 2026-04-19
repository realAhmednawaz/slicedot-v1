import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os

# --- AXIANT ENGINE CONFIG ---
st.set_page_config(layout="wide", page_title="AXIANT | Terminal")

# Hide Streamlit's default menu for a cleaner "App" look
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# Dark Theme Injection
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .news-box { border-left: 3px solid #00f2ff; padding-left: 15px; margin-bottom: 20px; background: #161b22; padding: 10px; border-radius: 0 5px 5px 0; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_logo, col_text = st.columns([1, 4])

with col_logo:
    # Safety Check for Logo
    logo_file = "Axiant_Logo.png" # Make sure this matches your GitHub file exactly!
    if os.path.exists(logo_file):
        st.image(Image.open(logo_file), width=120)
    else:
        st.markdown("### [AXIANT]")

with col_text:
    st.title("AXIANT INTELLIGENCE")
    st.caption(f"LIVE TERMINAL FEED | {datetime.now().strftime('%H:%M:%S')} UTC")

st.divider()

# --- THE SPLIT SCREEN ENGINE ---
col_news, col_portfolio = st.columns([1, 1], gap="large")

with col_news:
    st.subheader("📡 Live News Wire")
    try:
        r = requests.get("https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC", timeout=5)
        soup = BeautifulSoup(r.content, features="xml")
        items = soup.findAll('item')[:8]
        for i in items:
            with st.container():
                st.markdown(f"""<div class="news-box">
                    <strong>{i.title.text}</strong><br>
                    <small>{i.pubDate.text[5:16]}</small>
                </div>""", unsafe_allow_html=True)
    except:
        st.error("News Feed Offline. Attempting Reconnect...")

with col_portfolio:
    st.subheader("📈 Active Portfolio")
    # Default Tickers
    watch_list = ["AAPL", "BTC-USD", "RELIANCE.NS", "NVDA"]
    
    try:
        # Get data for the last 5 days
        data = yf.download(watch_list, period="5d", interval="1h")['Close']
        
        # Display individual metrics
        m_cols = st.columns(len(watch_list))
        for idx, ticker in enumerate(watch_list):
            current_price = data[ticker].iloc[-1]
            prev_price = data[ticker].iloc[-2]
            delta = ((current_price - prev_price) / prev_price) * 100
            m_cols[idx].metric(ticker, f"${current_price:.2f}", f"{delta:.2f}%")
        
        # Portfolio Chart
        fig = go.Figure()
        for ticker in watch_list:
            fig.add_trace(go.Scatter(x=data.index, y=data[ticker], name=ticker))
        
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Portfolio Feed Delayed. Waiting for Market Data.")

st.markdown("---")
st.caption("AXIANT SYSTEMS // NODE: GLOBAL-01 // NO UNAUTHORIZED ACCESS")









