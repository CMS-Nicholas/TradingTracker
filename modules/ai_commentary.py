from openai import OpenAI

def generate_ai_summary(df, openai_key):
    client = OpenAI(api_key=openai_key)
    ticker = df["Ticker"].tolist()
    summary_prompt = f"""You are a financial analyst who is an expert in stock investing. Provide a brief but insightful summary of the following stocks based on their statistics provided. Detail any suggestions on options and long term and short term gains.
    
Stocks:
{df[["Ticker", "Short-Term Score", "Long-Term Score", "Price ($)","50-Day SMA","100-Day SMA","RSI", "Current Volume","Avg Volume (20D)" ]].to_string(index=False)}

Highlight the best short-term and long-term opportunities and note any that should be avoided.
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