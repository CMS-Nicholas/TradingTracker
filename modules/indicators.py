import pandas as pd
import numpy as np

def calculate_tsi(data: pd.DataFrame, r: int = 6, s: int = 13) -> pd.DataFrame:
    """
    Calculate the True Strength Index (TSI) and signal line.
    Parameters:
        r: First EMA period (default 6)
        s: Second EMA period (default 13)
    Returns:
        DataFrame with added TSI and TSI_Signal columns
    """
    delta = data['Close'].diff()
    abs_delta = delta.abs()

    ema1 = delta.ewm(span=r, adjust=False).mean()
    ema2 = ema1.ewm(span=s, adjust=False).mean()

    abs_ema1 = abs_delta.ewm(span=r, adjust=False).mean()
    abs_ema2 = abs_ema1.ewm(span=s, adjust=False).mean()

    tsi = 100 * (ema2 / abs_ema2)
    signal = tsi.ewm(span=9, adjust=False).mean()

    data['TSI'] = tsi
    data['TSI_Signal'] = signal
    return data

def detect_hidden_bullish_divergence(data: pd.DataFrame, window: int = 20) -> bool:
    """
    Detect hidden bullish divergence: higher low in price and lower low in TSI.
    Parameters:
        window: number of periods to scan for swing points
    Returns:
        True if divergence is found, else False
    """
    if 'TSI' not in data.columns:
        raise ValueError("TSI must be calculated before checking for divergence.")

    lows = data['Close'].rolling(window).apply(lambda x: x[0] < x[1:-1].min() and x[0], raw=False)
    swing_lows = data[lows.notnull()]

    if len(swing_lows) < 2:
        return False

    last_two = swing_lows.tail(2)
    prices = last_two['Close'].values
    tsi_vals = last_two['TSI'].values

    return prices[1] > prices[0] and tsi_vals[1] < tsi_vals[0]
