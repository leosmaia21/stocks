import streamlit as st
import pandas as pd
from api_service import get_trading_212_portfolio, get_trading_212_orders
from auth import save_user_api_key

def show_trading_212_page():
    """Display the Trading 212 page"""
    st.title("📱 Trading 212 Portfolio")
    
    # Settings section
    with st.expander("⚙️ Settings"):
        st.write("**Trading 212 API Credentials Configuration**")
        st.caption("Your credentials are stored securely in Supabase and never exposed in the UI.")
        
        current_creds = st.session_state.get('trading_212_api_key')
        # Handle both old format (string) and new format (dict)
        if isinstance(current_creds, dict):
            key_status = "✅ Configured" if current_creds.get('key_id') else "❌ Not configured"
        else:
            key_status = "❌ Not configured"
        st.write(f"Status: {key_status}")
        
        # Environment selector
        env = st.radio(
            "Environment",
            options=["demo", "live"],
            index=0 if st.session_state.get('trading_212_env', 'live') == 'demo' else 1,
            help="Use 'demo' for testing, 'live' for real trading"
        )
        st.session_state.trading_212_env = env
        
        with st.form("api_key_form"):
            api_key = st.text_input(
                "Trading 212 API Key", 
                type="password",
                placeholder="Enter your Trading 212 API Key",
                help="Get your API key from Trading 212 Settings → API (Beta)"
            )
            save_button = st.form_submit_button("💾 Save API Key")
            
            if save_button and api_key:
                user_id = st.session_state.user.id
                # Store in key_id field, secret can be empty
                success, message = save_user_api_key(user_id, api_key, '')
                
                if success:
                    st.session_state.trading_212_api_key = {'key_id': api_key, 'secret': ''}
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.divider()
        st.info("""
        **How to get your Trading 212 API Key:**
        1. Log in to Trading 212
        2. Go to Settings → API (Beta)
        3. Generate a new API key
        4. Copy the entire key and paste it above
        
        **Environment:** Choose 'demo' for testing with paper trading, or 'live' for real trading.
        
        **Security:** Your API key is encrypted and stored in Supabase with Row Level Security (RLS).
        """)
        """)
    
    # Add refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Check if API credentials are configured
    api_creds = st.session_state.get('trading_212_api_key')
    if not api_creds or not isinstance(api_creds, dict) or not api_creds.get('key_id'):
        st.warning("⚠️ Please configure your Trading 212 API key in Settings above to view your portfolio.")
        return
    
    with st.spinner("Fetching portfolio data..."):
        portfolio_data, error = get_trading_212_portfolio()
        
        if error:
            st.error(error)
            st.info("""
            **How to get your Trading 212 API Key:**
            1. Log in to Trading 212
            2. Go to Settings → API (Beta)
            3. Generate a new API key
            4. Add it to your `.env` file as `TRADING_212_API_KEY=your_key`
            
            **Note:** Use the live API endpoint for real trading, or demo for testing.
            """)
        elif portfolio_data:
            positions = portfolio_data.get('positions', [])
            cash = portfolio_data.get('cash', {})
            
            # Display cash balance
            st.header("💰 Account Balance")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_cash = cash.get('total', 0)
                st.metric("Total Cash", f"${total_cash:,.2f}")
            
            with col2:
                free_cash = cash.get('free', 0)
                st.metric("Free Cash", f"${free_cash:,.2f}")
            
            with col3:
                invested = sum(pos.get('currentPrice', 0) * pos.get('quantity', 0) for pos in positions)
                st.metric("Invested", f"${invested:,.2f}")
            
            # Display positions
            st.header("📊 Current Positions")
            
            if positions and len(positions) > 0:
                # Prepare data for display
                positions_data = []
                for pos in positions:
                    ticker = pos.get('ticker', 'N/A')
                    quantity = pos.get('quantity', 0)
                    avg_price = pos.get('averagePrice', 0)
                    current_price = pos.get('currentPrice', 0)
                    pnl = pos.get('ppl', 0)
                    
                    total_value = current_price * quantity
                    pnl_percent = (pnl / (avg_price * quantity) * 100) if avg_price * quantity > 0 else 0
                    
                    positions_data.append({
                        'Ticker': ticker,
                        'Quantity': quantity,
                        'Avg Price': f"${avg_price:.2f}",
                        'Current Price': f"${current_price:.2f}",
                        'Total Value': f"${total_value:.2f}",
                        'P&L': f"${pnl:.2f}",
                        'P&L %': f"{pnl_percent:.2f}%"
                    })
                
                # Create DataFrame
                df = pd.DataFrame(positions_data)
                st.dataframe(df, use_container_width=True)
                
                # Show detailed view
                st.subheader("Position Details")
                for pos in positions:
                    ticker = pos.get('ticker', 'N/A')
                    with st.expander(f"📈 {ticker}"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.metric("Quantity", pos.get('quantity', 0))
                            st.metric("Average Price", f"${pos.get('averagePrice', 0):.2f}")
                            st.metric("Current Price", f"${pos.get('currentPrice', 0):.2f}")
                        
                        with col_b:
                            pnl = pos.get('ppl', 0)
                            st.metric("P&L", f"${pnl:.2f}", delta=f"{pnl:.2f}")
                            
                            max_buy = pos.get('maxBuy', 'N/A')
                            max_sell = pos.get('maxSell', 'N/A')
                            st.write(f"**Max Buy:** {max_buy}")
                            st.write(f"**Max Sell:** {max_sell}")
            else:
                st.info("No open positions found.")
            
            # Display recent orders
            st.header("📋 Recent Orders")
            orders_data, orders_error = get_trading_212_orders()
            
            if orders_error:
                st.error(orders_error)
            elif orders_data:
                if isinstance(orders_data, list) and len(orders_data) > 0:
                    orders_list = []
                    for order in orders_data[:10]:  # Show last 10 orders
                        orders_list.append({
                            'Date': order.get('dateCreated', 'N/A'),
                            'Ticker': order.get('ticker', 'N/A'),
                            'Type': order.get('type', 'N/A'),
                            'Quantity': order.get('quantity', 0),
                            'Price': f"${order.get('fillPrice', 0):.2f}",
                            'Status': order.get('status', 'N/A')
                        })
                    
                    df_orders = pd.DataFrame(orders_list)
                    st.dataframe(df_orders, use_container_width=True)
                else:
                    st.info("No recent orders found.")
        else:
            st.warning("No data returned from Trading 212.")
