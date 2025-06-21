def filter_dataframe(df, min_short, min_long):
    filtered = df.copy()
    filtered = filtered[
        (filtered["Short-Term Score"] >= min_short) &
        (filtered["Long-Term Score"] >= min_long)
    ]
    return filtered