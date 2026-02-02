import streamlit as st
from dotenv import load_dotenv
from auth import init_session_state, show_login_page, logout
from home_page import show_home_page
from earnings_page import show_earnings_page
from trading_212_page import show_trading_212_page

load_dotenv()

# Initialize session state
init_session_state()

# Initialize page selection
if 'page' not in st.session_state:
    st.session_state.page = 'Earnings Calendar'

def show_main_app():
    """Display the main application after login"""
    
    # Sidebar navigation
    with st.sidebar:
        st.write(f"👤 Logged in as: {st.session_state.user.email}")
        if st.button("Logout"):
            logout()
            st.rerun()
        
        st.divider()
        
        # Navigation menu
        st.subheader("📋 Menu")
        page = st.radio(
            "Navigation",
            ["Earnings Calendar", "Trading 212", "Home"],
            index=0 if st.session_state.page == 'Earnings Calendar' else (1 if st.session_state.page == 'Trading 212' else 2),
            label_visibility="collapsed"
        )
        st.session_state.page = page
    
    # Display selected page
    if st.session_state.page == "Earnings Calendar":
        show_earnings_page()
    elif st.session_state.page == "Trading 212":
        show_trading_212_page()
    elif st.session_state.page == "Home":
        show_home_page()

# Main app logic
if not st.session_state.authenticated:
    show_login_page()
else:
    show_main_app()
