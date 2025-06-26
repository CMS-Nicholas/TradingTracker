import pandas as pd
import numpy as np

def compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier):
    df = df.copy()

    print("⏳ [compute_scores] Start scoring...")
    print(f"📊 Input rows: {len(df)} | Columns: {list(df.columns)}")

    # 🚨 Early exit if data is insufficient
    if len(df) < 60 or "Close" not in df.columns or "Volume" not in df.columns:
        print("❌ Not enough data or missing Close/Volume columns")
        return {}, {}

    try:
        # RSI
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2

        # Key metrics
        close = float(df['Close'].iloc[-1])
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        sma_100 = df['Close'].rolling(window=100).mean().iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]

        print(f"🔍 close={close:.2f}, sma_50={sma_50:.2f}, sma_100={sma_100:.2f}, rsi={rsi:.2f}, macd={macd:.4f}")

    except Exception as e:
        print(f"❌ Error computing indicators: {e}")
        return {}, {}

    # Scores
    short_score = sum([
        close > sma_50,
        close > sma_100,
        macd > 0,
        rsi < rsi_threshold,
        volume > vol_multiplier * avg_volume
    ])
    long_score = sum([
        close > sma_100,
        macd > 0,
        rsi < rsi_long_threshold
    ])

    # Rebound calc
    try:
        low_7d = df['Close'].tail(7).min()
        low_30d = df['Close'].tail(30).min()
        rebound_7d = (close - low_7d) / low_7d * 100 if low_7d else 0
        rebound_30d = (close - low_30d) / low_30d * 100 if low_30d else 0
        avg_rebound = (rebound_7d + rebound_30d) / 2
    except Exception as e:
        print(f"⚠️ Rebound calc failed: {e}")
        avg_rebound = 0

    # Pattern logic
    if avg_rebound > 20:
        pattern_tag = "🚀 Breakout Potential"
    elif avg_rebound > 10:
        pattern_tag = "📈 Strong Reversal"
    elif avg_rebound > 5:
        pattern_tag = "🌀 Mild Recovery"
    else:
        pattern_tag = "⚖️ Consolidating"

    scores = {
        "Short-Term Score": float(short_score),
        "Long-Term Score": float(long_score),
        "Pattern": pattern_tag,
        "Rebound %": round(avg_rebound, 2)
    }

    indicators = {
        "Price ($)": round(close, 2),
        "50-Day SMA": round(sma_50, 2),
        "100-Day SMA": round(sma_100, 2),
        "RSI": round(rsi, 2),
        "MACD": round(macd, 4),
        "Current Volume": int(volume),
        "Avg Volume (20D)": int(avg_volume) if not pd.isna(avg_volume) else 0
    }

    print(f"✅ Scoring complete. ST={short_score}, LT={long_score}, Pattern={pattern_tag}")
    return scores, indicators
