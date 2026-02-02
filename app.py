import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
from auth import init_session_state, show_login_page, logout

load_dotenv()

# Initialize session state
init_session_state()

# API Ninja configuration
API_NINJA_KEY = os.getenv("API_NINJA_KEY")

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

def show_main_app():
    """Display the main application after login"""
    st.title("📊 Stocks Dashboard")
    
    # Display user info
    with st.sidebar:
        st.write(f"👤 Logged in as: {st.session_state.user.email}")
        if st.button("Logout"):
            logout()
            st.rerun()
    
    # Stock price and earnings section
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker", placeholder="e.g., AAPL, MSFT, GOOGL").upper()
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Search", type="primary")
    
    if search_button and ticker:
        with st.spinner(f"Fetching data for {ticker}..."):
            # Get current stock price
            st.header("💰 Current Price")
            price_data, price_error = get_stock_price(ticker)
            
            if price_error:
                st.error(price_error)
            elif price_data:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Ticker", price_data.get('ticker', 'N/A'))
                with col_b:
                    st.metric("Current Price", f"${price_data.get('price', 'N/A'):.2f}" if price_data.get('price') else 'N/A')
                with col_c:
                    if price_data.get('volume'):
                        st.metric("Volume", f"{price_data.get('volume'):,}")
            
            # Get earnings calendar
            st.header("📅 Earnings Calendar")
            data, error = get_earnings_calendar(ticker)
            
            if error:
                st.error(error)
            elif data:
                if len(data) > 0:
                    st.success(f"Found {len(data)} earnings report(s) for {ticker}")
                    
                    # Display each earnings report
                    for idx, report in enumerate(data):
                        earnings_date = report.get('date', 'N/A')
                        actual_eps = report.get('actual_eps', 'N/A')
                        estimated_eps = report.get('estimated_eps', 'N/A')
                        
                        with st.expander(f"📊 {earnings_date} - Q{idx + 1}", expanded=idx==0):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.metric("Earnings Date", earnings_date)
                                st.metric("Estimated EPS", f"${estimated_eps}" if estimated_eps != 'N/A' else 'N/A')
                                if report.get('estimated_revenue'):
                                    st.metric("Estimated Revenue", f"${report.get('estimated_revenue'):,.0f}")
                            
                            with col_b:
                                st.metric("Actual EPS", f"${actual_eps}" if actual_eps != 'N/A' else 'N/A')
                                if actual_eps != 'N/A' and estimated_eps != 'N/A':
                                    diff = actual_eps - estimated_eps
                                    st.metric("Beat/Miss EPS", f"${diff:.2f}", delta=diff)
                                if report.get('actual_revenue'):
                                    st.metric("Actual Revenue", f"${report.get('actual_revenue'):,.0f}")
                else:
                    st.warning(f"No earnings data found for {ticker}")
            else:
                st.warning(f"No data returned for {ticker}")
    
    elif search_button and not ticker:
        st.warning("Please enter a stock ticker")

# Main app logic
if not st.session_state.authenticated:
    show_login_page()
else:
    show_main_app()
