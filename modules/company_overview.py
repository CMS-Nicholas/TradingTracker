import yfinance as yf
from datetime import datetime, timedelta
from modules.ai_commentary import generate_company_ai_review
import streamlit as st

def fetch_company_overview(ticker):
    stock = yf.Ticker(ticker)
    info = {}
    calendar = None
    news = []
    history = None
    insider = None

    try:
        info = stock.get_info()
    except Exception as e:
        st.warning(f"Unable to load info for {ticker}: {e}")

    try:
        calendar_raw = stock.calendar
        if isinstance(calendar_raw, dict) or calendar_raw is None:
            calendar = None
        elif hasattr(calendar_raw, 'empty') and not calendar_raw.empty:
            calendar = calendar_raw.T
    except Exception as e:
        st.warning(f"Unable to load earnings calendar for {ticker}: {e}")

    try:
        news = stock.news if hasattr(stock, "news") else []
    except Exception as e:
        st.warning(f"Unable to load news for {ticker}: {e}")

    try:
        history = stock.history(period="2mo")
    except Exception as e:
        st.warning(f"Unable to load price history for {ticker}: {e}")

    try:
        insider = stock.insider_transactions if hasattr(stock, "insider_transactions") else None
    except Exception as e:
        st.warning(f"Unable to load insider transactions for {ticker}: {e}")

    return {
        "info": info,
        "calendar": calendar,
        "news": news,
        "history": history,
        "insider": insider
    }


def generate_company_summary(overview_data, openai_key):
    info = overview_data['info']
    ticker = info.get("symbol", "N/A")
    name = info.get("shortName", ticker)
    summary = info.get("longBusinessSummary", "")
    pe_ratio = info.get("trailingPE", "N/A")
    revenue = info.get("totalRevenue", "N/A")
    gross_margins = info.get("grossMargins", "N/A")
    calendar = overview_data['calendar']
    earnings_date = str(calendar.iloc[0][0]) if calendar is not None else "N/A"

    news_data = overview_data['news'] if isinstance(overview_data['news'], list) else []
    news_summaries = "\n".join(
        f"- {item.get('title')}: {item.get('link', '')}" 
        for item in news_data[:5] if item.get("title")
    ) if news_data else "No recent news."

    # DEBUG OUTPUT
    with st.expander(f"\U0001F4CA Raw Data Preview: {ticker}"):
        st.markdown(f"**Company Name:** {name}")
        st.markdown(f"**Ticker:** {ticker}")
        st.markdown(f"**Business Summary:** {summary or 'N/A'}")
        st.markdown(f"**P/E Ratio:** {pe_ratio}")
        st.markdown(f"**Revenue:** {revenue}")
        st.markdown(f"**Gross Margins:** {gross_margins}")
        st.markdown(f"**Earnings Date:** {earnings_date}")
        st.markdown("**Recent News Headlines:**")
        st.markdown(news_summaries)

    if not summary and news_summaries == "No recent news." and pe_ratio == "N/A" and earnings_date == "N/A":
        return "⚠️ No sufficient data available for this company to generate a summary."

    message = f"""
You are an AI financial analyst. Summarize the following company for a potential investor:

**Company Name:** {name}
**Ticker:** {ticker}
**Business Summary:** {summary}
**P/E Ratio:** {pe_ratio}
**Revenue:** {revenue}
**Gross Margins:** {gross_margins}
**Upcoming Earnings Date:** {earnings_date}

**Recent News (30 days):**
{news_summaries}

Please identify any recent developments that could act as a catalyst for stock movement based on news or insider/hedge fund trends.
"""

    return generate_company_ai_review(message, openai_key)
