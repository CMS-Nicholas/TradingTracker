import streamlit as st
import pandas as pd

def upload_watchlist():
    st.sidebar.markdown("### 📥 Upload Watchlist or Enter Manually")
    uploaded_file = st.sidebar.file_uploader("Upload CSV (must contain 'Ticker' column)", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if "Ticker" in df.columns:
                tickers = df["Ticker"].dropna().astype(str).tolist()
                st.sidebar.success(f"✅ Loaded {len(tickers)} tickers from file.")
                return tickers
            else:
                st.sidebar.error("❌ CSV must have a 'Ticker' column.")
                return []
        except Exception as e:
            st.sidebar.error(f"❌ Error reading file: {e}")
            return []
    else:
        manual_input = st.sidebar.text_area("Or paste tickers (comma-separated):", "AAPL, MSFT, AMD")
        tickers = [t.strip().upper() for t in manual_input.split(",") if t.strip()]
        if tickers:
            st.sidebar.success(f"✅ Using {len(tickers)} manually entered tickers.")
        return tickers
