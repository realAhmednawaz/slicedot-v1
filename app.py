import streamlit as st
import pandas as pd
import requests
import json
from supabase import create_client, Client

st.set_page_config(page_title="Slicedot V3 | Enterprise Engine", layout="wide")

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
        st.stop() # THE KILL SWITCH
    else:
        st.success(f"Active Session: {st.session_state.user.email}")
        if st.button("Sign Out"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()
        st.divider()

# --- 4. FIRM INITIALIZATION ---
user_id = st.session_state.user.id
user_email = st.session_state.user.email
try:
    firm_check = supabase.table('firms').select('*').eq('firm_id', user_id).execute()
    if not firm_check.data:
        firm_name = f"{user_email.split('@')[0].capitalize()} Capital"
        supabase.table('firms').insert([{'firm_id': user_id, 'firm_name': firm_name, 'contact_email': user_email}]).execute()
except Exception as e:
    st.sidebar.error(f"Firm Setup Error: {e}") # SILENCER REMOVED

# --- 5. CORE RISK ENGINE ---
st.title("Slicedot | Live Macro Risk Simulation")
st.markdown("Stress-testing institutional portfolios against real-time prediction market probabilities.")
st.divider()

@st.cache_data(ttl=60)
def fetch_macro_event():
    url = "https://gamma-api.polymarket.com/events?limit=500&active=true&closed=false"
    macro_keywords = macro_keywords = ["israel", "iran", "middle east", "gaza"]
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
    st.header("1. Data Ingestion")
    
    saved_ports = supabase.table('portfolios').select('*').eq('firm_id', user_id).execute()
    port_options = {"Upload New CSV": None}
    if saved_ports.data:
        for p in saved_ports.data:
            port_options[p['portfolio_name']] = p['portfolio_id']
            
    selected_mode = st.selectbox("Select Portfolio Source", list(port_options.keys()))
    
    df = None
    
    if selected_mode == "Upload New CSV":
        uploaded_file = st.file_uploader("Upload Portfolio CSV", type=['csv'])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            new_port_name = st.text_input("Name this Portfolio to Save (e.g., Q3 Energy)")
            if st.button("Save to Vault") and new_port_name:
                try:
                    port_res = supabase.table('portfolios').insert([{
                        'firm_id': user_id, 
                        'portfolio_name': new_port_name, 
                        'total_value': float(df['Value'].sum())
                    }]).execute()
                    new_p_id = port_res.data[0]['portfolio_id']
                    
                    records = []
                    for _, row in df.iterrows():
                        records.append({
                            'portfolio_id': new_p_id,
                            'ticker': str(row['Ticker']),
                            'sector': str(row['Sector']),
                            'capital_allocated': float(row['Value'])
                        })
                    supabase.table('positions').insert(records).execute()
                    st.success(f"'{new_port_name}' secured in database. Switch mode above to load.")
                except Exception as e:
                    st.error(f"Database Error: {e}") # SILENCER REMOVED
    else:
        p_id_to_load = port_options[selected_mode]
        positions_res = supabase.table('positions').select('*').eq('portfolio_id', p_id_to_load).execute()
        if positions_res.data:
            df = pd.DataFrame(positions_res.data)
            df = df.rename(columns={'ticker': 'Ticker', 'sector': 'Sector', 'capital_allocated': 'Value'})
        
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

    if df is not None and 'Value' in df.columns and 'Sector' in df.columns:
        st.subheader("Parsed Portfolio Data")
        st.dataframe(df[['Ticker', 'Sector', 'Value']], use_container_width=True)
        
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
        if selected_mode == "Upload New CSV":
            st.warning("Awaiting Portfolio Upload. Please drag and drop a CSV file into the sidebar.")
        else:
            st.warning("Portfolio is empty or failed to load.")
        
    st.info("Simulation powered by live Gamma API prediction markets.")
else:
    st.error("Could not fetch active macro markets. Please try again.")

    import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. THE SAFE CONNECTION
# Unlike GitHub Actions, this runs locally or on your Streamlit deployment server.
# Streamlit has its own secrets management (st.secrets) that you must use in production.
@st.cache_resource
def init_connection():
    # Use st.secrets in production, or fallback to local .env for testing
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
    # CRITICAL: Use the ANON key here, NEVER the service_role key used in GitHub Actions.
    key = st.secrets.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_ANON_KEY"))
    
    if not url or not key:
        st.error("FATAL: Database credentials missing.")
        st.stop()
        
    return create_client(url, key)

supabase = init_connection()

# 2. THE SURGICAL EXTRACTION (Cached)
# @st.cache_data prevents Streamlit from hitting your database every time a user types in a text box.
# It holds the downloaded data in memory for exactly 1 hour (3600 seconds).
@st.cache_data(ttl=3600)
def fetch_market_data(symbol: str, days_back: int = 30):
    try:
        # We only query the exact symbol we need, ordered by time.
        # This is why we built indexes in PostgreSQL earlier.
        response = supabase.table("clean_market_data") \
            .select("timestamp, price, volume") \
            .eq("symbol", symbol.upper()) \
            .order("timestamp", desc=True) \
            .limit(days_back) \
            .execute()
            
        data = response.data
        if not data:
            return pd.DataFrame() # Return empty dataframe if no data exists
            
        # 3. THE FINANCIAL TRANSFORMATION
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(ascending=True, inplace=True) # Chronological order for charting
        
        return df
        
    except Exception as e:
        st.error(f"Database Query Failed: {e}")
        return pd.DataFrame()

# --- Execution in your Streamlit UI ---
st.title("Slicedot Investment Simulator")

# User Input
target_symbol = st.text_input("Enter Ticker Symbol (e.g., AAPL)", value="AAPL")

if target_symbol:
    with st.spinner(f"Pulling verified data for {target_symbol}..."):
        # This function executes instantly after the first load because of the cache.
        market_df = fetch_market_data(target_symbol, days_back=90)
        
    if not market_df.empty:
        st.success(f"Successfully loaded {len(market_df)} days of clean data.")
        st.dataframe(market_df.tail()) # Show the last 5 days
        # st.line_chart(market_df['price']) # Instant visualization
    else:
        st.warning(f"No data found for {target_symbol}. Check your ingestion engine logs.")









