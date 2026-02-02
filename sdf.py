import streamlit as st
from datetime import datetime, timedelta
from api_service import get_stock_price, get_earnings_calendar

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

def show_earnings_page():
    """Display the earnings calendar page"""
    st.title("📊 Earnings Calendar")
    
    # Stock price and earnings section - using form so Enter key works
    with st.form("stock_search_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker = st.text_input("Enter Stock Ticker", placeholder="e.g., AAPL, MSFT, GOOGL").upper()
        with col2:
            st.write("")
            st.write("")
            search_button = st.form_submit_button("Search", type="primary")
    
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
                    # Estimate next earnings date based on the most recent report
                    # Usually earnings are reported quarterly (about 90 days apart)
                    today = datetime.now()
                    most_recent = None
                    
                    for report in data:
                        report_date_str = report.get('date')
                        if report_date_str:
                            try:
                                report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
                                if most_recent is None:
                                    most_recent = report
                                else:
                                    most_recent_date = datetime.strptime(most_recent.get('date'), '%Y-%m-%d')
                                    if report_date > most_recent_date:
                                        most_recent = report
                            except ValueError:
                                pass
                    
                    # Display estimated next earnings date if we have recent data
                    if most_recent:
                        most_recent_date = datetime.strptime(most_recent.get('date'), '%Y-%m-%d')
                        
                        # Calculate average days between earnings if we have multiple reports
                        if len(data) >= 2:
                            sorted_data = sorted(data, key=lambda x: x.get('date', ''), reverse=True)
                            try:
                                date1 = datetime.strptime(sorted_data[0].get('date'), '%Y-%m-%d')
                                date2 = datetime.strptime(sorted_data[1].get('date'), '%Y-%m-%d')
                                days_between = (date1 - date2).days
                            except:
                                days_between = 90  # Default to 90 days (quarterly)
                        else:
                            days_between = 90
                        
                        # Estimate next earnings date
                        estimated_next_date = most_recent_date + timedelta(days=days_between)
                        
                        # Only show if it's in the future
                        if estimated_next_date > today:
                            st.info("🔔 Estimated Next Quarterly Earnings Release")
                            st.caption(f"⚠️ Based on {days_between}-day pattern from recent earnings. Actual date may vary.")
                            col_x, col_y = st.columns(2)
                            with col_x:
                                st.metric("📆 Estimated Date", estimated_next_date.strftime('%Y-%m-%d'))
                            with col_y:
                                days_until = (estimated_next_date - today).days
                                st.metric("⏱️ Days Until", f"{days_until} days")
                            st.divider()
                    
                    st.subheader("Historical Earnings Reports")
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
