from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

def load_ticker_data(ticker):
    # --- Alpaca Primary Attempt ---
    try:
        from alpaca_trade_api.rest import REST

        ALPACA_KEY = st.secrets["ALPACA_KEY"]
        ALPACA_SECRET = st.secrets["ALPACA_SECRET"]
        BASE_URL = "https://paper-api.alpaca.markets"

        api = REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

        end_date = datetime.today()
        start_date = end_date - timedelta(days=180)

        bars = api.get_bars(
            ticker,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        ).df

        if "symbol" in bars.columns:
            bars = bars[bars["symbol"] == ticker]

        if not bars.empty and len(bars) >= 60:
            df = bars[["close", "volume"]].rename(columns={"close": "Close", "volume": "Volume"})
            print(f"✅ {ticker} loaded from Alpaca: {len(df)} rows.")
            return df

        print(f"⚠️ {ticker} Alpaca data insufficient, falling back to yfinance...")

    except Exception as e:
        print(f"{ticker}: Alpaca load failed — {e}")

    # --- yfinance Fallback ---
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo", interval="1d", auto_adjust=True)

        if hist.empty or len(hist) < 60:
            print(f"❌ yfinance returned empty or too few rows for {ticker}")
            return None

        df = hist[["Close", "Volume"]].dropna()
        print(f"✅ {ticker} loaded from yfinance: {len(df)} rows.")
        return df

    except Exception as e:
        print(f"{ticker}: yfinance load failed — {e}")
        return None
