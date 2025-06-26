from openai import OpenAI
import pandas as pd

def generate_ai_summary(df, openai_key):
    client = OpenAI(api_key=openai_key)
    tickers = df["Ticker"].tolist()
    summary_prompt = f"""
You are a seasoned financial analyst and options strategist.
Analyze the following stocks using their recent technical indicators and scoring summary.

Data:
{df[["Ticker", "Short-Term Score", "Long-Term Score", "Pattern", "Rebound %", "Price ($)", "50-Day SMA", "100-Day SMA", "RSI", "MACD"]].to_string(index=False)}

Instructions:
- Provide a summary of short-term and long-term trends.
- Highlight top breakout or reversal opportunities.
- Recommend basic options strategies to maximize gains or minimize losses:
    - Use covered calls, debit spreads, LEAPS, or protective puts where appropriate.
    - Specify entry timing, risk profile, and ideal expiration windows.
- Flag tickers that appear overbought or high-risk.

Finish with a concise 2–3 line outlook for each ticker.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Summary Error: {e}"
    
def generate_ai_option_recommendations(df, openai_key):
    client = OpenAI(api_key=openai_key)
    tickers = df["Ticker"].tolist()
    options_prompt = f"""
    You are an experienced options trader. For the following stocks, suggest potential options trading strategies (e.g., long call, covered call, put spread, straddle, etc.) based on their technical scoring and patterns.

    Consider:
    - Short-Term and Long-Term Scores
    - RSI and MACD
    - Rebound %
    - General momentum or consolidation

    Provide 1–2 strategy ideas per ticker:

    {df[['Ticker', 'Short-Term Score', 'Long-Term Score', 'Pattern', 'Rebound %', 'RSI', 'MACD']].to_string(index=False)}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": options_prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Options Error: {e}"


def generate_company_ai_review(prompt, openai_key):
    client = OpenAI(api_key=openai_key)
    try:
        if not prompt.strip():
            return "AI Company Summary Error: Empty prompt provided."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Company Summary Error: {e}"

def generate_strategy_confidence(df, openai_key):
    client = OpenAI(api_key=openai_key)
    prompt = f"""
Given the following stock scan data, assess which stocks would most likely yield a profitable trade based on a low-interaction, short-term breakout strategy. Prioritize those meeting the following:

- Short-Term Score ≥ 3
- Long-Term Score ≥ 2
- RSI between 50–75
- MACD > 0
- Rebound % ≥ 5
- Price > 50-Day SMA
- Volume ≥ Avg Volume

Also, rank by confidence level (1-5 stars).

{df[['Ticker', 'Short-Term Score', 'Long-Term Score', 'RSI', 'MACD', 'Rebound %', 'Price ($)', '50-Day SMA', 'Current Volume', 'Avg Volume (20D)']].to_string(index=False)}

Return a bullet list with confidence stars and short reasoning.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content