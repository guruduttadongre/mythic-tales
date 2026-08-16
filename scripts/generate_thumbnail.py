import os
import re
import base64
import requests

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY not found.")

STORY_FILE = os.environ.get("STORY_FILE")
if not STORY_FILE:
    raise SystemExit("STORY_FILE not set.")

MODEL = "gpt-image-1"

with open(STORY_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
frontmatter_text, story_text = match.groups()

title_match = re.search(r"title:\s*(.+)", frontmatter_text)
title = title_match.group(1).strip() if title_match else "Untitled story"

VISUAL_OVERRIDE = os.environ.get("VISUAL_OVERRIDE", "").strip()

STYLE_GUIDE = (
    "A richly detailed children's story illustration rendered in "
    "a cinematic style with full, natural, vibrant colors - not flat, "
    "not cartoonish, not monochrome. Soft, cinematic lighting with warm "
    "ambient tones. Characters have realistic proportions and expressive "
    "detail. Detailed, atmospheric backgrounds with genuine depth and "
    "texture (foliage, water, environmental storytelling elements as "
    "relevant to the scene). Clear focal point with a strong sense of "
    "atmosphere and wonder. No text in the image. Wide landscape "
    "composition."
)

story_for_image = re.sub(r"\[.*?\]", "", story_text).strip()

if VISUAL_OVERRIDE:
    print(f"Using visual override: {VISUAL_OVERRIDE}")
    prompt = f"""A children's story illustration for: "{title}"

Specific guidance: {VISUAL_OVERRIDE}

Style: {STYLE_GUIDE}
"""
else:
    prompt = f"""A children's story illustration for: "{title}"

Full story for context - choose the most visually interesting and dynamic moment to depict, not necessarily the opening: {story_for_image}

Style: {STYLE_GUIDE}
"""

url = "https://api.openai.com/v1/images/generations"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": MODEL,
    "prompt": prompt,
    "size": "1536x1024",
    "quality": "medium",
}

print(f"Requesting thumbnail image for: {title}")
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    raise SystemExit(f"OpenAI API error {response.status_code}: {response.text}")

data = response.json()
image_b64 = data["data"][0]["b64_json"]
image_bytes = base64.b64decode(image_b64)

slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
output_path = f"site/images/{slug}-card.png"

os.makedirs("site/images", exist_ok=True)
with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"Thumbnail saved to {output_path}")
