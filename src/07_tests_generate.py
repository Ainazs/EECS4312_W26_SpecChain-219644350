"""generates tests from specs"""
import json
import os
import re
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
SPEC_PATH  = "spec/spec_auto.md"
TESTS_OUT  = "tests/tests_auto.json"
MODEL      = "meta-llama/llama-4-scout-17b-16e-instruct"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Parse requirements from spec_auto.md ──────────────────────────────────────
with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec_content = f.read()

# Split on requirement headers
raw_blocks = re.split(r"(?=# Requirement ID:)", spec_content)
requirements = []

for block in raw_blocks:
    block = block.strip()
    if not block.startswith("# Requirement ID:"):
        continue

    # Extract FR id
    fr_match = re.search(r"# Requirement ID:\s*(FR\d+)", block)
    # Extract description
    desc_match = re.search(r"-\s*Description:\s*\[?(.+?)\]?\n", block)
    # Extract acceptance criteria
    ac_match = re.search(r"-\s*Acceptance Criteria:\s*\[?(.+?)\]?\s*$", block, re.DOTALL)

    if fr_match and desc_match:
        requirements.append({
            "fr_id": fr_match.group(1),
            "description": desc_match.group(1).strip(),
            "acceptance": ac_match.group(1).strip() if ac_match else ""
        })

print(f"Parsed {len(requirements)} requirements from spec_auto.md")

# ── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a software testing assistant.
Given a requirement ID, description, and acceptance criteria, generate exactly 2
test scenarios as a JSON array with this structure:

[
  {
    "test_id": "T_auto_1",
    "requirement_id": "FR1",
    "scenario": "Short scenario title",
    "steps": [
      "Step 1",
      "Step 2",
      "Step 3"
    ],
    "expected_result": "What should happen if the requirement is met."
  },
  {
    "test_id": "T_auto_2",
    "requirement_id": "FR1",
    "scenario": "Short scenario title for negative or edge case",
    "steps": [
      "Step 1",
      "Step 2"
    ],
    "expected_result": "What should happen."
  }
]

Rules:
- test_id must follow the pattern T_auto_N
- requirement_id must match the FR id given
- steps must be clear and executable
- One test should be a happy path, one should be an edge case or failure case
- Respond with only the JSON array, no explanation"""

# ── Generate 2 tests per requirement ─────────────────────────────────────────
all_tests = []
test_counter = 1

for req in requirements:
    user_prompt = f"""Requirement ID: {req['fr_id']}
Description: {req['description']}
Acceptance Criteria: {req['acceptance']}

Generate 2 test scenarios with test_ids T_auto_{test_counter} and T_auto_{test_counter + 1}."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        tests = json.loads(raw)
        all_tests.extend(tests)
        print(f"  Generated 2 tests for {req['fr_id']} (T_auto_{test_counter}, T_auto_{test_counter+1})")
        test_counter += 2
    except json.JSONDecodeError as e:
        print(f"  WARNING: could not parse tests for {req['fr_id']}: {e}")
        print(f"  Raw: {raw[:300]}")

# ── Save tests_auto.json ──────────────────────────────────────────────────────
os.makedirs("tests", exist_ok=True)
with open(TESTS_OUT, "w", encoding="utf-8") as f:
    json.dump({"tests": all_tests}, f, indent=2)

print(f"\nSaved {len(all_tests)} test scenarios to {TESTS_OUT}")