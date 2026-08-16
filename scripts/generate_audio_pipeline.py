import os
import re
import json
import base64
import requests
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voice_selector import get_voice_for_source

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise SystemExit("ELEVENLABS_API_KEY not found.")

STORY_FILE = os.environ.get("STORY_FILE")
if not STORY_FILE:
    raise SystemExit("STORY_FILE not set.")

STABILITY = float(os.environ.get("VOICE_STABILITY", "0.0"))

with open(STORY_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
frontmatter_text, story_text = match.groups()

title_match = re.search(r"title:\s*(.+)", frontmatter_text)
title = title_match.group(1).strip() if title_match else "Untitled story"

source_match = re.search(r"source:\s*(.+)", frontmatter_text)
source = source_match.group(1).strip() if source_match else ""

voice_name, voice_id, category = get_voice_for_source(source)
print(f"Story: {title}")
print(f"Source: {source} -> matched category: {category}")
print(f"Selected voice: {voice_name} ({voice_id})")

# --- Apply Devanagari pronunciation substitutions ---
with open("content/pronunciation-map.json", "r", encoding="utf-8") as f:
    pronunciation_map = json.load(f)

narration_text = story_text
for english_name, devanagari in pronunciation_map.items():
    narration_text = re.sub(rf"\b{re.escape(english_name)}\b", devanagari, narration_text)

print(f"Prepared narration text ({len(narration_text)} characters). Sending to ElevenLabs (eleven_v3)...")

# --- Call ElevenLabs ---
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
}
payload = {
    "text": narration_text,
    "model_id": "eleven_v3",
    "language_code": "en",
    "voice_settings": {
        "stability": STABILITY
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    raise SystemExit(f"ElevenLabs API error {response.status_code}: {response.text}")

data = response.json()

slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
output_audio = f"content/audio/{slug}-en.mp3"
output_timestamps = f"content/audio/{slug}-en-timestamps.json"

os.makedirs("content/audio", exist_ok=True)
audio_bytes = base64.b64decode(data["audio_base64"])
with open(output_audio, "wb") as f:
    f.write(audio_bytes)

with open(output_timestamps, "w", encoding="utf-8") as f:
    json.dump(data["alignment"], f, indent=2)

print(f"Audio saved to {output_audio}")
print(f"Timestamps saved to {output_timestamps}")
