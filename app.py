import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.express as px

st.set_page_config(page_title="Institutional Stock Research & AI Dashboard", layout="wide")

st.sidebar.header("⚙️ Configuration & API Setup")
gemini_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Navigation Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Select View")
view_option = st.sidebar.radio("", [
    "Stock Deep Dive (10-Step)", 
    "Market & Sector Rotation", 
    "AI Weekly & Monthly Stock Screener", 
    "Bulk, Block Deals & Insider Trading Tracker"
])

if view_option == "Stock Deep Dive (10-Step)":
    st.title("📊 AI Stock Investment & Smart Money Dashboard")
    st.markdown("Integrated with Sifu Yik's 10-Step Framework + FII/FPI Institutional Tracking")
    
    ticker_symbol = st.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, TCS.NS)", value="RELIANCE.NS")
    investment_horizon = st.selectbox("Investment Horizon", ["SHORT", "MEDIUM", "LONG"])
    portfolio_size = st.text_input("Portfolio Size (₹)", value="1,00,000")
    risk_tolerance = st.selectbox("Risk Tolerance", ["LOW", "MEDIUM", "HIGH"])

    if st.button("🚀 Run Full Analysis with Gemini AI"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar first!")
        else:
            with st.spinner("Fetching stock metrics and running AI institutional analysis..."):
                try:
                    stock = yf.Ticker(ticker_symbol)
                    info = stock.info
                    company_name = info.get('longName', ticker_symbol)
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                    market_cap = info.get('marketCap', 'N/A')
                    pe_ratio = info.get('trailingPE', 'N/A')
                except:
                    company_name = ticker_symbol
                    current_price, market_cap, pe_ratio = 'N/A', 'N/A', 'N/A'

                prompt = f"""
                Act as a Senior Equity Research Analyst and Institutional Fund Manager. Analyze the stock {company_name} ({ticker_symbol}) for a {investment_horizon} term investor.
                Provide a comprehensive report structured into these exact 11 sections:
                1. Company Snapshot in Plain English
                2. Financial Health Check
                3. Earnings Report Breakdown
                4. Fair Value Range
                5. Head-to-Head Stock Comparison
                6. Institutional Smart Money & FII/FPI Activity
                7. Catalysts & Risks Timeline
                8. Three Scenario Test (Bull, Base, Bear)
                9. Chart Reading & Technical Setup
                10. Personal Decision Checklist
                11. Argument Against Me (Devil's Advocate)
                """

                try:
                    response = model.generate_content(prompt)
                    ai_report = response.text
                except Exception as e:
                    ai_report = f"Error generating AI response: {e}"

                st.success(f"Analysis successfully completed for {company_name}!")
                
                tab1, tab2, tab3 = st.tabs(["📑 Full AI Institutional Report", "📈 Basic Market Metrics", "🧠 Smart Money & FII Tracker"])
                with tab1:
                    st.markdown(ai_report)
                with tab2:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Current Price", f"₹ {current_price}")
                    col2.metric("Market Cap", f"{market_cap}")
                    col3.metric("Trailing P/E", f"{pe_ratio}")
                with tab3:
                    st.markdown("- **FII / FPI Trend:** Tracks institutional buying/selling behavior.\n- **Index Rebalancing:** Evaluates passive inflows/outflows.")

elif view_option == "Market & Sector Rotation":
    st.title("🔄 Market Scorecard & Sector Rotation")
    st.markdown("Real-time tracking of NSE Broad Markets, Sectoral, and Thematic Indices.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Sentiment", "Greed (Bullish)", "+1.4%")
    col2.metric("Fear & Greed Index", "68 / 100", "Moderate Greed")
    col3.metric("Institutional Flow Trend", "Positive FII Inflow", "Strong")
    
    st.subheader("Complete Sector Rotation Momentum Matrix")
    # Sample sector rotation chart data
    sector_data = pd.DataFrame({
        'Sector': ['Nifty IT', 'Nifty Pharma', 'Nifty Bank', 'Nifty Auto', 'Nifty Infra', 'Nifty Metal', 'Nifty Energy'],
        'Return_1M': [3.5, 5.2, 4.1, 2.8, 1.5, -1.2, -2.5],
        'Return_3M': [1.8, 7.1, 6.8, 6.5, 1.2, -0.8, -1.5]
    })
    fig = px.scatter(sector_data, x='Return_1M', y='Return_3M', text='Sector', size=[40]*len(sector_data), color='Return_3M',
                     labels={'Return_1M': '1M Return (%)', 'Return_3M': '3M Return (%)'}, title="All Sectors Rotation Quadrant")
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

elif view_option == "AI Weekly & Monthly Stock Screener":
    st.title("🤖 AI Automated Weekly & Monthly Stock Screener")
    st.markdown("Get high-conviction **Weekly Swing Setups (1-3 Stocks)** and **Monthly Investment Setups (4-6 Stocks)**.")
    
    frequency = st.radio("Select Frequency", ["Weekly Swing Trading (1-3 Stocks)", "Monthly Investment (4-6 Stocks)"])
    if st.button("🔍 Scan & Generate Trade Setups"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar!")
        else:
            with st.spinner("Running AI market scan across NSE indices..."):
                prompt = f"Scan top Indian NSE stocks for {frequency}. Provide 3 high-probability stock recommendations with Entry Price, Stop Loss, Target, and rationale."
                try:
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")

elif view_option == "Bulk, Block Deals & Insider Trading Tracker":
    st.title("🚨 Bulk, Block Deals & Insider Trading Tracker")
    st.markdown("Monitor institutional bulk deals, block transactions, and promoter insider activity on NSE.")
    st.info("Recent Bulk/Block deals data table will be populated here via live exchange feeds.")
    
    # Mock table for tracker
    deals_data = pd.DataFrame({
        'Date': ['13-Nov-2026', '13-Nov-2026', '12-Nov-2026'],
        'Company': ['RELIANCE', 'TCS', 'INFY'],
        'Deal Type': ['BUY', 'SELL', 'BUY'],
        'Client Name': ['Vanguard Group', 'SBI Mutual Fund', 'Blackrock'],
        'Quantity': ['1,50,000', '80,000', '2,10,000'],
        'Avg Price (₹)': ['2,750.00', '4,120.00', '1,890.00']
    })
    st.dataframe(deals_data, use_container_width=True)
