import numpy as np

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12).mean()
    exp2 = data['Close'].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd - signal

def compute_scores(df, rsi_thresh, rsi_long_thresh, vol_multiplier):
    price = df['Close'].iloc[-1]
    sma_50 = df['Close'].rolling(50).mean().iloc[-1]
    sma_100 = df['Close'].rolling(100).mean().iloc[-1]
    rsi = calculate_rsi(df).iloc[-1]
    macd_hist = calculate_macd(df).iloc[-1]
    vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]

    short_score = int(sum([
        price > sma_50,
        price > sma_100,
        macd_hist > 0,
        rsi < rsi_thresh,
        vol > vol_multiplier * avg_vol
    ]))

    long_score = int(sum([
        price > sma_100,
        macd_hist > 0,
        rsi < rsi_long_thresh
    ]))

    return (
        {
            "Short-Term Score": short_score,
            "Long-Term Score": long_score
        },
        {
            "Price ($)": round(float(price), 2),
            "50-Day SMA": round(float(sma_50), 2),
            "100-Day SMA": round(float(sma_100), 2),
            "MACD Histogram": round(float(macd_hist), 4),
            "RSI": round(float(rsi), 2),
            "Current Volume": int(vol),
            "Avg Volume (20D)": int(avg_vol)
        }
    )