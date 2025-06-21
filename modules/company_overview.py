import yfinance as yf
import openai
from datetime import datetime, timedelta


def fetch_company_overview(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        calendar = stock.calendar.T if not stock.calendar.empty else None
    except Exception:
        info, calendar = {}, None

    try:
        news = stock.news[:10] if hasattr(stock, "news") else []
    except Exception:
        news = []

    try:
        history = stock.history(period="2mo")
        insider = stock.insider_transactions if hasattr(stock, "insider_transactions") else None
    except Exception:
        history, insider = None, None

    return {
        "info": info,
        "calendar": calendar,
        "news": news,
        "history": history,
        "insider": insider
    }


def generate_company_summary(overview_data, openai_key):
    openai.api_key = openai_key

    ticker = overview_data['info'].get("symbol", "N/A")
    name = overview_data['info'].get("shortName", ticker)
    summary = overview_data['info'].get("longBusinessSummary", "")
    pe_ratio = overview_data['info'].get("trailingPE", "N/A")
    earnings_date = str(overview_data['calendar'].iloc[0][0]) if overview_data['calendar'] is not None else "N/A"

    news_summaries = "\n".join(
        f"- {item.get('title', 'No Title')}: {item.get('link', '')}" for item in overview_data['news'][:5]
    ) if overview_data['news'] else "No recent news."

    message = f"""
You are an AI financial analyst. Summarize the following company for a potential investor:

**Company Name:** {name}
**Ticker:** {ticker}
**Business Summary:** {summary}
**P/E Ratio:** {pe_ratio}
**Upcoming Earnings Date:** {earnings_date}

**Recent News (30 days):**
{news_summaries}

Note any significant insider trading activity and trend over the last 60 days if available.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"AI Summary Error: {e}"
