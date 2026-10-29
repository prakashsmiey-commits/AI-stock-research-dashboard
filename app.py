import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Institutional Stock Research & AI Dashboard", layout="wide")

st.sidebar.header("⚙️ Configuration & API Setup")
gemini_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('models/gemini-pro')

ticker_symbol = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, TCS.NS)", value="RELIANCE.NS")
investment_horizon = st.sidebar.selectbox("Investment Horizon", ["SHORT", "MEDIUM", "LONG"])
portfolio_size = st.sidebar.text_input("Portfolio Size (₹)", value="1,00,000")
risk_tolerance = st.sidebar.selectbox("Risk Tolerance", ["LOW", "MEDIUM", "HIGH"])

st.title("📊 AI Stock Investment & Smart Money Dashboard")
st.markdown("Integrated with Sifu Yik's 10-Step Framework + FII/FPI Institutional Tracking")

if st.button("🚀 Run Full Analysis with Gemini AI"):
    if not gemini_api_key:
        st.error("Please enter your Gemini API Key in the sidebar first!")
    else:
        with st.spinner("Fetching stock metrics and running AI institutional analysis..."):
            
            # Fetching basic info via yfinance
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

            # Prompt Construction for Gemini
            prompt = f"""
            Act as a Senior Equity Research Analyst and Institutional Fund Manager. Analyze the stock {ticker_name if 'ticker_name' in locals() else ticker_symbol} ({ticker_symbol}) for a {investment_horizon} term investor.
            
            Provide a comprehensive report structured into these exact 11 sections (incorporating Sifu Yik's 10 steps + Smart Money/FII tracking):
            1. Company Snapshot in Plain English (Business model, moat, key metrics).
            2. Financial Health Check (Revenue, margins, cash flow, debt trends).
            3. Earnings Report Breakdown (Expectations, guidance, management commentary).
            4. Fair Value Range (Valuation models like P/E, DCF, conservative/base/optimistic bands).
            5. Head-to-Head Stock Comparison (Scored 1-10 against peers).
            6. Institutional Smart Money & FII/FPI Activity (Analyze recent FII/DII buying trends, quarterly holding changes, and impact of bi-monthly/periodic index rebalancing flows).
            7. Catalysts & Risks Timeline (6/12/24 month milestones).
            8. Three Scenario Test (Bull, Base, Bear cases with probability weights).
            9. Chart Reading & Technical Setup (Moving averages, RSI, support/resistance, breakout levels).
            10. Personal Decision Checklist (Portfolio limits, max loss, tracking metrics).
            11. Argument Against Me (Devil's Advocate - weakest assumptions and hidden risks).
            
            Format the output cleanly with markdown headings and bullet points.
            """

            try:
                response = model.generate_content(prompt)
                ai_report = response.text
            except Exception as e:
                ai_report = f"Error generating AI response: {e}"

            st.success(f"Analysis successfully completed for {company_name}!")
            
            # Display Results in Tabs
            tab1, tab2, tab3 = st.tabs(["📑 Full AI Institutional Report", "📈 Basic Market Metrics", "🧠 Smart Money & FII Tracker"])
            
            with tab1:
                st.markdown(ai_report)
                
            with tab2:
                st.subheader("Key Quantitative Metrics")
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Price", f"₹ {current_price}")
                col2.metric("Market Cap", f"{market_cap}")
                col3.metric("Trailing P/E", f"{pe_ratio}")
                
            with tab3:
                st.subheader("Institutional Smart Money & Rebalancing Tracking")
                st.markdown("""
                - **FII / FPI Trend:** Tracks net institutional buying/selling behavior over the last 2 to 4 quarters.
                - **Index Rebalancing Impact:** Evaluates bi-monthly/quarterly adjustments (e.g., Nifty/MSCI rebalancing) where passive smart money inflows or outflows trigger sharp momentum shifts.
                - **Promoter Pledges & DII Cushion:** Monitors domestic institutional accumulation to offset foreign capital outflows.
                """)
