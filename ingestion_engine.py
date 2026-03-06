import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel, ValidationError, Field
from datetime import datetime
from supabase import create_client, Client

# --- 1. ENVIRONMENT VARIABLES ---
# GitHub Actions will inject these securely. NEVER hardcode them here.
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("FATAL: Supabase credentials missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. SCHEMAS & VALIDATION ---
class StockDataSchema(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    timestamp: datetime
    price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)

def get_secure_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

# --- 3. THE CORE EXECUTION ---
def fetch_and_store(symbol: str, api_url: str):
    session = get_secure_session()
    print(f"[{datetime.now()}] Fetching data for {symbol}...")
    
    try:
        response = session.get(api_url, timeout=5)
        response.raise_for_status()
        
        # Simulate mapping API response to our schema (adjust based on your actual API)
        raw_data = response.json() 
        validated_data = StockDataSchema(**raw_data)
        
        # Push to Supabase
        clean_payload = validated_data.model_dump()
        # Ensure your Pydantic datetime is converted to ISO format for Postgres
        clean_payload['timestamp'] = clean_payload['timestamp'].isoformat() 
        
        supabase.table("clean_market_data").insert(clean_payload).execute()
        print(f"SUCCESS: {symbol} stored safely.")

    except requests.exceptions.RequestException as e:
        print(f"NETWORK ERROR on {symbol}: {e}")
    except ValidationError as e:
        error_payload = {"api_endpoint": api_url, "error_details": str(e.errors()), "status": "investigate"}
        supabase.table("quarantine_log").insert(error_payload).execute()
        print(f"QUARANTINED: Invalid data for {symbol}.")
    except Exception as e:
        print(f"FATAL SYSTEM ERROR: {e}")

# --- 4. THE INITIATOR ---
if __name__ == "__main__":
    # Define the assets you want Slicedot to track
    # Replace these placeholder URLs with your actual financial API endpoints
    TARGETS = {
        "AAPL": "https://api.example.com/v1/stock/AAPL",
        "MSFT": "https://api.example.com/v1/stock/MSFT"
    }
    
    for ticker, url in TARGETS.items():
        fetch_and_store(ticker, url)
    
    print("Ingestion cycle complete.")
