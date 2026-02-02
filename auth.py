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

def login(email: str, password: str):
    """Login with Supabase"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.authenticated = True
        st.session_state.user = response.user
        return True, "Login successful!"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def logout():
    """Logout from Supabase"""
    try:
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
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
