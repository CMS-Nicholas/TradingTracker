import streamlit as st
import pandas as pd

def upload_watchlist():
    uploaded_file = st.sidebar.file_uploader("Upload Ticker CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            tickers = df.iloc[:, 0].dropna().astype(str).str.upper().tolist()
            return tickers
        except Exception as e:
            st.sidebar.error(f"Error reading uploaded file: {e}")
    return []
