import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state
def init_session_state():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'trading_212_api_key' not in st.session_state:
        st.session_state.trading_212_api_key = None

def get_user_client():
    """Get a Supabase client with the current user's access token for RLS"""
    access_token = st.session_state.get('access_token')
    if access_token:
        # Create a client with the user's access token so RLS policies work
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.auth.set_session(access_token, st.session_state.get('refresh_token', ''))
        return client
    return supabase

def get_user_api_key(user_id: str):
    """Fetch user's Trading 212 API credentials from Supabase"""
    try:
        client = get_user_client()
        response = client.table('user_api_keys').select('trading_212_key_id, trading_212_secret').eq('user_id', user_id).execute()
        if response.data and len(response.data) > 0:
            return {
                'key_id': response.data[0].get('trading_212_key_id'),
                'secret': response.data[0].get('trading_212_secret')
            }
        return None
    except Exception as e:
        st.error(f"Error fetching API key: {str(e)}")
        return None

def save_user_api_key(user_id: str, key_id: str, secret: str):
    """Save user's Trading 212 API credentials to Supabase"""
    try:
        client = get_user_client()
        # Check if record exists
        existing = client.table('user_api_keys').select('*').eq('user_id', user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing record
            response = client.table('user_api_keys').update({
                'trading_212_key_id': key_id,
                'trading_212_secret': secret
            }).eq('user_id', user_id).execute()
        else:
            # Insert new record
            response = client.table('user_api_keys').insert({
                'user_id': user_id,
                'trading_212_key_id': key_id,
                'trading_212_secret': secret
            }).execute()
        
        return True, "API credentials saved successfully!"
    except Exception as e:
        return False, f"Error saving API credentials: {str(e)}"

def login(email: str, password: str):
    """Login with Supabase"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        st.session_state.authenticated = True
        st.session_state.user = response.user
        st.session_state.access_token = response.session.access_token
        st.session_state.refresh_token = response.session.refresh_token
        
        # Fetch user's API credentials from Supabase
        if response.user and response.user.id:
            api_creds = get_user_api_key(response.user.id)
            st.session_state.trading_212_api_key = api_creds
        
        return True, "Login successful!"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def logout():
    """Logout from Supabase"""
    try:
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.trading_212_api_key = None
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")

def show_login_page():
    """Display the login page"""
    st.title("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
