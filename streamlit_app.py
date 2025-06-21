import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart Stock Scanner", layout="wide")

# ========= FUNCTIONS ============

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd - signal

# ========= PAGE HEADER ============

st.title("📈 Smart Stock Scanner (Cloud Version)")
st.markdown("Use the panel below to input tickers and scan for short- and long-term opportunities.")

with st.expander("ℹ️ **How scoring works**"):
    st.markdown("""
    **Short-Term Score (Max 5)**:
    - Price above 50-day SMA ✅
    - Price above 100-day SMA ✅
    - MACD Histogram positive ✅
    - RSI under 55 ✅
    - Volume > 1.5× average ✅

    **Long-Term Score (Max 3)**:
    - Price above 100-day SMA ✅
    - MACD Histogram positive ✅
    - RSI under 60 ✅
    """)

# ========= USER INPUT ============

ticker_input = st.text_area("Enter comma-separated tickers (e.g., AMD, AAPL, XOM):", 
                            "AMD, ARM, ADCT, LTRY, XOM, LMT, ZTEK, TPR")

if st.button("Run Scan"):
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    results = []

    with st.spinner("🔎 Scanning stocks..."):
        for ticker in tickers:
            try:
                hist = yf.download(ticker, period="6mo", progress=False)
                if len(hist) < 100:
                    continue

                sma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma_100 = hist['Close'].rolling(100).mean().iloc[-1]
                price = hist['Close'].iloc[-1]
                rsi = calculate_rsi(hist).iloc[-1]
                macd_hist = calculate_macd(hist).iloc[-1]
                vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].rolling(20).mean().iloc[-1]

                short_score = int(sum([
                    price > sma_50,
                    price > sma_100,
                    macd_hist > 0,
                    rsi < 55,
                    vol > 1.5 * avg_vol
                ]))

                long_score = int(sum([
                    price > sma_100,
                    macd_hist > 0,
                    rsi < 60
                ]))

                results.append({
                    "Ticker": ticker,
                    "Price ($)": round(float(price), 2),
                    "50-Day SMA": round(float(sma_50), 2),
                    "100-Day SMA": round(float(sma_100), 2),
                    "MACD Histogram": round(float(macd_hist), 4),
                    "RSI": round(float(rsi), 2),
                    "Current Volume": f"{int(vol):,}",
                    "Avg Volume (20D)": f"{int(avg_vol):,}",
                    "Short-Term Score": short_score,
                    "Long-Term Score": long_score
                })

            except Exception as e:
                st.error(f"{ticker} failed: {e}")

    # ========= DISPLAY OUTPUT ============
    if results:
        df = pd.DataFrame(results)
        st.success("✅ Scan Complete!")

        # Clean and safely sort
        if "Short-Term Score" in df.columns:
            try:
                df["Short-Term Score"] = pd.to_numeric(df["Short-Term Score"], errors="coerce")
                df_sorted = df.sort_values("Short-Term Score", ascending=False)
            except Exception as e:
                st.warning(f"⚠️ Could not sort by Short-Term Score: {e}")
                df_sorted = df
        else:
            df_sorted = df

        st.dataframe(df_sorted, use_container_width=True)

        st.download_button("📥 Download CSV", df_sorted.to_csv(index=False), 
                           "scanned_stocks.csv", "text/csv")
    else:
        st.warning("⚠️ No valid data found. Try different tickers.")