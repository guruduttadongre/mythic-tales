import os
import re
import json
import glob
import requests

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY not found.")

MODEL = "gpt-4o"

# --- Determine which draft to process ---
# In automation, the workflow tells us exactly which file changed.
# For local testing, fall back to scanning the folder - but refuse to
# guess if it's ambiguous.
explicit_path = os.environ.get("DRAFT_FILE")

if explicit_path:
    draft_path = explicit_path
    print(f"Using explicitly specified draft: {draft_path}")
else:
    draft_files = glob.glob("content/drafts/*.md")
    if not draft_files:
        raise SystemExit("No draft files found in content/drafts/")
    if len(draft_files) > 1:
        raise SystemExit(
            f"Multiple drafts found: {draft_files}. Refusing to guess - "
            f"set DRAFT_FILE explicitly, or remove the extra file(s)."
        )
    draft_path = draft_files[0]
print(f"Processing: {draft_path}")

with open(draft_path, "r", encoding="utf-8") as f:
    raw = f.read()

# Split frontmatter from story text
match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
if not match:
    raise SystemExit("Could not parse frontmatter from draft file.")
frontmatter_text, story_text = match.groups()

# --- Load existing pronunciation map, so known names aren't re-proposed ---
with open("content/pronunciation-map.json", "r", encoding="utf-8") as f:
    known_names = json.load(f)

# --- Build the prompt ---
SYSTEM_PROMPT = """You prepare children's story text for expressive AI narration.

Task 1 - Add audio tags: Insert bracketed emotion/delivery cues like
[nervous], [determined], [gentle], [triumphant], [playful] at genuinely
significant emotional moments in the story. Use them sparingly - only at
real shifts, not every sentence. Do not change any of the story's actual
words.

Task 2 - Identify names needing pronunciation help: List any proper nouns
(character names, place names) in the story that are Sanskrit/Hindi-origin
and would benefit from a Devanagari spelling to guide correct pronunciation
by an English-speaking AI voice. Do NOT include names already in this
known list: {known_names}

Respond ONLY with valid JSON in this exact structure, nothing else:
{{
  "tagged_text": "the full story with audio tags inserted",
  "proposed_names": {{"EnglishName": "Devanagari spelling", ...}}
}}
"""

url = "https://api.openai.com/v1/responses"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": MODEL,
    "input": [
        {"role": "system", "content": SYSTEM_PROMPT.format(known_names=json.dumps(known_names, ensure_ascii=False))},
        {"role": "user", "content": story_text},
    ],
}

print("Requesting tagging + transliteration from OpenAI...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    raise SystemExit(f"OpenAI API error {response.status_code}: {response.text}")

data = response.json()

result_text = ""
for item in data.get("output", []):
    if item.get("type") == "message":
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                result_text += content.get("text", "")

if not result_text:
    print("No output text found. Full response:")
    print(json.dumps(data, indent=2))
    raise SystemExit("See raw response above to debug.")

# Strip markdown code fences if the model wrapped the JSON in them
cleaned = re.sub(r"^```json\s*|\s*```$", "", result_text.strip())

try:
    result = json.loads(cleaned)
except json.JSONDecodeError:
    print("Could not parse JSON from model output. Raw output:")
    print(result_text)
    raise SystemExit("See raw output above to debug.")

tagged_text = result["tagged_text"]
proposed_names = result.get("proposed_names", {})

# --- Save the tagged version, promoting it out of drafts/ into content/ ---
slug = os.path.basename(draft_path).replace(".md", "")
final_path = f"content/{slug}.md"

with open(final_path, "w", encoding="utf-8") as f:
    f.write(f"---\n{frontmatter_text}\nstatus: tagged\n---\n\n{tagged_text}")

os.remove(draft_path)
print(f"Tagged story saved to {final_path}, removed from drafts.")

# --- Save proposed names separately for the PR body, NOT merged into the map ---
with open("content/proposed-pronunciations.json", "w", encoding="utf-8") as f:
    json.dump(proposed_names, f, indent=2, ensure_ascii=False)

if proposed_names:
    print(f"Proposed {len(proposed_names)} new name(s) for pronunciation-map.json - review before adding manually.")
else:
    print("No new names proposed - all names already known.")