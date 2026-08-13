import os
import re
import json
import requests

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY not found. Is the Codespaces secret set and did you restart the Codespace?")

# --- Story parameters, read from environment variables ---
# (When run locally, set these yourself before running the script;
#  when run via GitHub Actions, these come from the workflow_dispatch inputs.)
THEME = os.environ.get("STORY_THEME", "Ganesha and the broken tusk")
WORD_COUNT = int(os.environ.get("STORY_WORD_COUNT", "600"))
CONTEXT = os.environ.get("STORY_CONTEXT", "Focus on quick thinking and resourcefulness when something goes wrong. End with a lesson about turning a setback into a strength.")
AGE_RANGE = os.environ.get("STORY_AGE_RANGE", "6-10 years")
SOURCE_EPIC = os.environ.get("STORY_SOURCE_EPIC", "Puranas")
TEMPERATURE = 0.8

# NOTE: verify this model name is current before running -
# check platform.openai.com/docs/models for OpenAI's latest recommended
# general-purpose model at the time you're reading this.
MODEL = "gpt-4o"

SYSTEM_PROMPT = """You write short, self-contained children's stories adapted from Indian
epics and mythology, in the style of a warm, expressive read-aloud story.

Requirements:
- The story must be understandable to someone with zero prior knowledge of
  the epic or its context - establish who's who and why the story is
  happening in the first 2-3 sentences.
- Written for a reader aged {age_range} - match vocabulary, sentence length,
  and emotional intensity appropriately for this age.
- Simple, clear English suitable for a child, but with genuine emotional
  range - moments of doubt, tension, warmth, and triumph.
- End with a short, separated closing reflection connecting the story to a
  real-life lesson a reader could apply.
- No violence, frightening imagery, or content unsuitable for young children.
- Roughly {word_count} words.
"""

USER_PROMPT = f"""Write a children's story based on: {THEME}

Source: {SOURCE_EPIC}
Additional context: {CONTEXT}
"""

url = "https://api.openai.com/v1/responses"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": MODEL,
    "temperature": TEMPERATURE,
    "input": [
        {"role": "system", "content": SYSTEM_PROMPT.format(word_count=WORD_COUNT, age_range=AGE_RANGE)},
        {"role": "user", "content": USER_PROMPT},
    ],
}

print(f"Requesting story draft from OpenAI ({MODEL})...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    raise SystemExit(f"OpenAI API error {response.status_code}: {response.text}")

data = response.json()

# Extract the generated text - walking the response structure defensively
# since the exact shape can vary by API version.
story_text = ""
for item in data.get("output", []):
    if item.get("type") == "message":
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                story_text += content.get("text", "")

if not story_text:
    print("Could not find story text in expected location. Full response:")
    print(json.dumps(data, indent=2))
    raise SystemExit("See raw response above to debug the response structure.")

slug = re.sub(r"[^a-z0-9]+", "-", THEME.lower()).strip("-")
os.makedirs("content/drafts", exist_ok=True)
output_path = f"content/drafts/{slug}.md"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"---\ntitle: {THEME}\nsource: {SOURCE_EPIC}\nage_range: {AGE_RANGE}\nstatus: draft\n---\n\n{story_text}")

print(f"Draft saved to {output_path}")
print("Review this before it goes any further in the pipeline.")
