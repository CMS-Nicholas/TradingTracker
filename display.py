import streamlit as st
import pandas as pd

def render_score_table(df):
    def highlight_scores(val):
        color = 'background-color: lightgreen' if val >= 4 else ''
        return color

    st.subheader("📋 Scored Results")
    styled_df = df.style.applymap(highlight_scores, subset=["Short-Term Score"])
    st.dataframe(styled_df, use_container_width=True)

def render_summary_box(df):
    st.markdown("### ⭐ Top Picks Summary")
    if not df.empty:
        top = df.sort_values("Short-Term Score", ascending=False).head(3)
        st.markdown("Top 3 by Short-Term Score:")
        st.table(top[["Ticker", "Short-Term Score", "Long-Term Score", "Price ($)"]])