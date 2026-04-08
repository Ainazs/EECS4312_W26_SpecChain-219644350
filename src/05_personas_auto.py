"""automated persona generation pipeline"""
import json
import os
import random
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
REVIEWS_PATH   = "data/reviews_clean.jsonl"
GROUPS_OUT     = "data/review_groups_auto.json"
PROMPTS_OUT    = "prompts/prompt_auto.json"
PERSONAS_OUT   = "personas/personas_auto.json"
MODEL          = "meta-llama/llama-4-scout-17b-16e-instruct"
SAMPLE_SIZE    = 300
BATCH_SIZE     = 50
NUM_GROUPS     = 5

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── 1. Load and sample reviews ────────────────────────────────────────────────
reviews = []
with open(REVIEWS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        reviews.append(json.loads(line.strip()))

sampled = random.sample(reviews, min(SAMPLE_SIZE, len(reviews)))
print(f"Loaded {len(reviews)} reviews, sampled {len(sampled)}")

# ── 2. Build review lookup (needed for example_reviews in aggregation) ────────
review_lookup = {}
with open(REVIEWS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line.strip())
        review_lookup[r["review_id"]] = r.get("original_content", r.get("content", ""))

# ── 3. Define grouping prompt ─────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a requirements engineering assistant.
Your job is to read user reviews of a mental health app and assign each review
to exactly one thematic group. The groups must represent distinct user needs or
pain points (e.g., language support, pricing, notifications, privacy, journaling).

You will be given a batch of reviews. For each review, respond with ONLY a JSON
array where each element has:
  - "id": the review ID
  - "group_id": a group identifier like "G1", "G2", ... up to "G5"
  - "group_theme": a short label for that group (e.g., "Language Support")

Use consistent group_ids and group_themes across all batches.
Respond with only the JSON array, no explanation."""

# ── 4. Process reviews in batches ─────────────────────────────────────────────
all_assignments = []

for i in range(0, len(sampled), BATCH_SIZE):
    batch = sampled[i : i + BATCH_SIZE]
    batch_text = "\n".join(
        f'ID: {r["review_id"]} | Review: {r.get("content", "")[:200]}'
        for r in batch
    )

    user_prompt = f"Assign each of the following reviews to one of {NUM_GROUPS} groups:\n\n{batch_text}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        assignments = json.loads(raw)
        all_assignments.extend(assignments)
        print(f"  Batch {i//BATCH_SIZE + 1}: assigned {len(assignments)} reviews")
    except json.JSONDecodeError as e:
        print(f"  WARNING: could not parse batch {i//BATCH_SIZE + 1}: {e}")
        print(f"  Raw response: {raw[:300]}")

# ── 5. Aggregate into groups ──────────────────────────────────────────────────
groups = {}
for a in all_assignments:
    gid   = a.get("group_id", "G_unknown")
    theme = a.get("group_theme", "Unknown")
    rid   = a.get("id")

    if gid not in groups:
        groups[gid] = {"group_id": gid, "theme": theme, "review_ids": [], "example_reviews": []}
    if rid:
        groups[gid]["review_ids"].append(rid)

# Add example_reviews (first 3 original review texts) and cap review_ids at 15
for gid, group in groups.items():
    sample_ids = group["review_ids"][:3]
    group["example_reviews"] = [
        review_lookup.get(rid, "")
        for rid in sample_ids
        if rid in review_lookup
    ]
    group["review_ids"] = group["review_ids"][:15]

output = {"groups": list(groups.values())}

# ── 6. Save review_groups_auto.json ──────────────────────────────────────────
os.makedirs("data", exist_ok=True)
with open(GROUPS_OUT, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved {len(groups)} groups to {GROUPS_OUT}")
for g in output["groups"]:
    print(f"  {g['group_id']} — {g['theme']}: {len(g['review_ids'])} reviews")

# ── 7. Save prompt log ────────────────────────────────────────────────────────
os.makedirs("prompts", exist_ok=True)
prompt_log = {
    "step": "4.1 - Group Reviews Automatically",
    "model": MODEL,
    "system_prompt": SYSTEM_PROMPT,
    "user_prompt_template": f"Assign each of the following reviews to one of {NUM_GROUPS} groups:\n\n[BATCH OF REVIEWS]",
    "parameters": {
        "sample_size": SAMPLE_SIZE,
        "batch_size": BATCH_SIZE,
        "num_groups": NUM_GROUPS,
        "temperature": 0.2
    }
}
with open(PROMPTS_OUT, "w", encoding="utf-8") as f:
    json.dump(prompt_log, f, indent=2)
print(f"Saved prompt log to {PROMPTS_OUT}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4.2 — Generate Personas Automatically
# ══════════════════════════════════════════════════════════════════════════════

PERSONA_SYSTEM_PROMPT = """You are a requirements engineering assistant.
Your job is to create a structured user persona from a group of app reviews.

Given a group theme and a list of review texts, respond with ONLY a JSON object
with these exact fields:
{
  "id": "P_auto_1",
  "name": "Short Persona Name",
  "description": "One sentence describing who this user is.",
  "derived_from_group": "G1",
  "goals": ["goal 1", "goal 2"],
  "pain_points": ["pain point 1", "pain point 2"],
  "context": ["context detail 1", "context detail 2"],
  "constraints": ["constraint 1", "constraint 2"],
  "evidence_reviews": ["rev_1", "rev_2"]
}

Base everything strictly on the reviews provided. Do not invent details.
Respond with only the JSON object, no explanation."""

# Load the groups we just saved
with open(GROUPS_OUT, "r", encoding="utf-8") as f:
    groups_data = json.load(f)

personas = []

for i, group in enumerate(groups_data["groups"]):
    gid     = group["group_id"]
    theme   = group["theme"]
    rev_ids = group["review_ids"][:15]

    review_texts = "\n".join(
        f'- [{rid}]: {review_lookup.get(rid, "")[:150]}'
        for rid in rev_ids
        if rid in review_lookup
    )

    user_prompt = f"""Group ID: {gid}
Group Theme: {theme}
Reviews:
{review_texts}

Create a persona for this group. Use persona ID "P_auto_{i+1}" and reference group "{gid}"."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        persona = json.loads(raw)
        persona["evidence_reviews"] = rev_ids
        personas.append(persona)
        print(f"  Generated persona for {gid} — {theme}: {persona['name']}")
    except json.JSONDecodeError as e:
        print(f"  WARNING: could not parse persona for {gid}: {e}")
        print(f"  Raw: {raw[:300]}")

# ── Save personas_auto.json ───────────────────────────────────────────────────
os.makedirs("personas", exist_ok=True)
with open(PERSONAS_OUT, "w", encoding="utf-8") as f:
    json.dump({"personas": personas}, f, indent=2)

print(f"\nSaved {len(personas)} personas to {PERSONAS_OUT}")