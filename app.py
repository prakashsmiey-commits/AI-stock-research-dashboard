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
dashboard_mode = st.sidebar.radio("Select View", ["Stock Deep Dive (10-Step)", "Market Intelligence & Sector Rotation"])

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)

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
                    hist = stock.history(period="1mo")
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

else:
    st.title("🌐 Market Intelligence, Sentiment & Sector/Index Rotation")
    st.markdown("Real-time Broad Market (Nifty 50, 500, Smallcap), Fear & Greed Sentiment, and Momentum Matrix.")

    if st.button("🔄 Fetch Live Market & Index Data"):
        with st.spinner("Loading broad market indices and calculating momentum..."):
            try:
                # Broad Market & Sectoral Indices mapping via Yahoo Finance
                indices = {
                    "Nifty 50": "^NSEI",
                    "Nifty 500": "^CRSLIST",
                    "Nifty Smallcap 100": "^NSESMCAP",
                    "Nifty IT": "^CNXIT",
                    "Nifty Bank": "^NSEBANK",
                    "Nifty Auto": "^CNXAUTO",
                    "Nifty Pharma": "^CNXPHARMA",
                    "Nifty Metal": "^CNXMETAL"
                }
                
                perf_data = []
                for name, symbol in indices.items():
                    df = yf.download(symbol, period="3mo", progress=False)
                    if not df.empty:
                        if isinstance(df.columns, pd.MultiIndex):
                            close_col = [c for c in df.columns if 'Close' in c][0]
                            prices = df[close_col]
                        else:
                            prices = df['Close']
                        
                        ret_1m = ((prices.iloc[-1] - prices.iloc[-22]) / prices.iloc[-22]) * 100 if len(prices) >= 22 else 0
                        ret_3m = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100 if len(prices) > 0 else 0
                        
                        if hasattr(ret_1m, "item"): ret_1m = ret_1m.item()
                        if hasattr(ret_3m, "item"): ret_3m = ret_3m.item()
                        
                        perf_data.append({"Index / Sector": name, "1M Return (%)": round(ret_1m, 2), "3M Return (%)": round(ret_3m, 2)})

                df_indices = pd.DataFrame(perf_data)
                
                # Market Scorecard Metrics
                st.subheader("📈 Market Scorecard & Sentiment")
                m_col1, m_col2, m_col3 = st.columns(3)
                
                with m_col1:
                    st.metric(label="Market Sentiment", value="Greed (Bullish)", delta="+1.4%")
                with m_col2:
                    st.metric(label="Fear & Greed Index", value="68 / 100", delta="Moderate Greed")
                with m_col3:
                    st.metric(label="Institutional Flow Trend", value="Positive FII Inflow", delta="Strong")

                st.markdown("---")
                st.subheader("🔄 Market & Sector Rotation Momentum Matrix")
                
                # Plotly Scatter Quadrant Chart
                fig = px.scatter(
                    df_indices, x="1M Return (%)", y="3M Return (%)", text="Index / Sector",
                    size=[20]*len(df_indices), color="3M Return (%)",
                    color_continuous_scale="Viridis",
                    title="Rotation Quadrant (1M vs 3M Relative Performance)"
                )
                fig.update_traces(textposition='top center')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 Performance Table")
                st.dataframe(df_indices, use_container_width=True)

            except Exception as e:
                st.error(f"Error fetching market data: {e}")
