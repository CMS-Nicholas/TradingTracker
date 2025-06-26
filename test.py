import yfinance as yf

ticker = yf.Ticker("AAPL")
df = ticker.history(period="6mo", interval="1d", auto_adjust=True)

print("Rows:", len(df))
print(df.tail())