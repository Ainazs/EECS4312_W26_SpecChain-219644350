"""computes metrics: coverage/traceability/ambiguity/testability"""
import json
import os
import re

REVIEWS_PATH   = "data/reviews_clean.jsonl"
GROUPS_PATH    = "data/review_groups_auto.json"
PERSONAS_PATH  = "personas/personas_auto.json"
SPEC_PATH      = "spec/spec_auto.md"
TESTS_PATH     = "tests/tests_auto.json"
METRICS_OUT    = "metrics/metrics_auto.json"

dataset_size = 0
with open(REVIEWS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            dataset_size += 1

print(f"Dataset size: {dataset_size}")

with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
    personas_data = json.load(f)
personas = personas_data["personas"]
persona_count = len(personas)
print(f"Persona count: {persona_count}")

with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec_content = f.read()

fr_ids = re.findall(r"# Requirement ID:\s*(FR\d+)", spec_content)
requirements_count = len(fr_ids)
print(f"Requirements count: {requirements_count}")

with open(TESTS_PATH, "r", encoding="utf-8") as f:
    tests_data = json.load(f)
tests_count = len(tests_data["tests"])
print(f"Tests count: {tests_count}")

# Traceability links :
# persona -> review group: 1 per persona
# requirement -> persona: 1 per requirement
# test -> requirement: 1 per test
with open(GROUPS_PATH, "r", encoding="utf-8") as f:
    groups_data = json.load(f)

persona_to_group = persona_count
req_to_persona   = requirements_count
test_to_req      = tests_count
traceability_links = persona_to_group + req_to_persona + test_to_req
print(f"Traceability links: {traceability_links} ({persona_to_group} persona->group + {req_to_persona} req->persona + {test_to_req} test->req)")

covered_reviews = set()
for group in groups_data["groups"]:
    for rid in group.get("review_ids", []):
        covered_reviews.add(rid)

review_coverage = round(len(covered_reviews) / dataset_size, 4)
print(f"Review coverage: {len(covered_reviews)}/{dataset_size} = {review_coverage}")

# Count how many requirements have both a Source Persona and Traceability line
traceable = len(re.findall(r"- Source Persona:", spec_content))
traceability_ratio = round(traceable / requirements_count, 4) if requirements_count else 0
print(f"Traceability ratio: {traceable}/{requirements_count} = {traceability_ratio}")

tested_req_ids = set(t["requirement_id"] for t in tests_data["tests"])
testability_rate = round(len(tested_req_ids) / requirements_count, 4) if requirements_count else 0
print(f"Testability rate: {len(tested_req_ids)}/{requirements_count} = {testability_rate}")

ambiguous_terms = [
    r'\bfast\b', r'\bquickly\b', r'\bsoon\b', r'\beasy\b', r'\beasily\b',
    r'\bbetter\b', r'\buser.friendly\b', r'\bsimple\b', r'\bsimply\b',
    r'\bsmooth\b', r'\bappropriate\b', r'\befficient\b', r'\befficiently\b',
    r'\bconvenient\b', r'\bseamless\b', r'\bseamlessly\b', r'\bimproved\b',
    r'\bnice\b', r'\bgood\b', r'\bshould be\b', r'\beasier\b', r'\bfaster\b'
]

blocks = re.split(r"(?=# Requirement ID:)", spec_content)
req_blocks = [b for b in blocks if b.strip().startswith("# Requirement ID:")]

ambiguous_count = 0
for block in req_blocks:
    block_lower = block.lower()
    if any(re.search(term, block_lower) for term in ambiguous_terms):
        ambiguous_count += 1

ambiguity_ratio = round(ambiguous_count / requirements_count, 4) if requirements_count else 0
print(f"Ambiguity ratio: {ambiguous_count}/{requirements_count} = {ambiguity_ratio}")

metrics = {
    "pipeline": "automated",
    "dataset_size": dataset_size,
    "persona_count": persona_count,
    "requirements_count": requirements_count,
    "tests_count": tests_count,
    "traceability_links": traceability_links,
    "review_coverage": review_coverage,
    "traceability_ratio": traceability_ratio,
    "testability_rate": testability_rate,
    "ambiguity_ratio": ambiguity_ratio
}

os.makedirs("metrics", exist_ok=True)
with open(METRICS_OUT, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\nSaved metrics to {METRICS_OUT}")
print(json.dumps(metrics, indent=2))


# HYBRID METRICS
HYBRID_GROUPS_PATH   = "data/review_groups_hybrid.json"
HYBRID_PERSONAS_PATH = "personas/personas_hybrid.json"
HYBRID_SPEC_PATH     = "spec/spec_hybrid.md"
HYBRID_TESTS_PATH    = "tests/tests_hybrid.json"
HYBRID_METRICS_OUT   = "metrics/metrics_hybrid.json"

# 1. Dataset size (same dataset)
print("\n--- Hybrid Metrics ---")
print(f"Dataset size: {dataset_size}")

# 2. Persona count
with open(HYBRID_PERSONAS_PATH, "r", encoding="utf-8") as f:
    hybrid_personas = json.load(f)["personas"]
hybrid_persona_count = len(hybrid_personas)
print(f"Persona count: {hybrid_persona_count}")

# 3. Requirements count
with open(HYBRID_SPEC_PATH, "r", encoding="utf-8") as f:
    hybrid_spec = f.read()
hybrid_fr_ids = re.findall(r"# Requirement ID:\s*(FR_hybrid_\d+)", hybrid_spec)
hybrid_req_count = len(hybrid_fr_ids)
print(f"Requirements count: {hybrid_req_count}")

# 4. Tests count
with open(HYBRID_TESTS_PATH, "r", encoding="utf-8") as f:
    hybrid_tests = json.load(f)["tests"]
hybrid_tests_count = len(hybrid_tests)
print(f"Tests count: {hybrid_tests_count}")

# 5. Traceability links
hybrid_persona_to_group = hybrid_persona_count
hybrid_req_to_persona   = hybrid_req_count
hybrid_test_to_req      = hybrid_tests_count
hybrid_traceability_links = hybrid_persona_to_group + hybrid_req_to_persona + hybrid_test_to_req
print(f"Traceability links: {hybrid_traceability_links}")

# 6. Review coverage ratio
with open(HYBRID_GROUPS_PATH, "r", encoding="utf-8") as f:
    hybrid_groups = json.load(f)["groups"]
hybrid_covered = set()
for group in hybrid_groups:
    for rid in group.get("review_ids", []):
        hybrid_covered.add(rid)
hybrid_coverage = round(len(hybrid_covered) / dataset_size, 4)
print(f"Review coverage: {len(hybrid_covered)}/{dataset_size} = {hybrid_coverage}")

# 7. Traceability ratio
hybrid_traceable = len(re.findall(r"- Source Persona:", hybrid_spec))
hybrid_traceability_ratio = round(hybrid_traceable / hybrid_req_count, 4) if hybrid_req_count else 0
print(f"Traceability ratio: {hybrid_traceable}/{hybrid_req_count} = {hybrid_traceability_ratio}")

# 8. Testability rate
hybrid_tested_ids = set(t["requirement_id"] for t in hybrid_tests)
hybrid_testability_rate = round(len(hybrid_tested_ids) / hybrid_req_count, 4) if hybrid_req_count else 0
print(f"Testability rate: {len(hybrid_tested_ids)}/{hybrid_req_count} = {hybrid_testability_rate}")

# 9. Ambiguity ratio
hybrid_blocks = re.split(r"(?=# Requirement ID:)", hybrid_spec)
hybrid_req_blocks = [b for b in hybrid_blocks if b.strip().startswith("# Requirement ID:")]
hybrid_ambiguous_count = 0
for block in hybrid_req_blocks:
    block_lower = block.lower()
    if any(re.search(term, block_lower) for term in ambiguous_terms):
        hybrid_ambiguous_count += 1
hybrid_ambiguity_ratio = round(hybrid_ambiguous_count / hybrid_req_count, 4) if hybrid_req_count else 0
print(f"Ambiguity ratio: {hybrid_ambiguous_count}/{hybrid_req_count} = {hybrid_ambiguity_ratio}")

# Save
hybrid_metrics = {
    "pipeline": "hybrid",
    "dataset_size": dataset_size,
    "persona_count": hybrid_persona_count,
    "requirements_count": hybrid_req_count,
    "tests_count": hybrid_tests_count,
    "traceability_links": hybrid_traceability_links,
    "review_coverage": hybrid_coverage,
    "traceability_ratio": hybrid_traceability_ratio,
    "testability_rate": hybrid_testability_rate,
    "ambiguity_ratio": hybrid_ambiguity_ratio
}

with open(HYBRID_METRICS_OUT, "w", encoding="utf-8") as f:
    json.dump(hybrid_metrics, f, indent=2)

print(f"\nSaved hybrid metrics to {HYBRID_METRICS_OUT}")
print(json.dumps(hybrid_metrics, indent=2))