import re
import json

TAGGED_TEXT_FILE = "content/audio/hanuman-leap-of-faith-en-tagged.txt"
PRONUNCIATION_MAP_FILE = "content/pronunciation-map.json"
OUTPUT_FILE = "content/audio/hanuman-leap-of-faith-en-final-text.txt"

with open(TAGGED_TEXT_FILE, "r", encoding="utf-8") as f:
    text = f.read().strip()

with open(PRONUNCIATION_MAP_FILE, "r", encoding="utf-8") as f:
    pronunciation_map = json.load(f)

for english_name, devanagari in pronunciation_map.items():
    text = re.sub(rf"\b{re.escape(english_name)}\b", devanagari, text)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Reconstructed final text saved to {OUTPUT_FILE}")
print("This should exactly match what was sent to ElevenLabs for the current audio file.")