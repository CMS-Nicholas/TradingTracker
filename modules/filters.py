import pandas as pd

def filter_dataframe(df: pd.DataFrame, min_short: int, min_long: int) -> pd.DataFrame:
    df = df.copy()

    print(f"📊 Filtering {len(df)} rows with thresholds: ST ≥ {min_short}, LT ≥ {min_long}")

    # Ensure scoring columns exist and are numeric
    df["Short-Term Score"] = pd.to_numeric(df.get("Short-Term Score", pd.Series(dtype=float)), errors="coerce")
    df["Long-Term Score"] = pd.to_numeric(df.get("Long-Term Score", pd.Series(dtype=float)), errors="coerce")

    before_drop = len(df)
    df.dropna(subset=["Short-Term Score", "Long-Term Score"], inplace=True)
    after_drop = len(df)
    print(f"❎ Dropped {before_drop - after_drop} rows due to missing scores.")

    # Drop any nested Series or malformed columns
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, pd.Series)).any():
            df[col] = df[col].apply(lambda x: x.iloc[0] if isinstance(x, pd.Series) and not x.empty else x)

    # Ensure floats
    df["Short-Term Score"] = df["Short-Term Score"].astype(float)
    df["Long-Term Score"] = df["Long-Term Score"].astype(float)

    # Final filtering
    filtered = df[
        (df["Short-Term Score"] >= min_short) &
        (df["Long-Term Score"] >= min_long)
    ]

    print(f"✅ Filtered down to {len(filtered)} rows.")
    return filtered.reset_index(drop=True)
