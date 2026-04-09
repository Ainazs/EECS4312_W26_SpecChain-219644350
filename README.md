# EECS4312_W26_SpecChain

## Application
MindDoc: Mood Tracker & Journal (Google Play Store)

## Dataset
- `data/reviews_raw.jsonl` contains the collected reviews.
- `data/reviews_clean.jsonl` contains the cleaned dataset.
- The original collected dataset contains 4,288 reviews.
- The cleaned dataset contains 4,288 reviews.
- Collection method: Google Play Store scraper.
- Cleaning steps: removed duplicates, empty and short entries, punctuation,
  special characters, and emojis. Lowercased all text, removed stop words,
  and lemmatized all words.

## Repository Structure
- `data/` contains datasets and review groups
- `personas/` contains persona files
- `spec/` contains specifications
- `tests/` contains validation tests
- `metrics/` contains all metric files
- `prompts/` contains LLM prompts used in the automated pipeline
- `src/` contains executable Python scripts
- `reflection/` contains the final reflection

## How to Run
1. `python src/00_validate_repo.py`
2. `python src/02_clean.py`
3. `python src/run_all.py`
4. Open `metrics/metrics_summary.json` for comparison results

## Notes
- Requires a Groq API key set as an environment variable before running the pipeline.
- Windows: `$env:GROQ_API_KEY="your_key_here"`
- Mac/Linux: `export GROQ_API_KEY="your_key_here"`