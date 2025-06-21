import streamlit as st
import pandas as pd

def render_score_table(df):
    if df.empty:
        st.warning("No data available to display.")
        return

    st.markdown("#### ✅ Full Scored Data")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)


def render_summary_box(df):
    if df.empty:
        st.warning("No data available for Top Picks Summary.")
        return

    st.markdown("#### ✅ Top 3 by Short-Term Score")
    top = df.sort_values("Short-Term Score", ascending=False).head(3)
    st.table(top[["Ticker", "Short-Term Score", "Long-Term Score", "Price ($)"]].reset_index(drop=True))