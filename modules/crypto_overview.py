import streamlit as st
import requests
from modules.ai_commentary import generate_company_ai_review
from modules.crypto_scoring import score_crypto

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_crypto_data(coin_id):
    data = {}
    try:
        resp = requests.get(f"{COINGECKO_BASE}/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=true&developer_data=true&sparkline=true")
        if resp.status_code == 200:
            data = resp.json()
        else:
            st.warning(f"Failed to fetch data for {coin_id}: {resp.status_code}")
    except Exception as e:
        st.warning(f"Error fetching crypto data for {coin_id}: {e}")
    return data


def get_coin_list():
    try:
        resp = requests.get(f"{COINGECKO_BASE}/coins/list")
        if resp.status_code == 200:
            return sorted(resp.json(), key=lambda x: x['name'])
    except Exception as e:
        st.warning(f"Unable to fetch coin list: {e}")
    return []


def generate_crypto_summary(coin_data, openai_key):
    name = coin_data.get("name", "N/A")
    symbol = coin_data.get("symbol", "N/A").upper()
    market_cap = coin_data.get("market_data", {}).get("market_cap", {}).get("usd", "N/A")
    volume = coin_data.get("market_data", {}).get("total_volume", {}).get("usd", "N/A")
    price_change_24h = coin_data.get("market_data", {}).get("price_change_percentage_24h", "N/A")
    description = coin_data.get("description", {}).get("en", "")

    score, grade, detail_breakdown = score_crypto(coin_data)

    st.markdown(f"### 📊 Grading Breakdown for {symbol}")
    st.markdown(f"**Overall Score:** {score} — **Rating:** {grade}")
    for label, value in detail_breakdown.items():
        st.markdown(f"- **{label}:** {value}")

    # Simple 7d sparkline visual
    prices = coin_data.get("market_data", {}).get("sparkline_7d", {}).get("price", [])
    if prices:
        st.line_chart(prices[-168:])  # last 7 days (hourly)

    prompt = f"""
You are a crypto market analyst. Based on the current statistics and project description, provide a brief investment summary for:

**Name:** {name}
**Symbol:** {symbol}
**Market Cap (USD):** {market_cap}
**24h Volume (USD):** {volume}
**24h Price Change (%):** {price_change_24h}
**Overall Score:** {score} — Rating: {grade}

**Breakdown:**
"""
    for k, v in detail_breakdown.items():
        prompt += f"- {k}: {v}\n"

    prompt += f"\n**Project Description:**\n{description}\n"
    prompt += "\nHighlight any risks or upcoming catalysts based on market data."

    return generate_company_ai_review(prompt, openai_key)
