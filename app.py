import streamlit as st
import pandas as pd
import requests
import json
from supabase import create_client, Client

st.set_page_config(page_title="Slicedot V2 | Secure Portal", layout="wide")

# --- 1. DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Database connection failed. Check your Streamlit secrets.")
    st.stop()

# --- 2. AUTHENTICATION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 3. THE LOGIN VAULT ---
with st.sidebar:
    st.header("Institutional Login")
    if st.session_state.user is None:
        login_email = st.text_input("Corporate Email")
        login_password = st.text_input("Password", type="password")
        if st.button("Authenticate"):
            try:
                response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = response.user
                st.success("Authentication successful.")
                st.rerun()
            except Exception as e:
                st.error("Invalid credentials. Access Denied.")
        st.divider()
        st.caption("Awaiting secure login to load risk engine.")
        st.stop() # THIS IS THE KILL SWITCH.
    else:
        st.success(f"Active Session: {st.session_state.user.email}")
        if st.button("Sign Out"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()
        st.divider()

# --- 4. CORE RISK ENGINE (ONLY RUNS IF LOGGED IN) ---
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
            outcomes = json.loads(primary_market.get('outcomes', '[]'))
            prices = json.loads(primary_market.get('outcomePrices', '[]'))
            p1 = float(prices[0])
            p2 = float(prices[1]) if len(prices) > 1 else 0.0
            if 0.05 < p1 < 0.95:
                return title, p1, p2
        except:
            continue
    return None, 0, 0

with st.sidebar:
    st.header("1. Portfolio Ingestion")
    uploaded_file = st.file_uploader("Upload Portfolio CSV", type=['csv'])
    st.caption("Required columns: Ticker, Sector, Value")
    st.divider()
    
    st.header("2. Scenario Assumptions")
    impact_yes = st.slider("Target Sector Impact if YES (%)", min_value=-20.0, max_value=20.0, value=-5.0, step=0.5) / 100
    impact_no = st.slider("Target Sector Impact if NO (%)", min_value=-20.0, max_value=20.0, value=2.0, step=0.5) / 100

event_title, prob_yes, prob_no = fetch_macro_event()

if event_title:
    st.subheader(f"Live Risk Event: {event_title}")
    col1, col2 = st.columns(2)
    col1.metric("Probability: YES", f"{prob_yes * 100:.1f}%")
    col2.metric("Probability: NO", f"{prob_no * 100:.1f}%")
    st.divider()

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if 'Value' in df.columns and 'Sector' in df.columns:
            st.subheader("Parsed Portfolio Data")
            st.dataframe(df, use_container_width=True)
            
            total_portfolio_value = df['Value'].sum()
            
            st.markdown("### Risk Calculation")
            target_sector = st.selectbox("Select Sector Most Exposed to this Event", df['Sector'].unique())
            exposed_value = df[df['Sector'] == target_sector]['Value'].sum()

            expected_value_impact = (prob_yes * impact_yes) + (prob_no * impact_no)
            projected_exposure = exposed_value * expected_value_impact
            
            col3, col4, col5 = st.columns(3)
            col3.metric("Total Book Value", f"${total_portfolio_value:,.2f}")
            col4.metric(f"Exposed Capital ({target_sector})", f"${exposed_value:,.2f}")
            
            if projected_exposure < 0:
                col5.metric("Projected Value at Risk", f"-${abs(projected_exposure):,.2f}")
            else:
                col5.metric("Projected Gain Exposure", f"+${projected_exposure:,.2f}")
        else:
            st.error("Upload Failed: The CSV must contain columns named exactly 'Ticker', 'Sector', and 'Value'.")
    else:
        st.warning("Awaiting Portfolio Upload. Please drag and drop a CSV file into the sidebar.")
        
    st.info("Simulation powered by live Gamma API prediction markets.")
else:
    st.error("Could not fetch active macro markets. Please try again.")








