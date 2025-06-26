from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta

def run_trade_simulation(tickers, alpaca_key, alpaca_secret, paper=True):
    endpoint = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
    api = REST(alpaca_key, alpaca_secret, base_url=endpoint)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    results = []

    for ticker in tickers:
        try:
            bars = api.get_bars(ticker, "1D", start=yesterday.isoformat(), end=today.isoformat()).df
            if bars.empty or len(bars) < 2:
                continue

            y_close = bars.iloc[-2]['close']
            t_high = bars.iloc[-1]['high']
            t_low = bars.iloc[-1]['low']
            t_close = bars.iloc[-1]['close']

            entry_price = y_close
            tp_price = entry_price * 1.04
            sl_price = entry_price * 0.975

            if t_high >= tp_price:
                result = "TP Hit"
                pnl = entry_price * 0.04
            elif t_low <= sl_price:
                result = "SL Hit"
                pnl = entry_price * -0.025
            else:
                pnl = t_close - entry_price
                result = "Held to Close"

            results.append({
                "Ticker": ticker,
                "Entry": entry_price,
                "High": t_high,
                "Low": t_low,
                "Close": t_close,
                "Result": result,
                "PNL": round(pnl, 2)
            })

        except Exception as e:
            results.append({"Ticker": ticker, "Error": str(e)})

    return results
