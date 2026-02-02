import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API Ninja configuration
API_NINJA_KEY = os.getenv("API_NINJA_KEY")

# Trading 212 configuration
TRADING_212_API_KEY = os.getenv("TRADING_212_API_KEY")

def get_stock_price(ticker: str):
    """Get stock price from API Ninja"""
    if not API_NINJA_KEY:
        return None, "⚠️ API_NINJA_KEY not found in .env file"
    
    api_url = f"https://api.api-ninjas.com/v1/stockprice?ticker={ticker}"
    
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_NINJA_KEY})
        if response.status_code == requests.codes.ok:
            data = response.json()
            return data, None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {str(e)}"

def get_earnings_calendar(ticker: str):
    """Get stock earnings/quarter release date from API Ninja"""
    if not API_NINJA_KEY:
        return None, "⚠️ API_NINJA_KEY not found in .env file"
    
    url = f"https://api.api-ninjas.com/v1/earningscalendar?ticker={ticker}"
    headers = {"X-Api-Key": API_NINJA_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data, None
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {str(e)}"

def get_trading_212_portfolio():
    """Get portfolio data from Trading 212"""
    import streamlit as st
    
    # Get API credentials from session state (stored securely in Supabase)
    api_creds = st.session_state.get('trading_212_api_key')
    
    # Handle both old format (string) and new format (dict)
    if not api_creds or not isinstance(api_creds, dict) or not api_creds.get('key_id') or not api_creds.get('secret'):
        return None, "⚠️ Trading 212 API credentials not configured. Please add them in Settings."
    
    # Get environment (demo or live)
    env = st.session_state.get('trading_212_env', 'live')
    base_url = f"https://{env}.trading212.com/api/v0"
    
    # Combine key_id and secret for authorization
    api_key = f"{api_creds['key_id']}:{api_creds['secret']}".strip()
    
    headers = {
        "Authorization": api_key
    }
    
    try:
        # Get account cash
        cash_response = requests.get(f"{base_url}/equity/account/cash", headers=headers, timeout=10)
        
        # Get all positions
        positions_response = requests.get(f"{base_url}/equity/portfolio", headers=headers, timeout=10)
        
        if positions_response.status_code == 200:
            positions = positions_response.json()
            cash = cash_response.json() if cash_response.status_code == 200 else {}
            return {"positions": positions, "cash": cash}, None
        elif positions_response.status_code == 401:
            return None, f"❌ Authentication failed (401). Please check your API Key ID and Secret."
        else:
            return None, f"Error: {positions_response.status_code} - {positions_response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {str(e)}"

def get_trading_212_orders():
    """Get order history from Trading 212"""
    import streamlit as st
    
    # Get API credentials from session state (stored securely in Supabase)
    api_creds = st.session_state.get('trading_212_api_key')
    
    # Handle both old format (string) and new format (dict)
    if not api_creds or not isinstance(api_creds, dict) or not api_creds.get('key_id') or not api_creds.get('secret'):
        return None, "⚠️ Trading 212 API credentials not configured. Please add them in Settings."
    
    # Get environment (demo or live)
    env = st.session_state.get('trading_212_env', 'live')
    base_url = f"https://{env}.trading212.com/api/v0"
    
    # Combine key_id and secret for authorization
    api_key = f"{api_creds['key_id']}:{api_creds['secret']}".strip()
    
    headers = {
        "Authorization": api_key
    }
    
    try:
        response = requests.get(f"{base_url}/equity/history/orders", headers=headers, params={"limit": 50}, timeout=10)
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 401:
            return None, f"❌ Authentication failed (401). Please check your API Key ID and Secret."
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {str(e)}"
