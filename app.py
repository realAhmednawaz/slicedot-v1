import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="AXIANT | Strategic Intelligence")

if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'

def toggle_theme():
    st.session_state.theme = 'Light' if st.session_state.theme == 'Dark' else 'Dark'

# --- 2. AXIANT VISUAL IDENTITY (CSS) ---
theme_css = ""
if st.session_state.theme == 'Dark':
    theme_css = """
    <style>
    .stApp { background: #0a0a0a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Monaco', monospace; }
    .stMetric { border: 1px solid #222; background: #161616; padding: 10px; border-radius: 5px; }
    /* News Feed Styling */
    .news-card { padding: 10px; border-bottom: 1px solid #222; margin-bottom: 5px; }
    .news-card:hover { background: #1a1a1a; }
    </style>
    """
else:
    theme_css = """
    <style>
    .stApp { background: #f4f7f6; color: #1e1e1e; }
    h1, h2, h3 { color: #005a8d !important; }
    .stMetric { border: 1px solid #ddd; background: #ffffff; padding: 10px; }
    </style>
    """
st.markdown(theme_css, unsafe_allow_html=True)

# --- 3. DATA ENGINES ---
@st.cache_data(ttl=300)
def fetch_live_news():
    """Scrapes financial news for the news column"""
    url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.content, features="xml")
        return [{"title": i.title.text, "link": i.link.text, "time": i.pubDate.text[17:22]} for i in soup.findAll('item')[:12]]
    except:
        return [{"title": "Data Feed Interrupted", "link": "#", "time": "00:00"}]

def get_portfolio_data(tickers):
    """Fetches real-time price and change %"""
    data = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            info = stock.fast_info
            price = info['last_price']
            change = ((price - info['previous_close']) / info['previous_close']) * 100
            data.append({"Ticker": t, "Price": round(price, 2), "Change %": round(change, 2)})
        except:
            continue
    return pd.DataFrame(data)

# --- 4. HEADER & NAVIGATION ---
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title("AXIANT SYSTEMS")
    st.caption(f"LIVE TERMINAL // SESSION: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

with col_h2:
    # Look for the new Axiant Logo
    logo_path = "Axiant_Logo.png" 
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=150)
    else:
        st.subheader("AXIANT")

st.divider()

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Terminal Control")
    st.button(f"Switch to {st.session_state.theme} Mode", on_click=toggle_theme)
    
    st.divider()
    st.subheader("Watchlist Configuration")
    user_tickers = st.text_input("Enter Tickers (CSV)", "RELIANCE.NS, BTC-USD, NVDA, TSLA, GC=F")
    ticker_list = [x.strip() for x in user_tickers.split(",")]
    
    st.info("System Status: Operational")

# --- 6. SPLIT-SCREEN INTERFACE ---
col_news, col_portfolio = st.columns([1, 1], gap="large")

# --- LEFT SIDE: LIVE NEWS FEED ---
with col_news:
    st.subheader("🌐 Global Intelligence Feed")
    news_items = fetch_live_news()
    
    for item in news_items:
        st.markdown(f"""
        <div class="news-card">
            <small style="color: #00d4ff;">[{item['time']}]</small><br>
            <a href="{item['link']}" style="text-decoration: none; color: inherit; font-weight: bold;">
                {item['title']}
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- RIGHT SIDE: LIVE PORTFOLIO ---
with col_portfolio:
    st.subheader("📊 Live Portfolio Monitor")
    
    portfolio_df = get_portfolio_data(ticker_list)
    
    if not portfolio_df.empty:
        # Display as a clean table first
        st.table(portfolio_df)
        
        # Display a mini-chart for the first ticker
        st.write(f"Chart Analysis: {ticker_list[0]}")
        hist = yf.download(ticker_list[0], period="1d", interval="15m")
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Input valid tickers in the sidebar to populate portfolio.")

# --- 7. FOOTER ---
st.markdown("---")
st.caption("AXIANT | Proprietary Intelligence Engine | encrypted_node_882")









