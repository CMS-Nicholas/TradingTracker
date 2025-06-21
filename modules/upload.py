import streamlit as st
import pandas as pd

def upload_watchlist():
    st.sidebar.markdown("### 📥 Upload Watchlist or Enter Manually")
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Ticker column)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "Ticker" in df.columns:
            return df["Ticker"].dropna().astype(str).tolist()
        else:
            st.sidebar.error("CSV must have a 'Ticker' column.")
            return []
    else:
        manual_input = st.sidebar.text_area("Or paste tickers (comma-separated):", "AAPL, MSFT, AMD")
        return [t.strip().upper() for t in manual_input.split(",") if t.strip()]