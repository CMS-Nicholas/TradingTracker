from modules.data_loader import load_ticker_data


df = load_ticker_data("AAPL")
print(df.head())