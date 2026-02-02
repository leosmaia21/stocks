import streamlit as st

def show_home_page():
    """Display the home page"""
    st.title("🏠 Home")
    st.markdown("""
    ### Welcome to Stocks Dashboard
    
    This application helps you track stock information including:
    - 📈 Current stock prices
    - 📅 Earnings calendar and history
    - 🔮 Estimated next earnings dates
    
    **Popular tickers to try:**
    - AAPL (Apple)
    - MSFT (Microsoft)
    - GOOGL (Google)
    - PLTR (Palantir)
    - TSLA (Tesla)
    
    Use the menu on the left to navigate to different sections.
    """)
