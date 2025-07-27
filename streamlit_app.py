import streamlit as st
import pandas as pd
from modules.data_loader import load_ticker_data
from modules.scoring import compute_scores
from modules.visuals import display_charts, display_divergence_info, plot_bollinger_overlay
from modules.filters import filter_dataframe
from modules.display import render_score_table, render_summary_box
from modules.upload import upload_watchlist
from modules.ai_commentary import (
    generate_ai_summary,
    generate_ai_option_recommendations,
    generate_strategy_confidence,
)
from modules.email_alerts import send_alert_email
from modules.company_overview import fetch_company_overview, generate_company_summary
from modules.crypto_overview import fetch_crypto_data, generate_crypto_summary
from modules.crypto_scoring import score_crypto

st.set_page_config(page_title="Modular Stock & Crypto Scanner", layout="wide")
st.title("📈 Modular Smart Stock & Crypto Scanner")

st.sidebar.header("⚙️ Scan Controls")
debug_mode = st.sidebar.checkbox("🛠 Debug Mode", value=False)
data_type = st.sidebar.radio("Select Data Type", ["Stocks", "Crypto"])
show_only_squeeze = st.sidebar.checkbox("📉 Only Show Squeeze Setups", value=False)

# RSI/Volume thresholds
if data_type == "Stocks":
    rsi_threshold = st.sidebar.slider("RSI Threshold (Short-Term)", 40, 70, 55)
    rsi_long_threshold = st.sidebar.slider("RSI Threshold (Long-Term)", 40, 70, 60)
    vol_multiplier = st.sidebar.slider("Volume Multiplier", 1.0, 3.0, 1.5)
    min_short_score = st.sidebar.slider("Min Short-Term Score", 0, 6, 3)
    min_long_score = st.sidebar.slider("Min Long-Term Score", 0, 3, 2)
else:
    rsi_threshold, rsi_long_threshold, vol_multiplier = 55, 60, 1.5
    min_short_score = st.sidebar.slider("Min Score (Crypto)", 0, 10, 5)
    min_long_score = 0

# Top 10 Movers Section
st.markdown("### 🔢 Top 10 Movers (Daily or Weekly Change)")
change_window = st.sidebar.radio("📈 % Change Window", ["1D", "7D"], index=0)
default_tickers = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "GOOGL", "META", "AMZN", "NFLX", "JPM"]

default_results = []
for ticker in default_tickers:
    df = load_ticker_data(ticker)
    if df is None or df.empty:
        continue
    df.attrs["ticker"] = ticker
    scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
    if not indicators:
        continue
    row = {"Ticker": ticker}
    row.update(indicators)
    default_results.append(row)

if default_results:
    top_df = pd.DataFrame(default_results)
    sort_key = "Daily % Change" if change_window == "1D" else "Weekly % Change"
    top_df = top_df.sort_values(by=sort_key, ascending=False).head(10)

    scroll_cols = st.columns(len(top_df))
    for i, row in top_df.iterrows():
        with scroll_cols[i]:
            price = row.get("Price ($)", 0)
            change = row.get(sort_key, 0)

            st.metric(
                label=f"**{row['Ticker']}**",
                value=f"${price:.2f}",
                delta=f"{change:+.2f}%",
            )

            if st.button(f"➕ Add {row['Ticker']}", key=f"add_{row['Ticker']}"):
                if "manual_watchlist" not in st.session_state:
                    st.session_state["manual_watchlist"] = []
                if row["Ticker"] not in st.session_state["manual_watchlist"]:
                    st.session_state["manual_watchlist"].append(row["Ticker"])

# Watchlist input
if data_type == "Crypto":
    tickers = st.multiselect("Search Cryptos", ["bitcoin", "ethereum", "solana", "dogecoin", "cardano"], default=["bitcoin"])
else:
    tickers = upload_watchlist()

# Scan logic
if tickers and st.button("🔍 Run Scan"):
    results = []
    crypto_data_map = {}

    with st.spinner("🔎 Scanning..."):
        for ticker in tickers:
            if data_type == "Stocks":
                df = load_ticker_data(ticker)
                if df is None or df.empty:
                    if debug_mode:
                        st.warning(f"{ticker} skipped: no data")
                    continue

                df.attrs["ticker"] = ticker
                scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
                if not scores:
                    continue

                if show_only_squeeze and not indicators.get("Bollinger Squeeze", False):
                    continue

                results.append({
                    "Ticker": ticker,
                    **scores,
                    **indicators,
                    "Divergence": "Yes" if indicators.get("Divergence", False) else "No",
                    "Bollinger Squeeze": "Yes" if indicators.get("Bollinger Squeeze", False) else "No"
                })
            else:
                coin_data = fetch_crypto_data(ticker)
                if not coin_data:
                    continue
                score, grade, breakdown = score_crypto(coin_data)
                rebound = breakdown.get("Rebound Potential", "0")
                rebound_value = float(rebound.split("%")[0]) if "%" in rebound else 0
                result = {
                    "Ticker": ticker,
                    "Short-Term Score": score,
                    "Long-Term Score": 0,
                    "Pattern": breakdown.get("Rebound Potential", "N/A"),
                    "Rebound %": rebound_value,
                    "Price ($)": coin_data.get("market_data", {}).get("current_price", {}).get("usd", 0),
                    "RSI": "N/A",
                    "MACD": "N/A",
                    "50-Day SMA": "N/A",
                    "100-Day SMA": "N/A",
                    "Current Volume": coin_data.get("market_data", {}).get("total_volume", {}).get("usd", 0),
                    "Avg Volume (20D)": "N/A"
                }
                results.append(result)
                crypto_data_map[ticker] = coin_data

    if results:
        df_all = pd.DataFrame(results)
        df_filtered = filter_dataframe(df_all, min_short_score, min_long_score)

        if not df_filtered.empty:
            render_summary_box(df_filtered)
            render_score_table(df_filtered)

            summary = generate_ai_summary(df_filtered, st.secrets["OPENAI_KEY"])
            st.info(summary)

            if data_type == "Stocks":
                st.success(generate_ai_option_recommendations(df_filtered, st.secrets["OPENAI_KEY"]))
                st.info(generate_strategy_confidence(df_filtered, st.secrets["OPENAI_KEY"]))

            st.markdown("### 📈 Charts and Indicators")
            for _, row in df_filtered.iterrows():
                ticker = row["Ticker"]
                df = load_ticker_data(ticker)
                scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
                divergence_found = indicators.get("Divergence", False)
                squeeze_flag = indicators.get("Bollinger Squeeze", False)
                display_divergence_info(scores, indicators, divergence_found)
                display_charts(ticker, df, divergence_found)
                if squeeze_flag:
                    plot_bollinger_overlay(ticker, df)

            if data_type == "Stocks":
                for ticker in df_filtered["Ticker"]:
                    with st.expander(f"Company overview: {ticker}"):
                        st.markdown(generate_company_summary(fetch_company_overview(ticker), st.secrets["OPENAI_KEY"]))
            else:
                for ticker in df_filtered["Ticker"]:
                    with st.expander(f"Crypto overview: {ticker}"):
                        st.markdown(generate_crypto_summary(crypto_data_map[ticker], st.secrets["OPENAI_KEY"]))

            if st.button("📤 Send Alert Email"):
                html_content = df_filtered.to_html(index=False)
                status = send_alert_email(st.secrets["SENDGRID_KEY"], st.secrets["EMAIL_TO"], "📈 Scan Results", html_content)
                st.success(f"Email sent! Status: {status}")
        else:
            st.warning("⚠️ No tickers met the scoring criteria.")
    else:
        st.warning("⚠️ No data returned from scan.")
