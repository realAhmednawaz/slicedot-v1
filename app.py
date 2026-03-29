import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os

# --- 1. GLOBAL CONFIG & THEME STATE ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'
if 'eye_shield' not in st.session_state:
    st.session_state.eye_shield = False

st.set_page_config(layout="wide", page_title="Clovant | Institutional Terminal")

def toggle_theme():
    st.session_state.theme = 'Light' if st.session_state.theme == 'Dark' else 'Dark'

# --- 2. DYNAMIC CSS (Gradients & Eye Shield) ---
theme_css = ""
if st.session_state.theme == 'Dark':
    theme_css = """
    <style>
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #051a05 100%); color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #00ff0022; }
    h1, h2, h3 { color: #00ff00 !important; font-family: 'Inter', sans-serif; letter-spacing: -0.5px; }
    .stMetric { border: 1px solid #00ff0033; background: rgba(0, 255, 0, 0.05); border-radius: 4px; }
    </style>
    """
else:
    theme_css = """
    <style>
    .stApp { background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%); color: #1e1e1e; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    h1, h2, h3 { color: #004080 !important; }
    .stMetric { border: 1px solid #00408022; background: #ffffff; border-radius: 4px; }
    </style>
    """

eye_shield_css = """
<style>
.stApp::after { content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(255, 191, 0, 0.06); pointer-events: none; z-index: 9999; }
</style>
""" if st.session_state.eye_shield else ""

st.markdown(theme_css + eye_shield_css, unsafe_allow_html=True)

# --- 3. LOGO & HEADER SECTION ---
# Create a header with 2 columns to push the logo to the right
head_left, head_right = st.columns([4, 1])

with head_left:
    st.title("CLOVANT SYSTEMS")
    st.caption("Institutional Simulation & Validation Engine | Terminal v1.0")

with head_right:
    # Look for the logo file
    logo_path = "Clovant_Logo.jpg" # Ensure this filename matches your file
    if os.path.exists(logo_path):
        image = Image.open(logo_path)
        st.image(image, use_container_width=True)
    else:
        st.warning("Logo file missing")

st.divider()

# --- 4. DATA ENGINES ---
def get_risk_score(news_items):
    score = 0
    weights = {"war": -35, "conflict": -30, "iran": -25, "inflation": -15, "growth": 20, "rate cut": 25}
    for item in news_items:
        title = item['title'].lower()
        for word, val in weights.items():
            if word in title: score += val
    return max(min(score, 100), -100)

def scrape_news():
    url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.content, features="xml")
        return [{"title": i.title.text, "link": i.link.text, "date": i.pubDate.text} for i in soup.findAll('item')[:6]]
    except: return []

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Terminal Control")
    st.button(f"🌓 Mode: {st.session_state.theme}", on_click=toggle_theme, use_container_width=True)
    st.checkbox("🛡️ Eye Comfort Shield", key="eye_shield")
    
    st.divider()
    st.subheader("Asset Monitor")
    ticker_list = st.text_input("Portfolio Tickers", "RELIANCE.NS, TCS.NS, GC=F, BTC-USD")
    tickers = [t.strip() for t in ticker_list.split(",")]

# --- 6. MAIN DASHBOARD ---
news_data = scrape_news()
risk_val = get_risk_score(news_data)

# Top Metrics Row
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Systemic Risk Index", f"{risk_val}%", delta="UNSTABLE" if risk_val < 0 else "STABLE")
with m2:
    st.metric("Active Assets", len(tickers))
with m3:
    st.metric("Last Sync", datetime.now().strftime("%H:%M:%S"))

st.write("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Performance Analytics")
    try:
        df = yf.download(tickers, period="1mo", interval="1d")['Close']
        df_norm = (df / df.iloc[0]) * 100 # Normalize to 100
        
        fig = go.Figure()
        for col in df_norm.columns:
            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col, line=dict(width=2)))
        
        fig.update_layout(
            template="plotly_dark" if st.session_state.theme == 'Dark' else "plotly_white",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=0), height=400,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Market Data Feed Offline. Check Tickers.")

with col_right:
    st.subheader("Current Scenario")
    for n in news_data:
        with st.expander(n['title'][:50] + "..."):
            st.write(n['title'])
            st.caption(n['date'])
            st.markdown(f"[View Impact Analysis]({n['link']})")

# --- 7. FOOTER ---
st.markdown("---")
st.caption("Clovant Systems | Secure Node: Jamnagar-01 | Proprietary & Confidential")









