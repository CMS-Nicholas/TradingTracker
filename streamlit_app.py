import streamlit as st
import pandas as pd
from modules.data_loader import load_ticker_data
from modules.scoring import compute_scores
from modules.visuals import display_charts
from modules.filters import filter_dataframe
from modules.display import render_score_table, render_summary_box
from modules.upload import upload_watchlist
from modules.ai_commentary import generate_ai_summary
from modules.email_alerts import send_alert_email
from modules.company_overview import fetch_company_overview, generate_company_summary

st.set_page_config(page_title="📈 Modular Stock Scanner", layout="wide")
st.title("📈 Modular Smart Stock Scanner")

# === Load secrets from Streamlit Cloud ===
sendgrid_key = st.secrets["SENDGRID_KEY"]
openai_key = st.secrets["OPENAI_KEY"]
email_to = st.secrets["EMAIL_TO"]

# Sidebar Controls
st.sidebar.header("⚙️ Scan Controls")
rsi_threshold = st.sidebar.slider("RSI Threshold (Short-Term)", 40, 70, 55)
rsi_long_threshold = st.sidebar.slider("RSI Threshold (Long-Term)", 40, 70, 60)
vol_multiplier = st.sidebar.slider("Volume Multiplier", 1.0, 3.0, 1.5)
min_short_score = st.sidebar.slider("Min Short-Term Score", 0, 5, 3)
min_long_score = st.sidebar.slider("Min Long-Term Score", 0, 3, 2)

# Watchlist Upload or Manual Entry
tickers = upload_watchlist()

if tickers and st.button("🔍 Run Scan"):
    results = []

    with st.spinner("🔎 Scanning stocks..."):
        for ticker in tickers:
            df = load_ticker_data(ticker)
            if df is not None:
                scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
                result = {"Ticker": ticker}
                result.update(scores)
                result.update(indicators)
                results.append(result)

    if results:
        df_all = pd.DataFrame(results)

        st.write("Raw scan results:", df_all)

        df_filtered = filter_dataframe(df_all, min_short_score, min_long_score)

        if not df_filtered.empty:
            st.markdown("### ⭐ Top Picks Summary")
            render_summary_box(df_filtered)
            st.markdown("### 📋 Scored Results")
            render_score_table(df_filtered)

            st.markdown("### 🧠 AI-Generated Market Summary")
            summary = generate_ai_summary(df_filtered, openai_key)
            st.info(summary)

            st.markdown("### 📈 Charts by Ticker")
            scroll_container = st.container()
            with scroll_container:
                scroll_columns = st.columns(len(df_filtered))
                for i, ticker in enumerate(df_filtered["Ticker"].tolist()):
                    chart_data = load_ticker_data(ticker)
                    if chart_data is not None:
                        with scroll_columns[i]:
                            st.subheader(f"[{ticker}](#{ticker})")
                            display_charts(ticker, chart_data)

            # Company Overview Expansion
            st.markdown("### 📅 Company Overview & Insights")
            for ticker in df_filtered["Ticker"].tolist():
                with st.expander(f"Show overview for {ticker}"):
                    overview = fetch_company_overview(ticker)
                    company_summary = generate_company_summary(overview, openai_key)
                    st.markdown(company_summary)

            if st.button("📤 Send Alert Email", key="send_email_button"):
                html_content = df_filtered.to_html(index=False)
                status = send_alert_email(sendgrid_key, email_to, "📈 Stock Scan Results", html_content)
                st.success(f"Email sent! Status: {status}")
        else:
            st.warning("⚠️ No tickers met the minimum scoring criteria.")
    else:
        st.warning("⚠️ No results found or tickers failed to load.")
