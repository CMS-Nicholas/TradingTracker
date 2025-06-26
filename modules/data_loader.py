import yfinance as yf
import pandas as pd

def load_ticker_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        if len(hist) < 60:
            return None

        hist = hist.dropna()

        # RSI calculation
        delta = hist['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        # MACD calculation
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = exp1 - exp2

        return hist
    except Exception as e:
        print(f"Failed to load data for {ticker}: {e}")
        return None
