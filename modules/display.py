import streamlit as st
import pandas as pd

def render_score_table(df):
    if df.empty:
        st.warning("No data available to display.")
        return

    st.markdown("#### ✅ Full Scored Data")
    
    def highlight_valuation(val):
        if val == 1:
            return 'background-color: #d4edda; color: #155724'  # green
        elif val == -1:
            return 'background-color: #f8d7da; color: #721c24'  # red
        elif val == 0:
            return 'background-color: #fff3cd; color: #856404'  # yellow
        return ''

    styled_df = df.style.applymap(highlight_valuation, subset=['Valuation Score'])
    st.dataframe(styled_df, use_container_width=True)
    


def render_summary_box(df):
    if df.empty:
        st.warning("No data available for Top Picks Summary.")
        return

    st.markdown("#### ✅ Top 3 by Short-Term Score")
    top = df.sort_values("Short-Term Score", ascending=False).head(3)
    st.table(top[["Ticker", "Short-Term Score", "Long-Term Score", "Price ($)"]].reset_index(drop=True))


def render_discovery_results(discovery_results):
    if not discovery_results:
        st.warning("No discovery results found.")
        return

    st.subheader("🔍 Discovery Results (Top Candidates)")

    rows = []
    for ticker, data in discovery_results:
        rows.append({
            "Ticker": ticker,
            "Short-Term Score": data.get("Short-Term Score", 0),
            "Long-Term Score": data.get("Long-Term Score", 0),
            "Perfect Setup Score": data.get("Perfect Setup Score", "N/A"),
            "Pattern": data.get("Pattern", ""),
            "Rebound %": data.get("Rebound %", 0),
            "Valuation Score": data.get("Valuation Score", 0),
            "Price ($)": data.get("price", "N/A"),
            "RSI": data.get("RSI", ""),
            "MACD": data.get("MACD", ""),
            "Volume": data.get("Current Volume", ""),
            "Breakout Tag": "🚀" if "Breakout" in data.get("Pattern", "") else ""
       
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)