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