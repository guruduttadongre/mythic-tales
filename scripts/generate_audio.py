import os
import re
import json
import base64
import requests

# --- Configuration ---
VOICE_ID = "KlhjbO6ojVZPbMdaYohO"  # Shardul
TAGGED_TEXT_FILE = "content/audio/hanuman-leap-of-faith-en-tagged.txt"
PRONUNCIATION_MAP_FILE = "content/pronunciation-map.json"
OUTPUT_AUDIO = "content/audio/hanuman-leap-of-faith-en.mp3"
OUTPUT_TIMESTAMPS = "content/audio/hanuman-leap-of-faith-en-timestamps.json"

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise SystemExit("ELEVENLABS_API_KEY not found. Is the Codespaces secret set and did you restart the Codespace?")

# --- Step 1: Load the tagged narration text ---
with open(TAGGED_TEXT_FILE, "r", encoding="utf-8") as f:
    text = f.read().strip()

# --- Step 2: Apply Devanagari pronunciation substitutions ---
with open(PRONUNCIATION_MAP_FILE, "r", encoding="utf-8") as f:
    pronunciation_map = json.load(f)

for english_name, devanagari in pronunciation_map.items():
    text = re.sub(rf"\b{re.escape(english_name)}\b", devanagari, text)

print(f"Prepared narration text ({len(text)} characters). Sending to ElevenLabs (eleven_v3)...")

# --- Step 3: Call ElevenLabs with eleven_v3 and timestamps ---
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
}

payload = {
    "text": text,
    "model_id": "eleven_v3",
    "language_code": "en",
    "voice_settings": {
        "stability": 0.0  # "Creative" setting - full emotional expression
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    raise SystemExit(f"ElevenLabs API error {response.status_code}: {response.text}")

data = response.json()

# --- Step 4: Save the audio ---
os.makedirs(os.path.dirname(OUTPUT_AUDIO), exist_ok=True)
audio_bytes = base64.b64decode(data["audio_base64"])
with open(OUTPUT_AUDIO, "wb") as f:
    f.write(audio_bytes)

# --- Step 5: Save the timestamp data ---
with open(OUTPUT_TIMESTAMPS, "w", encoding="utf-8") as f:
    json.dump(data["alignment"], f, indent=2)

print(f"Done. Audio saved to {OUTPUT_AUDIO}")
print(f"Timestamps saved to {OUTPUT_TIMESTAMPS}")