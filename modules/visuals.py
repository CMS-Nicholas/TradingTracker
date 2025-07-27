import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def display_charts(ticker, df, divergence_found=False):
    st.subheader(f"📊 Charts for {ticker}")

    # Price + SMA
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Close'], label='Price', color='blue')
    ax.plot(df['Close'].rolling(50).mean(), label='50 SMA', linestyle='--')
    ax.plot(df['Close'].rolling(100).mean(), label='100 SMA', linestyle='--')
    ax.set_title(f"{ticker} Price and SMA")
    ax.legend()
    st.pyplot(fig)

    # RSI
    fig2, ax2 = plt.subplots(figsize=(10, 2))
    rsi = df['Close'].diff().clip(lower=0).rolling(14).mean() / (
        -df['Close'].diff().clip(upper=0).rolling(14).mean())
    rsi = 100 - (100 / (1 + rsi))
    ax2.plot(rsi, color='orange')
    ax2.axhline(70, linestyle='--', color='red', label='Overbought')
    ax2.axhline(30, linestyle='--', color='green', label='Oversold')
    ax2.set_title(f"{ticker} RSI (14)")
    ax2.legend()
    st.pyplot(fig2)

    # TSI + Signal
    if 'TSI' in df.columns and 'TSI_Signal' in df.columns:
        fig3, ax3 = plt.subplots(figsize=(10, 3))
        ax3.plot(df['TSI'], label='TSI', color='purple')
        ax3.plot(df['TSI_Signal'], label='Signal Line', color='orange', linestyle='--')
        ax3.axhline(0, color='gray', linestyle=':')
        ax3.set_title(f"{ticker} True Strength Index (TSI)")
        ax3.legend()

        # Annotate divergence bars
        if divergence_found:
            recent_tsi = df['TSI'].tail(30)
            min_idx = recent_tsi.idxmin()
            max_idx = recent_tsi[recent_tsi.index < min_idx].idxmin()
            ax3.annotate('⬇️', xy=(min_idx, df['TSI'].loc[min_idx]), textcoords='offset points', xytext=(0,10), ha='center', color='green')
            ax3.annotate('⬇️', xy=(max_idx, df['TSI'].loc[max_idx]), textcoords='offset points', xytext=(0,10), ha='center', color='red')

        st.pyplot(fig3)

        if divergence_found:
            st.success("✨ Hidden Bullish Divergence detected — boosting score!")

def display_divergence_info(scores: dict, indicators: dict, divergence_found: bool):
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Divergence Signal", "Yes" if divergence_found else "No")

    with col2:
        if divergence_found:
            st.success("Hidden Bullish Divergence detected: +1 to Short-Term Score")
        else:
            st.info("No divergence found this session")

    st.write("### Score Breakdown")
    st.write({k: v for k, v in scores.items() if k in ["Short-Term Score", "Long-Term Score", "Pattern"]})

def plot_bollinger_overlay(ticker, df):
    st.subheader(f"📉 Bollinger Band Overlay for {ticker}")

    window = 20
    std_dev = 2

    df['SMA'] = df['Close'].rolling(window=window).mean()
    df['Upper'] = df['SMA'] + std_dev * df['Close'].rolling(window=window).std()
    df['Lower'] = df['SMA'] - std_dev * df['Close'].rolling(window=window).std()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Close'], label='Close', color='blue')
    ax.plot(df['SMA'], label='SMA (20)', linestyle='--', color='gray')
    ax.plot(df['Upper'], label='Upper Band', linestyle='--', color='green')
    ax.plot(df['Lower'], label='Lower Band', linestyle='--', color='red')
    ax.fill_between(df.index, df['Upper'], df['Lower'], color='gray', alpha=0.1)

    ax.set_title(f"{ticker} Bollinger Band Squeeze")
    ax.legend()
    st.pyplot(fig)