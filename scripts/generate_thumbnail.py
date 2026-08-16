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
    "A cinematic, highly realistic depiction of Indian mythology, "
    "designed for a premium children's mythology story experience. The "
    "image should look like a frame from a large-scale, high-budget "
    "Indian mythological fantasy film rather than a painting or "
    "traditional illustration. Photorealistic cinematic rendering, "
    "realistic human anatomy and proportions, lifelike skin, realistic "
    "facial features, natural hair and fabric textures, physically "
    "believable lighting, detailed environments, realistic atmospheric "
    "depth, volumetric light, natural shadows, subtle depth of field, "
    "high dynamic range, rich but natural colors, realistic materials "
    "and textures. Characters should feel physically present and "
    "believable while retaining their divine and mythological identity. "
    "Expressions should be emotionally clear and appropriate to the "
    "story. Use dramatic cinematic composition and lighting to "
    "communicate the story visually. Epic environments should have a "
    "strong sense of scale and depth. The image should feel immersive, "
    "majestic, beautiful, and awe-inspiring. The overall mood should "
    "remain suitable for children: wondrous, heroic, reverent, magical, "
    "and emotionally uplifting. Avoid horror, gore, grotesque imagery, "
    "excessive darkness, frightening faces, or disturbing violence. "
    "IMPORTANT: Prioritize realistic cinematic visuals over an "
    "illustrated or painterly appearance. Do NOT make the image look "
    "like a watercolor painting, oil painting, digital painting, "
    "children's book painting, cartoon, animation, concept sketch, or "
    "flat illustration. No text, no captions, no borders, no decorative "
    "frame. Wide landscape composition, cinematic 16:9 framing."
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
