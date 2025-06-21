import streamlit as st
import pandas as pd

# === Load secrets from Streamlit Cloud ===
sendgrid_key = st.secrets["SENDGRID_KEY"]
openai_key = st.secrets["OPENAI_KEY"]
email_to = st.secrets["EMAIL_TO"]


from modules.data_loader import load_ticker_data
from modules.scoring import compute_scores
from modules.visuals import display_charts
from modules.filters import filter_dataframe
from modules.display import render_score_table, render_summary_box
from modules.upload import upload_watchlist
from modules.email_alerts import send_alert_email
from modules.ai_commentary import generate_ai_summary


if st.button("📤 Send Alert Email", key="send_email_button"):
    status = send_alert_email(sendgrid_api_key=st.secrets["SENDGRID_KEY"],
                              to_email="you@example.com",
                              subject="📈 Daily Stock Scan",
                              html_content=sorted.to_html(index=False))
    st.success(f"Email sent! Status: {status}")


st.set_page_config(page_title="📈 Modular Stock Scanner", layout="wide")
st.title("📈 Modular Smart Stock Scanner")

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
    for ticker in tickers:
        df = load_ticker_data(ticker)
        if df is not None:
            scores, indicators = compute_scores(df, rsi_threshold, rsi_long_threshold, vol_multiplier)
            results.append({**scores, **indicators, "Ticker": ticker})

    if results:
        df_all = pd.DataFrame(results)
        df_filtered = filter_dataframe(df_all, min_short_score, min_long_score)
        render_summary_box(df_filtered)
        render_score_table(df_filtered)
        for ticker in df_filtered["Ticker"]:
            data = load_ticker_data(ticker)
            display_charts(ticker, data)
    
    # After filtering and scoring:
    if not df_filtered.empty:
        st.markdown("### 🧠 AI-Generated Market Summary")
        summary = generate_ai_summary(df_filtered, openai_key)
        st.info(summary)
    else:
        st.warning("No results found or tickers failed to load.")

