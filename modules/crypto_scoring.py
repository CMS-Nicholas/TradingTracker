def score_crypto(coin_data):
    market_data = coin_data.get("market_data", {})
    community_data = coin_data.get("community_data", {})
    developer_data = coin_data.get("developer_data", {})

    score = 0
    details = {}

    # --- 7-Day Momentum ---
    change_7d = market_data.get("price_change_percentage_7d", 0)
    if change_7d >= 15:
        week_score = 10
        week_label = "Explosive"
    elif change_7d >= 5:
        week_score = 6
        week_label = "Bullish"
    else:
        week_score = 2
        week_label = "Flat/Weak"
    score += week_score * 0.25
    details["7-Day Momentum"] = f"{change_7d:.2f}% ({week_label})"

    # --- Market Cap Rank ---
    rank = coin_data.get("market_cap_rank", 999)
    if rank <= 10:
        cap_score = 10
        cap_label = "Top 10"
    elif rank <= 50:
        cap_score = 6
        cap_label = "Mid Cap"
    else:
        cap_score = 2
        cap_label = "Small Cap"
    score += cap_score * 0.15
    details["Market Cap Rank"] = f"#{rank} ({cap_label})"

    # --- Developer Activity ---
    stars = developer_data.get("stars", 0)
    forks = developer_data.get("forks", 0)
    contributors = developer_data.get("contributors", 0)
    dev_score = min(stars + forks + contributors, 100) / 10  # scale 0–10
    score += dev_score * 0.15
    details["Developer Activity"] = f"{stars}★ / {forks}F / {contributors}C"

    # --- Community Activity ---
    twitter = community_data.get("twitter_followers", 0)
    reddit = community_data.get("reddit_average_posts_48h", 0)
    comm_score = min((twitter / 50000 + reddit * 2), 10)
    score += comm_score * 0.15
    details["Community Signal"] = f"{twitter:,} followers, {reddit} Reddit posts"

    # --- Sentiment / Volume ---
    sentiment_votes_up = coin_data.get("sentiment_votes_up_percentage", 0)
    volume = market_data.get("total_volume", {}).get("usd", 0)
    vol_score = min(sentiment_votes_up / 10 + (volume / 1e9), 10)
    score += vol_score * 0.2
    details["Sentiment & Volume"] = f"{sentiment_votes_up:.1f}% upvotes, ${volume:,.0f} volume"

    # --- ATH Gap ---
    ath = market_data.get("ath", {}).get("usd", 1)
    current = market_data.get("current_price", {}).get("usd", 1)
    gap_score = 0
    if ath and current:
        gap_pct = 100 * (ath - current) / ath
        if gap_pct <= 30:
            gap_score = 10
        elif gap_pct <= 60:
            gap_score = 5
        else:
            gap_score = 2
        details["ATH Gap"] = f"{gap_pct:.1f}% below ATH"
    score += gap_score * 0.1
        # --- Rebound Potential & Pattern Tag ---
    low_7d = market_data.get("low_7d", current)
    low_30d = market_data.get("low_30d", current)
    high_7d = market_data.get("high_7d", current)

    rebound = 0
    pattern = "Consolidating"

    if low_7d and current:
        rebound_7d = 100 * (current - low_7d) / low_7d
        rebound += rebound_7d
    if low_30d and current:
        rebound_30d = 100 * (current - low_30d) / low_30d
        rebound += rebound_30d

    # Normalize score and assign label
    avg_rebound = rebound / 2
    if avg_rebound > 20:
        rebound_tag = "🚀 Breakout Potential"
        rebound_score = 10
    elif avg_rebound > 10:
        rebound_tag = "📈 Strong Reversal"
        rebound_score = 6
    elif avg_rebound > 5:
        rebound_tag = "🌀 Mild Recovery"
        rebound_score = 3
    else:
        rebound_tag = "⚖️ Consolidating"
        rebound_score = 1

    score += rebound_score * 0.15
    details["Rebound Potential"] = f"{avg_rebound:.2f}% from recent lows — {rebound_tag}"
    
    # Final Grade
    if score >= 8:
        grade = "🔥 Strong Buy"
    elif score >= 5:
        grade = "🧐 Neutral / Watchlist"
    else:
        grade = "⚠️ Risky / Avoid"

    return round(score, 2), grade, details
