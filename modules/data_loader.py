import yfinance as yf
import pandas as pd

def load_ticker_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        if df.empty or len(df) < 60:
            print(f"❌ {ticker} returned too little data.")
            return None

        df = df[["Close", "Volume"]].dropna()
        df = df.rename(columns=str.title)
        print(f"✅ {ticker} returned {len(df)} rows from yfinance.")
        return df
    except Exception as e:
        print(f"{ticker}: ❌ yfinance error – {e}")
        return None
