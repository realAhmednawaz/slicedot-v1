import streamlit as st
import requests
import json

st.set_page_config(page_title="Slicedot V1", layout="wide")

st.title("Slicedot | Live Macro Risk Simulation")
st.markdown("Stress-testing institutional portfolios against real-time prediction market probabilities.")
st.divider()

@st.cache_data(ttl=60) # Caches the data for 60 seconds so you don't spam the API
def fetch_macro_event():
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    macro_keywords = ["fed", "rate", "inflation", "gdp", "election", "sec", "treasury", "oil", "china", "taiwan"]
    
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
            outcomes = json.loads(primary_market.get('outcomes', '[]'))
            prices = json.loads(primary_market.get('outcomePrices', '[]'))
            p1 = float(prices[0])
            p2 = float(prices[1]) if len(prices) > 1 else 0.0
            
            if 0.05 < p1 < 0.95: 
                return title, p1, p2
        except:
            continue
            
    return None, 0, 0

# --- UI LAYOUT ---
with st.sidebar:
    st.header("Simulation Parameters")
    portfolio_value = st.number_input("Portfolio Value ($)", value=10000000, step=1000000)
    impact_yes = st.slider("Expected Impact if YES (%)", min_value=-20.0, max_value=20.0, value=-5.0, step=0.5) / 100
    impact_no = st.slider("Expected Impact if NO (%)", min_value=-20.0, max_value=20.0, value=2.0, step=0.5) / 100

event_title, prob_yes, prob_no = fetch_macro_event()

if event_title:
    st.subheader(f"Live Risk Event: {event_title}")
    
    col1, col2 = st.columns(2)
    col1.metric("Probability: YES", f"{prob_yes * 100:.1f}%")
    col2.metric("Probability: NO", f"{prob_no * 100:.1f}%")
    
    st.divider()
    
    # Math
    expected_value_impact = (prob_yes * impact_yes) + (prob_no * impact_no)
    projected_exposure = portfolio_value * expected_value_impact
    
    st.subheader("Real-Time Portfolio Exposure")
    
    col3, col4 = st.columns(2)
    col3.metric("Expected Impact (%)", f"{expected_value_impact * 100:.2f}%")
    
    if projected_exposure < 0:
        col4.metric("Projected Value at Risk", f"-${abs(projected_exposure):,.2f}")
    else:
        col4.metric("Projected Gain Exposure", f"+${projected_exposure:,.2f}")
        
    st.info("Simulation powered by live Gamma API prediction markets.")
else:
    st.error("Could not fetch active macro markets. Please try again.")