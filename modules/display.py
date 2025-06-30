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