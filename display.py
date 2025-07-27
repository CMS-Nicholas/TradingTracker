import streamlit as st
import pandas as pd

def render_score_table(df):
    def highlight_scores(val):
        color = 'background-color: lightgreen' if val >= 4 else ''
        return color

    st.subheader("📋 Scored Results")
    columns_to_display = [
        "Ticker", "Price ($)", "Short-Term Score", "Long-Term Score", "RSI", "MACD",
        "Suggested Entry", "Exit Zone", "Pattern", "Daily % Change", "Weekly % Change"
    ]

    styled_df = df.style.applymap(highlight_scores, subset=["Short-Term Score"])
    st.dataframe(styled_df[columns_to_display], use_container_width=True)
    if st.checkbox("✅ Show only suggested entries"):
        df_filtered = df[df["Suggested Entry"] == "✅"]
        st.dataframe(df_filtered[columns_to_display], use_container_width=True)

def render_summary_box(df):
    st.markdown("### ⭐ Top Picks Summary")
    if not df.empty:
        top = df.sort_values("Short-Term Score", ascending=False).head(3)
        st.markdown("Top 3 by Short-Term Score:")
        st.table(top[["Ticker", "Short-Term Score", "Long-Term Score", "Price ($)"]])

def render_discovery_results(discovery_results):
    if not discovery_results:
        st.warning("No stocks found within the selected price range.")
        return

    st.subheader("🔍 Discovery Scanner Results")
    
    table_data = []
    for ticker, scores in discovery_results:
        table_data.append({
            "Ticker": ticker,
            "Short-Term Score": scores.get("short_term_score", 0),
            "Long-Term Score": scores.get("long_term_score", 0),
            "Pump Score": scores.get("pump_score", 0),
            "Volume Surge": "✅" if scores.get("volume_surge") else "",
            "Breakout": "🚀" if scores.get("breakout") else "",
            "Tags": ", ".join(scores.get("tags", [])),
            "Price": scores.get("price", "N/A")
        })

    df = pd.DataFrame(table_data)
    
    # Optional: Sort by Pump Score + Short-Term Score
    df["Sort Score"] = df["Pump Score"] + df["Short-Term Score"]
    df = df.sort_values(by="Sort Score", ascending=False).drop(columns=["Sort Score"])

    st.dataframe(df.reset_index(drop=True), use_container_width=True)