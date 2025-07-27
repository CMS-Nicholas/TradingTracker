import streamlit as st
import matplotlib.pyplot as plt

def display_charts(ticker, df):
    st.subheader(f"📊 Charts for {ticker}")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Close'], label='Price', color='blue')
    ax.plot(df['Close'].rolling(50).mean(), label='50 SMA', linestyle='--')
    ax.plot(df['Close'].rolling(100).mean(), label='100 SMA', linestyle='--')
    ax.set_title(f"{ticker} Price and SMA")
    ax.legend()
    st.pyplot(fig)

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