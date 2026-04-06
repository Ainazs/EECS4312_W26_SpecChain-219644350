"""cleans raw data & make clean dataset"""
"""
02_clean.py
Cleans raw MindDoc reviews and saves to data/reviews_clean.jsonl

Cleaning steps (per project requirements):
  1. Remove duplicates
  2. Remove empty entries
  3. Remove extremely short reviews
  4. Remove punctuation
  5. Remove special characters and emojis
  6. Convert numbers to text
  7. Remove extra whitespace
  8. Convert all words to lowercase
  9. Remove stop words
  10. Lemmatize the reviews

Requirements:
    pip install nltk num2words

Usage:
    python src/02_clean.py
"""

import json
import os
import re
import nltk
from num2words import num2words

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Configuration ──────────────────────────────────────────────
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reviews_raw.jsonl")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reviews_clean.jsonl")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_metadata.json")

MIN_WORD_COUNT = 3  # minimum words after cleaning to keep a review

# ── Setup NLP tools ────────────────────────────────────────────
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def remove_emojis(text):
    """Remove emojis and special unicode characters."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001f926-\U0001f937"  # supplemental
        "\U00010000-\U0010ffff"  # supplementary
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def convert_numbers_to_text(text):
    """Convert standalone numbers to their word equivalents."""
    def replace_number(match):
        num = match.group()
        try:
            # Only convert reasonable numbers (avoid huge numbers)
            n = float(num)
            if abs(n) > 999999:
                return num
            if n == int(n):
                return num2words(int(n))
            else:
                return num2words(n)
        except (ValueError, OverflowError):
            return num
    return re.sub(r'\b\d+\.?\d*\b', replace_number, text)


def clean_review(text):
    """Apply all cleaning steps to a single review."""
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove emojis and special characters
    text = remove_emojis(text)

    # Step 3: Convert numbers to text (before removing punctuation)
    text = convert_numbers_to_text(text)

    # Step 4: Remove punctuation and special characters (keep letters and spaces)
    text = re.sub(r'[^a-z\s]', '', text)

    # Step 5: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 6: Tokenize, remove stop words, and lemmatize
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

    return " ".join(words)


# ── Load raw reviews ───────────────────────────────────────────
print("Loading raw reviews...")
raw_reviews = []
with open(RAW_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            raw_reviews.append(json.loads(line))

print(f"Raw reviews loaded: {len(raw_reviews)}")

# ── Remove duplicates by content ──────────────────────────────
seen_content = set()
unique_reviews = []
for r in raw_reviews:
    content = r.get("content", "").strip()
    if content and content not in seen_content:
        seen_content.add(content)
        unique_reviews.append(r)

print(f"After removing duplicates: {len(unique_reviews)}")

# ── Remove empty entries ──────────────────────────────────────
non_empty = [r for r in unique_reviews if r.get("content", "").strip()]
print(f"After removing empty reviews: {len(non_empty)}")

# ── Clean and filter ──────────────────────────────────────────
print("Cleaning reviews...")
clean_reviews = []
removed_short = 0

for r in non_empty:
    cleaned_text = clean_review(r.get("content", ""))

    # Remove extremely short reviews (fewer than MIN_WORD_COUNT words after cleaning)
    if len(cleaned_text.split()) < MIN_WORD_COUNT:
        removed_short += 1
        continue

    clean_record = {
        "review_id": r["review_id"],
        "original_id": r.get("original_id", ""),
        "score": r.get("score", 0),
        "content": cleaned_text,
        "original_content": r.get("content", ""),
        "review_date": r.get("review_date", ""),
    }
    clean_reviews.append(clean_record)

print(f"Removed {removed_short} extremely short reviews")
print(f"Final cleaned dataset: {len(clean_reviews)} reviews")

# ── Reassign sequential review IDs ────────────────────────────
for i, r in enumerate(clean_reviews):
    r["review_id"] = f"rev_{i+1}"

# ── Save cleaned reviews ──────────────────────────────────────
os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)

with open(CLEAN_PATH, "w", encoding="utf-8") as f:
    for r in clean_reviews:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Saved cleaned reviews to {CLEAN_PATH}")

# ── Save metadata ─────────────────────────────────────────────
metadata = {
    "app_name": "MindDoc: Mental Health Support",
    "app_id": "de.moodpath.android",
    "platform": "Google Play Store",
    "raw_review_count": len(raw_reviews),
    "unique_review_count": len(unique_reviews),
    "cleaned_review_count": len(clean_reviews),
    "collection_method": "google-play-scraper library (reviews_all), scraped from US, CA, GB regions",
    "cleaning_steps": [
        "Removed duplicate reviews by content",
        "Removed empty entries",
        "Converted to lowercase",
        "Removed emojis and special unicode characters",
        "Converted numbers to text using num2words",
        "Removed punctuation and special characters",
        "Removed extra whitespace",
        "Removed English stop words (NLTK)",
        "Lemmatized words (WordNet lemmatizer)",
        "Removed reviews with fewer than 3 words after cleaning"
    ],
    "min_word_count_threshold": MIN_WORD_COUNT,
}

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"Saved metadata to {METADATA_PATH}")
print("\nDone!")