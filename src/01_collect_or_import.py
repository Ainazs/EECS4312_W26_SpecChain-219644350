"""imports or reads your raw dataset; if you scraped, include scraper here"""
"""
01_collect_or_import.py
Scrapes Google Play Store reviews for MindDoc (de.moodpath.android)
and saves them as data/reviews_raw.jsonl

Requirements:
    pip install google-play-scraper pandas numpy

Usage:
    python src/01_collect_or_import.py
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from google_play_scraper import Sort, reviews

# ── Configuration ──────────────────────────────────────────────
APP_ID = "de.moodpath.android"  # MindDoc package ID
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reviews_raw.jsonl")

# Collect up to 5000 reviews using batched fetching
all_reviews = []
continuation_token = None

while len(all_reviews) < 5000:
    result, continuation_token = reviews(
        APP_ID,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=200,
        continuation_token=continuation_token,
    )
    if not result:
        break
    all_reviews.extend(result)
    print(f"  Fetched {len(all_reviews)} so far...")

# Trim to exactly 5000
all_reviews = all_reviews[:5000]
print(f"\nTotal reviews collected: {len(all_reviews)}")

# ── Combine into DataFrame ────────────────────────────────────
df = pd.DataFrame(np.array(all_reviews), columns=['review'])
df = df.join(pd.DataFrame(df.pop('review').tolist()))

# Remove duplicates based on reviewId
df = df.drop_duplicates(subset=['reviewId'], keep='first')
df = df.reset_index(drop=True)
print(f"Total reviews after dedup: {len(df)}")

# ── Save as JSONL ──────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for i, row in df.iterrows():
        # Convert datetime to string if needed
        review_date = row.get("at", "")
        if isinstance(review_date, datetime):
            review_date = review_date.isoformat()
        else:
            review_date = str(review_date) if review_date else ""

        record = {
            "review_id": f"rev_{i+1}",
            "original_id": str(row.get("reviewId", "")),
            "username": str(row.get("userName", "")),
            "score": int(row.get("score", 0)) if pd.notna(row.get("score")) else 0,
            "content": str(row.get("content", "")),
            "thumbs_up": int(row.get("thumbsUpCount", 0)) if pd.notna(row.get("thumbsUpCount")) else 0,
            "review_date": review_date,
            "reply_content": str(row.get("replyContent", "")) if pd.notna(row.get("replyContent")) else "",
            "app_version": str(row.get("appVersion", "")) if pd.notna(row.get("appVersion")) else "",
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
