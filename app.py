import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Slicedot V2 | Custom Portfolio", layout="wide")

st.title("Slicedot | Live Macro Risk Simulation")
st.markdown("Stress-testing institutional portfolios against real-time prediction market probabilities.")
st.divider()

@st.cache_data(ttl=60)
def fetch_macro_event():
    url = "https://gamma-api.polymarket.com/events?limit=500&active=true&closed=false"
    macro_keywords = ["israel", "iran", "middle east", "gaza", "oil", "saudi", "taiwan", "china", "fed", "rate", "inflation", "gdp"]
    try:
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
    except:
        return None, 0, 0

    for event in events:
        title = event.get('title', '')
        if not any(kw in title.lower() for kw in macro_keywords):
            continue
        markets = event.get('markets', [])
        if not markets: continue
        primary_market = markets[0]
        try:
            outcomes = json.loads(primary_market.get('outcomes', '





