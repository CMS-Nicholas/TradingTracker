import pandas as pd
import numpy as np
from modules.valuation import get_and_score_valuation, get_valuation_metrics
from modules.valuation import compute_valuation_score
from modules.indicators import detect_hidden_bullish_divergence

def compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier):
    df = df.copy()

    print("\u23f3 [compute_scores] Start scoring...")
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

    # Hidden Bullish Divergence Detection
    try:
        if detect_hidden_bullish_divergence(df):
            short_score += 1
            print("✨ Hidden Bullish Divergence detected – Short-Term Score +1")
            pattern_tag += " + Divergence"
    except Exception as e:
        print(f"⚠️ Divergence detection failed: {e}")

    # % Change calculations
    try:
        change_1d = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
        change_7d = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100
    except:
        change_1d = change_7d = 0

    # Valuation Score
    try:
        ticker = df.attrs.get("ticker", "")
        print(f"📌 Valuation ticker passed to scoring: {ticker}")
        valuation_metrics = get_valuation_metrics(ticker)
        valuation_score = compute_valuation_score(valuation_metrics)
        target_price = valuation_metrics.get("target_price") if valuation_metrics else None
    except Exception as e:
        print(f"⚠️ Valuation data error: {e}")
        valuation_score = 0
        target_price = None

    scores = {
        "Short-Term Score": float(short_score),
        "Long-Term Score": float(long_score),
        "Pattern": pattern_tag,
        "Rebound %": round(avg_rebound, 2),
        "Valuation Score": valuation_score
    }

    indicators = {
        "Price ($)": round(close, 2),
        "50-Day SMA": round(sma_50, 2),
        "100-Day SMA": round(sma_100, 2),
        "RSI": round(rsi, 2),
        "MACD": round(macd, 4),
        "Current Volume": int(volume),
        "Avg Volume (20D)": int(avg_volume) if not pd.isna(avg_volume) else 0,
        "Daily % Change": round(change_1d, 2),
        "Weekly % Change": round(change_7d, 2),
        "Target Price ($)": round(target_price, 2) if target_price else None
    }

    entry_flag = (
        50 <= rsi <= 65 and
        macd > 0 and
        close > sma_50 and
        short_score >= 3 and
        long_score >= 2 and
        volume >= avg_volume
    )

    # Suggested Exit Flag (for simulation prediction, not historical real sell point)
    if avg_rebound >= 3.5:
        exit_zone = "📈 Take Profit"
    elif avg_rebound <= -2.5:
        exit_zone = "⚠️ Stop Loss"
    else:
        exit_zone = "⏳ Hold"

    indicators["Suggested Entry"] = "✅" if entry_flag else ""
    indicators["Exit Zone"] = exit_zone

    print(f"✅ Scoring complete. ST={short_score}, LT={long_score}, Pattern={pattern_tag}")
    return scores, indicators

def evaluate_perfect_setup(indicators, scores):
    checklist = {}

    checklist["Pullback/Base Breakout"] = "✅" if "Breakout" in scores.get("Pattern", "") or "Reversal" in scores.get("Pattern", "") else "❌"
    checklist["RSI 50–65"] = "✅" if 50 <= indicators.get("RSI", 0) <= 65 else "❌"
    checklist["MACD Bullish"] = "✅" if indicators.get("MACD", 0) > 0 else "❌"
    checklist["Above 20D SMA"] = "✅" if indicators.get("Price ($)", 0) > indicators.get("50-Day SMA", 0) else "❌"
    checklist["Above 50D SMA"] = "✅" if indicators.get("Price ($)", 0) > indicators.get("100-Day SMA", 0) else "❌"
    checklist["Price < $100"] = "✅" if indicators.get("Price ($)", 0) < 100 else "❌"
    checklist["No Earnings Next Week"] = "⚠️"  # Optional, if you want to integrate earnings API
    checklist["Not Overextended"] = "✅" if scores.get("Rebound %", 0) < 30 else "❌"
    checklist["Reasonable Options"] = "⚠️"  # Optional: only if you add options API
    checklist["Tight Strike Increments"] = "⚠️"

    score = list(checklist.values()).count("✅")
    checklist["Perfect Setup Score"] = f"{score}/10"
    return checklist