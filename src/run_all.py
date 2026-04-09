"""runs the full pipeline end-to-end"""

import subprocess
import sys

scripts = [
    ("Step 4.1 & 4.2 — Group reviews and generate personas", "src/05_personas_auto.py"),
    ("Step 4.3 — Generate specifications",                   "src/06_spec_generate.py"),
    ("Step 4.4 — Generate validation tests",                 "src/07_tests_generate.py"),
    ("Step 4.5 & 6 — Compute metrics for all pipelines",     "src/08_metrics.py"),
]

print("=" * 60)
print("SpecChain — Automated Pipeline")
print("=" * 60)

for description, script in scripts:
    print(f"\n>> {description}")
    print(f"   Running {script} ...")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"\nERROR: {script} failed with exit code {result.returncode}. Stopping.")
        sys.exit(result.returncode)
    print(f"   Done.")

print("\n" + "=" * 60)
print("All automated pipeline steps completed successfully.")
print("=" * 60)