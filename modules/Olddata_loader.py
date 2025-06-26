import yfinance as yf
import pandas as pd

def load_ticker_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        if len(df) >= 100:
            df.dropna(inplace=True)
            return df
    except:
        return None
    return None