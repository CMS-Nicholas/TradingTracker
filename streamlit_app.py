import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart Stock Scanner", layout="wide")

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

st.title("📈 Smart Stock Scanner (Cloud Version)")

ticker_input = st.text_area("Enter comma-separated tickers (e.g., AMD, AAPL, XOM):", "AMD, ARM, ADCT, LTRY, XOM, LMT, ZTEK, TPR")

if st.button("Run Scan"):
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    results = []

    with st.spinner("Scanning stocks..."):
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

                short_score = sum([
                    price > sma_50,
                    price > sma_100,
                    macd_hist > 0,
                    rsi < 55,
                    vol > 1.5 * avg_vol
                ])

                long_score = sum([
                    price > sma_100,
                    macd_hist > 0,
                    rsi < 60
                ])

                results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "50 SMA": round(sma_50, 2),
                    "100 SMA": round(sma_100, 2),
                    "MACD Hist": round(macd_hist, 4),
                    "RSI": round(rsi, 2),
                    "Curr Vol": int(vol),
                    "Avg Vol (20D)": int(avg_vol),
                    "Short Score": short_score,
                    "Long Score": long_score
                })
            except Exception as e:
                st.error(f"{ticker} failed: {e}")

    if results:
        df = pd.DataFrame(results)
        st.success("Scan Complete!")
        st.dataframe(df.sort_values("Short Score", ascending=False), use_container_width=True)
        st.download_button("📥 Download CSV", df.to_csv(index=False), "scanned_stocks.csv", "text/csv")
    else:
        st.warning("No valid tickers or no data found.")
