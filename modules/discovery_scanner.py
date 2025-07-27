from modules.data_loader import get_stock_data
from modules.scoring import compute_scores
import pandas as pd
import yfinance as yf
import pathlib
from modules.scoring import evaluate_perfect_setup

def get_tickers_by_price_range(min_price, max_price, limit=250):
    csv_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "constituents.csv"
    df = pd.read_csv(csv_path)
    tickers = df["Symbol"].dropna().unique().tolist()

    filtered = []
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty:
                continue
            last_price = data['Close'].iloc[-1]
            if min_price <= last_price <= max_price:
                filtered.append(ticker)
            if len(filtered) >= limit:
                break
        except Exception:
            continue
    return filtered

def run_discovery(min_price, max_price, batch_size=10):
    candidates = get_tickers_by_price_range(min_price, max_price)
    scored = []

    for ticker in candidates:
        df = get_stock_data(ticker)
        if df is None or df.empty:
            continue

        df.attrs["ticker"] = ticker
        scores, indicators = compute_scores(df, 55, 60, 1.5)
        if not scores:
            continue

        combined = {
            **scores,
            **indicators,
            "price": indicators.get("Price ($)", None),
        }

        checklist = evaluate_perfect_setup(indicators, scores)
        combined["Perfect Setup Score"] = checklist.pop("Perfect Setup Score")
        combined["Setup Checklist"] = checklist
        scored.append((ticker, combined))

    scored.sort(key=lambda x: x[1].get("Short-Term Score", 0), reverse=True)
    return scored[:batch_size]
