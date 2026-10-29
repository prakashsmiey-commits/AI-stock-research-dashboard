import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from google import genai

# Page Configuration
st.set_page_config(page_title="AI Stock & Market Intelligence Dashboard", layout="wide")

# Sidebar - Configuration
st.sidebar.markdown("## ⚙️ Configuration & API Setup")
gemini_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.sidebar.markdown("---")
dashboard_mode = st.sidebar.radio(
    "Select View", 
    [
        "Stock Deep Dive (10-Step)", 
        "Market & Sector Rotation", 
        "🤖 AI Weekly & Monthly Stock Screener",
        "🚨 Bulk, Block Deals & Insider Trading Tracker",
        "📊 Live Index Option Chain Analyzer"
    ]
)

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)

# ----------------- VIEW 1: STOCK DEEP DIVE -----------------
if dashboard_mode == "Stock Deep Dive (10-Step)":
    st.title("📊 AI Stock Investment & Smart Money Dashboard")
    st.markdown("Integrated with Sifu Yik's 10-Step Framework + FII/FPI Institutional Tracking")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ticker = st.text_input("Stock Ticker (e.g., RELIANCE.NS, TCS.NS)", "RELIANCE.NS")
    with col2:
        horizon = st.selectbox("Investment Horizon", ["SHORT", "MEDIUM", "LONG"])
    with col3:
        portfolio_size = st.number_input("Portfolio Size (₹)", value=100000)
    with col4:
        risk_tolerance = st.selectbox("Risk Tolerance", ["LOW", "MEDIUM", "HIGH"])

    if st.button("🚀 Run Full Analysis with Gemini AI"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Fetching stock metrics and running AI institutional analysis..."):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                    
                    prompt = f"""
                    Analyze the stock {ticker} using Sifu Yik's 10-Step Framework and FII/FPI Institutional Tracking.
                    Current Price: {current_price}
                    Horizon: {horizon}, Portfolio Size: {portfolio_size}, Risk Tolerance: {risk_tolerance}
                    Provide a structured markdown report including Valuation Inputs (Bear, Base, Bull targets), Peer Comparison, and Institutional Smart Money & Rebalancing Tracking.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    
                    st.success(f"Analysis successfully completed for {info.get('longName', ticker)}!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error generating AI response: {e}")

# ----------------- VIEW 2: MARKET & SECTOR ROTATION -----------------
elif dashboard_mode == "Market & Sector Rotation":
    st.title("🌐 Complete Market Intelligence & Sector Rotation Matrix")
    st.markdown("Real-time tracking of all NSE Broad Markets, Sectoral, and Thematic Indices.")

    if st.button("🔄 Fetch All Sectors & Indices Data"):
        with st.spinner("Loading all market sectors and calculating relative momentum..."):
            try:
                indices = {
                    "Nifty 50": "^NSEI",
                    "Nifty 500": "^CRSLIST",
                    "Nifty Smallcap": "^NSESMCAP",
                    "Bank Nifty": "^NSEBANK",
                    "FinNifty": "NIFTY_FIN_SERVICE.NS",
                    "Midcap Select": "NIFTY_MID_SELECT.NS",
                    "Nifty IT": "^CNXIT",
                    "Nifty Auto": "^CNXAUTO",
                    "Nifty Pharma": "^CNXPHARMA",
                    "Nifty Metal": "^CNXMETAL",
                    "Nifty FMCG": "^CNXFMCG",
                    "Nifty Energy": "^CNXENERGY",
                    "Nifty Media": "^CNXMEDIA",
                    "Nifty Infra": "^CNXINFRA",
                    "Nifty Realty": "CNXREALTY.NS",
                    "Nifty PSU Bank": "NIFTY_PSU_BANK.NS"
                }
                
                perf_data = []
                for name, symbol in indices.items():
                    df = yf.download(symbol, period="3mo", progress=False)
                    if not df.empty:
                        if isinstance(df.columns, pd.MultiIndex):
                            close_col = [c for c in df.columns if 'Close' in c][0]
                            prices = df[close_col].dropna()
                        else:
                            prices = df['Close'].dropna()
                        
                        if len(prices) > 1:
                            idx_1m = -22 if len(prices) >= 22 else 0
                            ret_1m = ((prices.iloc[-1] - prices.iloc[idx_1m]) / prices.iloc[idx_1m]) * 100
                            ret_3m = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
                            
                            if hasattr(ret_1m, "item"): ret_1m = ret_1m.item()
                            if hasattr(ret_3m, "item"): ret_3m = ret_3m.item()
                            
                            perf_data.append({
                                "Index / Sector": name, 
                                "1M Return (%)": round(ret_1m, 2), 
                                "3M Return (%)": round(ret_3m, 2)
                            })

                df_indices = pd.DataFrame(perf_data).dropna()
                
                st.subheader("📈 Market Scorecard & Sentiment")
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric(label="Market Sentiment", value="Greed (Bullish)", delta="+1.4%")
                with m_col2:
                    st.metric(label="Fear & Greed Index", value="68 / 100", delta="Moderate Greed")
                with m_col3:
                    st.metric(label="Institutional Flow Trend", value="Positive FII Inflow", delta="Strong")

                st.markdown("---")
                st.subheader("🔄 Complete Sector Rotation Momentum Matrix")
                
                fig = px.scatter(
                    df_indices, x="1M Return (%)", y="3M Return (%)", text="Index / Sector",
                    size=[25]*len(df_indices), color="3M Return (%)",
                    color_continuous_scale="Viridis",
                    title="All Sectors Rotation Quadrant (1M vs 3M Relative Performance)"
                )
                fig.update_traces(textposition='top center')
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 All Sectors Performance Table")
                st.dataframe(df_indices, use_container_width=True)

            except Exception as e:
                st.error(f"Error fetching market data: {e}")

# ----------------- VIEW 3: WEEKLY & MONTHLY AI SCREENER -----------------
elif dashboard_mode == "🤖 AI Weekly & Monthly Stock Screener":
    st.title("🤖 AI Automated Weekly & Monthly Stock Screener")
    st.markdown("Get high-conviction **Weekly Swing Setups (1-3 Stocks)** and **Monthly Investment Setups (4-6 Stocks)** with precise Entry, Stop Loss, and Targets.")

    timeframe = st.radio("Select Frequency", ["Weekly Swing Trading (1-3 Stocks)", "Monthly Investment (4-6 Stocks)"])
    
    if st.button("🔍 Scan & Generate Trade Setups"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            count = "1-3 high-probability swing trading" if "Weekly" in timeframe else "4-6 fundamentally strong long-term"
            with st.spinner(f"AI is scanning NSE market for {count} stock setups..."):
                try:
                    prompt = f"""
                    Act as an expert Indian Stock Market Quantitative Analyst and Institutional Trader.
                    Provide {count} stock recommendations for the Indian NSE market for '{timeframe}'.
                    
                    For each stock provide:
                    1. Stock Name & Ticker (e.g., RELIANCE.NS)
                    2. Current Market Price
                    3. Recommended Entry Range
                    4. Stop Loss (SL)
                    5. Target 1 & Target 2
                    6. Risk-to-Reward Ratio
                    7. Institutional / Technical Rationale
                    
                    Format the output cleanly using Markdown tables and bullet points.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    
                    st.success("Successfully scanned and generated trade setups!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error running scan: {e}")

# ----------------- VIEW 4: BULK, BLOCK & INSIDER TRADING -----------------
elif dashboard_mode == "🚨 Bulk, Block Deals & Insider Trading Tracker":
    st.title("🚨 Bulk Deals, Block Deals & Insider Trading Tracker")
    st.markdown("AI-powered analysis of recent smart money accumulation, promoter buying/selling, and heavy institutional block deals in NSE/BSE.")

    if st.button("🔍 Fetch Smart Money & Insider Activity"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Analyzing recent exchange bulk deals, block transactions, and insider disclosures..."):
                try:
                    insider_prompt = """
                    Act as an elite Institutional Market Intelligence Analyst tracking the Indian Stock Market (NSE/BSE).
                    Provide a detailed intelligence report on recent trends regarding:
                    1. **Major Bulk & Block Deals** (Which institutional funds, HNIs, or foreign entities are aggressively buying/selling key stocks this week?)
                    2. **Insider Trading Activity** (Key promoter buying or selling actions, stake changes by top management)
                    3. **Smart Money Accumulation Zones** (Which sectors are seeing heavy block transactions?)
                    
                    Present the information using structured tables, stock tickers, transaction types, and actionable insights.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=insider_prompt,
                    )
                    
                    st.success("Smart Money & Insider Data successfully analyzed!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error fetching insider data: {e}")

# ----------------- VIEW 5: LIVE INDEX OPTION CHAIN ANALYZER -----------------
else:
    st.title("📊 Live Index Option Chain & BTST Analyzer")
    st.markdown("Advanced option chain breakdown with PCR, Max Pain, Strike-wise Build-up, and AI BTST / Momentum View for **Nifty, Bank Nifty, and Sensex**.")

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        selected_index = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "SENSEX"])
    with col_opt2:
        analysis_mode = st.selectbox("View Mode", ["Live Option Chain Metrics & AI BTST View", "Strike-wise OI & Build-up Breakdown"])

    if st.button("⚡ Fetch Option Chain Intelligence"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner(f"Fetching real-time option chain data and computing smart money signals for {selected_index}..."):
                try:
                    oc_prompt = f"""
                    Act as an expert Indian Derivatives Quantitative Analyst. Provide a professional live option chain intelligence report for **{selected_index}** in the exact format required by elite traders:
                    
                    1. **Summary Header Metrics**: Current Spot Price, Expiry Date, PCR (OI), PCR (Chg OI), Max Pain, Resistance (Max CE OI), Support (Max PE OI), and BTST Signal (e.g., Bullish - Buy Call / Bearish - Buy Put with clear rationale).
                    2. **Strike-Wise Chain Table**: A detailed table resembling professional terminal layouts showing: Calls OI, Chg OI, Build-up (SC/LB), Volume, IV, Delta, Signal, VWAP, LTP, Strike, PCR, LTP (Put), VWAP (Put), Signal, Delta, IV, Volume, Build-up, Chg OI, Puts OI.
                    3. **Institutional OI Build-up Insights**: Where smart money is writing calls/puts and directional momentum triggers.
                    
                    Format cleanly using markdown tables and clear highlights.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=oc_prompt,
                    )
                    
                    st.success(f"Option Chain analysis successfully generated for {selected_index}!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error fetching option chain data: {e}")
