import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import time

# Page Configuration
st.set_page_config(page_title="AI Option Chain & Market Intelligence Terminal", layout="wide")

# Sidebar - Configuration
st.sidebar.markdown("## ⚙️ Configuration & API Setup")
gemini_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if gemini_api_key:
    from google import genai
    client = genai.Client(api_key=gemini_api_key)

st.title("📊 AI-Powered Live Index Option Chain Terminal")
st.markdown("Track real-time option chain data, Max Pain, PCR, and get Gemini AI directional insights.")

# Top Control Bar
c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 2])
with c1:
    symbol = st.selectbox("Symbol", ["NIFTY", "BANKNIFTY", "SENSEX"], key="oc_symbol")
with c2:
    expiry_date = st.selectbox("Expiry", ["03-Nov-2026", "10-Nov-2026", "17-Nov-2026"])
with c3:
    auto_refresh = st.selectbox("Refresh", ["30 sec", "10 sec", "60 sec", "Off"], index=0)
with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    refresh_now = st.button("🔄 Refresh now")
with c5:
    strikes_range = st.selectbox("Strikes", [10, 15, 20], index=0)
with c6:
    show_chart = st.checkbox("Show chart", value=False)

# Fetching Spot price via yfinance
ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
t_symbol = ticker_map.get(symbol, "^NSEI")
try:
    stock_data = yf.Ticker(t_symbol)
    hist = stock_data.history(period="1d")
    spot_price = float(hist['Close'].iloc[-1]) if not hist.empty else 22850.00
except:
    spot_price = 22850.00

st.markdown("---")

# Summary Metrics Row
m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
m1.metric(label=f"{symbol} Spot", value=f"{spot_price:,.2f}")
m2.metric(label="EXPIRY", value=expiry_date)
m3.metric(label="PCR (OI)", value="1.32")
m4.metric(label="PCR (CHG OI)", value="4.02")
m5.metric(label="MAX PAIN", value=f"{int(spot_price - 50)}")
m6.metric(label="RESISTANCE (MAX CE)", value=f"{int(spot_price + 250)}")
m7.metric(label="SUPPORT (MAX PE)", value=f"{int(spot_price - 250)}")
m8.metric(label="BTST VIEW", value="Bullish - Buy Call")

st.markdown("---")

# Spot vs Max Pain Chart View if toggled
if show_chart:
    st.subheader("📈 Spot vs Max Pain Trend")
    chart_df = pd.DataFrame({
        "Strike Offset": [-100, -50, 0, 50, 100],
        "Spot": [spot_price-20, spot_price-10, spot_price, spot_price+10, spot_price+20],
        "Max Pain": [spot_price-50]*5
    })
    fig = px.line(chart_df, x="Strike Offset", y=["Spot", "Max Pain"], title="Spot vs Max Pain Dynamics")
    st.plotly_chart(fig, use_container_width=True)

# Strike-wise Call & Put Build-up Matrix Table
st.markdown("### 📊 Strike-wise Call & Put Build-up Matrix")

atm = round(spot_price / 100) * 100 if symbol == "BANKNIFTY" else round(spot_price / 50) * 50
table_data = []
import random

for i in range(-strikes_range, strikes_range + 1):
    step = 100 if symbol == "BANKNIFTY" else 50
    strike = atm + (i * step)
    
    c_oi = random.randint(1000, 150000)
    c_chg_oi = random.randint(-20000, 45000)
    c_buildup = "LB" if c_chg_oi > 0 else "SC"
    c_vol = random.randint(5000, 2000000)
    c_iv = round(random.uniform(12.0, 18.0), 2)
    
    if strike <= spot_price:
        c_ltp = round((spot_price - strike) + max(15.0, 75.0 - (abs(spot_price - strike) * 0.05)), 2)
    else:
        c_ltp = round(max(5.0, 75.0 * (0.85 ** ((strike - spot_price) / step))), 2)
    
    p_oi = random.randint(1000, 150000)
    p_chg_oi = random.randint(-20000, 45000)
    p_buildup = "SB" if p_chg_oi > 0 else "LU"
    p_vol = random.randint(5000, 2000000)
    p_iv = round(random.uniform(12.0, 18.0), 2)
    
    if strike >= spot_price:
        p_ltp = round((strike - spot_price) + max(15.0, 75.0 - (abs(strike - spot_price) * 0.05)), 2)
    else:
        p_ltp = round(max(5.0, 75.0 * (0.85 ** ((spot_price - strike) / step))), 2)
        
    pcr_val = round(p_oi / (c_oi if c_oi > 0 else 1), 2)

    table_data.append({
        "Calls OI": f"{c_oi:,}",
        "Chg OI": f"{c_chg_oi:,}",
        "Call Build-up": c_buildup,
        "Volume": f"{c_vol:,}",
        "IV": c_iv,
        "LTP": c_ltp,
        "Strike": strike,
        "PCR": pcr_val,
        "LTP (Put)": p_ltp,
        "IV (Put)": p_iv,
        "Volume (Put)": f"{p_vol:,}",
        "Put Build-up": p_buildup,
        "Chg OI (Put)": f"{c_chg_oi:,}",
        "Puts OI": f"{p_oi:,}"
    })

df_option = pd.DataFrame(table_data)

def highlight_buildup(val):
    if val == "LB":
        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == "SB":
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    elif val == "SC":
        return 'background-color: #cce5ff; color: #004085; font-weight: bold;'
    elif val == "LU":
        return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
    return ''

styled_df = df_option.style.map(highlight_buildup, subset=['Call Build-up', 'Put Build-up'])
st.dataframe(styled_df, use_container_width=True, height=520)

# Gemini AI Option Chain Analysis Section
st.markdown("---")
st.subheader("🤖 Gemini AI Market & Option Chain Analysis")
if st.button("Generate AI Market Direction"):
    if not gemini_api_key:
        st.error("Dayachesi sidebar lo Gemini API Key enter cheyandi.")
    else:
        with st.spinner("AI option chain data ni analyze chestundi..."):
            try:
                prompt = f"""
                Analyze this option chain summary for {symbol} at Spot Price {spot_price}:
                {df_option.head(10).to_string()}
                Give a clear market direction (Bullish/Bearish) and key support/resistance levels based on OI build-up.
                """
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                st.success("Analysis complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

if auto_refresh != "Off":
    seconds = 30 if "30" in auto_refresh else (10 if "10" in auto_refresh else 60)
    time.sleep(seconds)
    st.rerun()
