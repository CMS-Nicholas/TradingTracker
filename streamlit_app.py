import streamlit as st
import pandas as pd
from modules.data_loader import load_ticker_data
from modules.scoring import compute_scores
from modules.visuals import display_charts
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
from modules.crypto_scoring import score_crypto  # ✅ Confirmed



st.set_page_config(page_title="📈 Modular Stock & Crypto Scanner", layout="wide")
st.title("📈 Modular Smart Stock & Crypto Scanner")
st.markdown("### 🧭 Top 10 Movers (Daily or Weekly Change)")

change_window = st.sidebar.radio("📈 % Change Window", ["1D", "7D"], index=0)
default_tickers = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "GOOGL", "META", "AMZN", "NFLX", "JPM"]

default_results = []
for ticker in default_tickers:
    df = load_ticker_data(ticker)
    if df is None or df.empty:
        continue
        df.attrs["ticker"] = ticker  # ✅ Ensure ticker is passed into scoring
    scores, indicators = compute_scores(df, 55, 60, 1.5)
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

# 🔐 Load Secrets
sendgrid_key = st.secrets["SENDGRID_KEY"]
openai_key = st.secrets["OPENAI_KEY"]
email_to = st.secrets["EMAIL_TO"]

# ⚙️ Sidebar Controls
st.sidebar.header("⚙️ Scan Controls")
debug_mode = st.sidebar.checkbox("🛠 Debug Mode", value=False)
data_type = st.sidebar.radio("Select Data Type", ["Stocks", "Crypto"])


if data_type == "Stocks":
    rsi_threshold = st.sidebar.slider("RSI Threshold (Short-Term)", 40, 70, 55)
    rsi_long_threshold = st.sidebar.slider("RSI Threshold (Long-Term)", 40, 70, 60)
    vol_multiplier = st.sidebar.slider("Volume Multiplier", 1.0, 3.0, 1.5)
    min_short_score = st.sidebar.slider("Min Short-Term Score", 0, 5, 3)
    min_long_score = st.sidebar.slider("Min Long-Term Score", 0, 3, 2)
else:
    min_short_score = st.sidebar.slider("Min Score (Crypto)", 0, 10, 5)
    min_long_score = 0
    rsi_threshold = 55
    rsi_long_threshold = 60
    vol_multiplier = 1.5

# Ticker Input
if data_type == "Crypto":
    tickers = st.multiselect("Search Cryptos (by name or symbol)", options=["bitcoin", "ethereum", "solana", "dogecoin", "cardano"], default=["bitcoin"])
else:
    tickers = upload_watchlist()

# 🔍 Run Scan
if tickers and st.button("🔍 Run Scan"):
    results = []
    detailed_crypto_scores = {}

    with st.spinner("🔎 Scanning..."):
        for ticker in tickers:
            if data_type == "Stocks":
                df = load_ticker_data(ticker)
                if df is None or df.empty:
                    if debug_mode:
                        st.warning(f"{ticker}: Skipped — no data returned.")
                    continue

                if debug_mode:
                    st.write(f"🔍 Raw data preview for {ticker}", df.tail())
                df.attrs["ticker"] = ticker  # Store ticker in DataFrame attributes
                scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
                if not scores:
                    if debug_mode:
                        st.warning(f"{ticker}: Skipped — scoring failed or insufficient indicators.")
                    continue

                result = {"Ticker": ticker}
                result.update(scores)
                result.update(indicators)

                if debug_mode:
                    st.write(f"✅ Final result for {ticker}", result)

                results.append(result)

            else:  # ✅ CRYPTO MODE
                coin_data = fetch_crypto_data(ticker)
                if not coin_data:
                    if debug_mode:
                        st.warning(f"{ticker}: Skipped — no crypto data retrieved.")
                    continue

                score, grade, breakdown = score_crypto(coin_data)
                try:
                    rebound = breakdown.get("Rebound Potential", "0")
                    rebound_value = float(rebound.split("%")[-2].strip()) if "%" in rebound else 0
                except:
                    rebound_value = 0

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
                if debug_mode:
                    st.write(f"✅ Final result for {ticker} (crypto)", result)

                results.append(result)
                detailed_crypto_scores[ticker] = coin_data

    # ✅ Results Summary
    if results:
        df_all = pd.DataFrame(results)

        for col in df_all.select_dtypes(include='object').columns:
            df_all[col] = df_all[col].astype(str).str.replace(r"Name:.*", "", regex=True).str.strip()

        st.write("📦 Raw scan results (pre-filter):", df_all)

        df_filtered = filter_dataframe(df_all, min_short_score, min_long_score)

        if not df_filtered.empty:
            st.markdown("### ⭐ Top Picks Summary")
            render_summary_box(df_filtered)

            st.markdown("### 📋 Scored Results")
            render_score_table(df_filtered)

            st.markdown("### 🧠 AI Market Commentary")
            summary = generate_ai_summary(df_filtered, openai_key)
            st.info(summary)

            if data_type == "Stocks":
                st.markdown("### 💡 Options Suggestions & Trade Ideas")
                option_tips = generate_ai_option_recommendations(df_filtered, openai_key)
                st.success(option_tips)

                st.markdown("### ⭐ Strategy Confidence Summary (AI)")
                strategy_summary = generate_strategy_confidence(df_filtered, openai_key)
                st.info(strategy_summary)

            st.markdown("### 📈 Charts by Ticker")
            scroll_container = st.container()
            with scroll_container:
                scroll_columns = st.columns(len(df_filtered))
                for i, ticker in enumerate(df_filtered["Ticker"].tolist()):
                    chart_data = load_ticker_data(ticker) if data_type == "Stocks" else detailed_crypto_scores.get(ticker, {})
                    if chart_data is not None and not chart_data.empty:
                        with scroll_columns[i]:
                            st.subheader(f"[{ticker}](#{ticker})")
                            if data_type == "Stocks":
                                display_charts(ticker, chart_data)
                            elif "market_data" in chart_data:
                                st.line_chart(chart_data["market_data"]["sparkline_7d"]["price"][-168:])

            if data_type == "Stocks":
                st.markdown("### 📅 Company Overview & Insights")
                for ticker in df_filtered["Ticker"].tolist():
                    with st.expander(f"Show overview for {ticker}"):
                        overview = fetch_company_overview(ticker)
                        company_summary = generate_company_summary(overview, openai_key)
                        st.markdown(company_summary)
            else:
                st.markdown("### 🧠 Crypto Overviews")
                for ticker in df_filtered["Ticker"].tolist():
                    with st.expander(f"Show crypto overview for {ticker}"):
                        coin_data = detailed_crypto_scores.get(ticker)
                        if coin_data:
                            summary = generate_crypto_summary(coin_data, openai_key)
                            st.markdown(summary)

            if st.button("📤 Send Alert Email", key="send_email_button"):
                html_content = df_filtered.to_html(index=False)
                status = send_alert_email(sendgrid_key, email_to, "📈 Scan Results", html_content)
                st.success(f"Email sent! Status: {status}")
        else:
            st.warning("⚠️ No tickers met the minimum scoring criteria.")
    else:
        st.warning("⚠️ No results found or tickers failed to load.")

