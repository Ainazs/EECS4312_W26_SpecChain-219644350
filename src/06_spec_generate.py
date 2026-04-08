"""generates structured specs from personas"""
import json
import os
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
PERSONAS_PATH = "personas/personas_auto.json"
SPEC_OUT      = "spec/spec_auto.md"
MODEL         = "meta-llama/llama-4-scout-17b-16e-instruct"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Load personas ─────────────────────────────────────────────────────────────
with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
    personas = json.load(f)["personas"]

print(f"Loaded {len(personas)} personas")

# ── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a requirements engineering assistant.
Given a user persona, generate exactly 2 software requirements in this markdown format:

# Requirement ID: FR{N}

- Description: [The system shall ...]
- Source Persona: [Persona name and ID]
- Traceability: [Derived from review group GX]
- Acceptance Criteria: [Given ... When ... Then ...]

# Requirement ID: FR{N+1}

- Description: [The system shall ...]
- Source Persona: [Persona name and ID]
- Traceability: [Derived from review group GX]
- Acceptance Criteria: [Given ... When ... Then ...]

Rules:
- Always start descriptions with "The system shall"
- Acceptance criteria must use Given/When/Then format
- Be specific and measurable, avoid vague terms like fast, easy, better
- Base requirements strictly on the persona provided
- Respond with only the markdown, no explanation"""

# ── Generate requirements per persona ─────────────────────────────────────────
all_requirements = []
fr_counter = 1

for persona in personas:
    user_prompt = f"""Persona ID: {persona['id']}
Persona Name: {persona['name']}
Description: {persona['description']}
Goals: {json.dumps(persona['goals'])}
Pain Points: {json.dumps(persona['pain_points'])}
Context: {json.dumps(persona['context'])}
Constraints: {json.dumps(persona['constraints'])}
Derived from group: {persona['derived_from_group']}

Generate 2 requirements starting from FR{fr_counter}."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    all_requirements.append(raw)
    print(f"  Generated 2 requirements for {persona['id']} — {persona['name']} (FR{fr_counter}, FR{fr_counter+1})")
    fr_counter += 2

# ── Write spec_auto.md ────────────────────────────────────────────────────────
os.makedirs("spec", exist_ok=True)
with open(SPEC_OUT, "w", encoding="utf-8") as f:
    f.write("# Automated Specification\n")
    f.write("# Application: MindDoc\n")
    f.write("# Pipeline: Automated\n\n")
    f.write("---\n\n")
    f.write("\n\n---\n\n".join(all_requirements))

print(f"\nSaved {fr_counter - 1} requirements to {SPEC_OUT}")