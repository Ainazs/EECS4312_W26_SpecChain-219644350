"""checks required files/folders exist"""
import os

required_files = [
    # Task 2
    "data/reviews_clean.jsonl",
    "data/dataset_metadata.json",

    # Task 3 - Manual pipeline
    "data/review_groups_manual.json",
    "personas/personas_manual.json",
    "spec/spec_manual.md",
    "tests/tests_manual.json",
    "metrics/metrics_manual.json",

    # Task 4 - Automated pipeline
    "data/review_groups_auto.json",
    "personas/personas_auto.json",
    "spec/spec_auto.md",
    "tests/tests_auto.json",
    "metrics/metrics_auto.json",
    "prompts/prompt_auto.json",

    # Task 5 - Hybrid pipeline
    "data/review_groups_hybrid.json",
    "personas/personas_hybrid.json",
    "spec/spec_hybrid.md",
    "tests/tests_hybrid.json",
    "metrics/metrics_hybrid.json",

    # Task 6 - Summary
    "metrics/metrics_summary.json",

    # Task 7 - Scripts
    "src/00_validate_repo.py",
    "src/05_personas_auto.py",
    "src/06_spec_generate.py",
    "src/07_tests_generate.py",
    "src/08_metrics.py",
    "src/run_all.py",

    # Reflection
    "reflection/reflection.md",
]

print("Checking repository structure...")
print()

all_found = True
for filepath in required_files:
    if os.path.exists(filepath):
        print(f"  [FOUND]   {filepath}")
    else:
        print(f"  [MISSING] {filepath}")
        all_found = False

print()
if all_found:
    print("Repository validation complete — all files present.")
else:
    print("Repository validation complete — some files are MISSING. See above.")