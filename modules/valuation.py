import yfinance as yf

def get_valuation_metrics(ticker_symbol):
    print(f"\n🔍 Fetching data for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)

    try:
        info = ticker.info or {}
        print(f"\n📦 Raw info for {ticker_symbol}:\n{info}")
        price = info.get("currentPrice") or info.get("regularMarketPrice") or ticker.fast_info.get("lastPrice")
        pe_ratio = info.get("trailingPE")
        pb_ratio = info.get("priceToBook")
        eps = info.get("trailingEps")
        analyst_rating = info.get("recommendationKey", "none")

        # Fallback for target price
        target_price = info.get("targetMeanPrice")
        if not target_price:
            try:
                print(f"🔍 Attempting fallback via analyst_price_target for {ticker_symbol}...")
                targets = ticker.analyst_price_target
                print(f"📈 analyst_price_target: {targets}")
                target_price = targets.get("mean") if targets else None
            except:
                target_price = None

    except Exception as e:
        print(f"⚠️ Failed to fetch data for {ticker_symbol}: {e}")
        return None

    if not price or not eps:
        print(f"⚠️ Missing critical data for {ticker_symbol} (price={price}, eps={eps})")
        return None

    return {
        "price": price,
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "eps": eps,
        "target_price": target_price,
        "analyst_rating": analyst_rating
    }

def compute_valuation_score(metrics):
    if metrics is None:
        return 0  # neutral if no data

    score = 0

    # --- P/E Ratio Scoring (Assume Sector Avg P/E ~20) ---
    pe = metrics.get("pe_ratio")
    if pe:
        if pe > 26:  # over 130% of avg
            score -= 1
        elif pe < 14:  # under 70% of avg
            score += 1

    # --- P/B Ratio Scoring ---
    pb = metrics.get("pb_ratio")
    if pb:
        if pb > 3:
            score -= 1
        elif pb < 1:
            score += 1

    # --- Earnings Yield Scoring ---
    price = metrics.get("price")
    eps = metrics.get("eps")
    if eps and price:
        ey = eps / price
        if ey > 0.08:
            score += 1
        elif ey < 0.04:
            score -= 1

    # --- Analyst Sentiment Score ---
    sentiment = metrics.get("analyst_rating", "none")
    if sentiment == "strong_buy":
        score += 1
    elif sentiment == "buy":
        score += 0.5
    elif sentiment == "sell":
        score -= 0.5
    elif sentiment == "strong_sell":
        score -= 1

    # --- Fair Value Gap ---
    target = metrics.get("target_price")
    if target and price:
        gap = (target - price) / price
        if gap > 0.10:
            score += 1
        elif gap < -0.10:
            score -= 1

    # Normalize score to -1, 0, 1
    if score > 1:
        return 1
    elif score < -1:
        return -1
    else:
        return 0

def get_and_score_valuation(ticker):
    metrics = get_valuation_metrics(ticker)
    return compute_valuation_score(metrics)

# Example usage:
if __name__ == "__main__":
    test_ticker = "AAPL"
    metrics = get_valuation_metrics(test_ticker)
    print(f"\n📊 Raw Valuation Metrics for {test_ticker}:\n{metrics}")

    if metrics:
        val_score = compute_valuation_score(metrics)
        print(f"\n✅ Valuation Score: {val_score}")
    else:
        print("⚠️ No metrics available to score.")
