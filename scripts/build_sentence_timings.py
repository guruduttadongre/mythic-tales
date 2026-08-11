import re
import json

FINAL_TEXT_FILE = "content/audio/hanuman-leap-of-faith-en-final-text.txt"
TIMESTAMPS_FILE = "content/audio/hanuman-leap-of-faith-en-timestamps.json"
DISPLAY_STORY_FILE = "content/hanuman-leap-of-faith.md"
OUTPUT_FILE = "content/audio/hanuman-leap-of-faith-en-sentences.json"

def split_into_sentences(text):
    # Split on sentence-ending punctuation followed by a space or newline
    # Keeps it simple: treats ., !, ? as sentence enders
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\u0900-\u097F\[])', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def strip_tags(text):
    # Remove [audio tags] like [nervous], [determined] etc.
    return re.sub(r'\[.*?\]', '', text).strip()

with open(FINAL_TEXT_FILE, "r", encoding="utf-8") as f:
    final_text = f.read().strip()

with open(TIMESTAMPS_FILE, "r", encoding="utf-8") as f:
    alignment = json.load(f)

characters = alignment["characters"]
start_times = alignment["character_start_times_seconds"]

with open(DISPLAY_STORY_FILE, "r", encoding="utf-8") as f:
    raw_display = f.read()
display_text = re.sub(r"^---.*?---\s*", "", raw_display, flags=re.DOTALL).strip()

# Strip markdown formatting artifacts that don't exist in the tagged/final text,
# so both texts split into sentences the same way
display_text = display_text.replace("---", " ")
display_text = display_text.replace("*", "")
display_text = re.sub(r"\s+", " ", display_text).strip()

final_sentences = split_into_sentences(final_text)
display_sentences = split_into_sentences(display_text)

if len(final_sentences) != len(display_sentences):
    print(f"WARNING: sentence count mismatch - final text has {len(final_sentences)}, "
          f"display text has {len(display_sentences)}. Review before using this output.")

# Find the starting character index of each sentence within the full final_text
result = []
search_pos = 0
for i, sentence in enumerate(final_sentences):
    idx = final_text.find(sentence, search_pos)
    if idx == -1:
        print(f"WARNING: could not locate sentence {i} in final text, skipping timing for it.")
        continue
    search_pos = idx + len(sentence)

    # Find first non-tag character's timestamp at or after idx
    start_time = None
    for char_idx in range(idx, min(idx + len(sentence), len(characters))):
        start_time = start_times[char_idx]
        break

    display_sentence = display_sentences[i] if i < len(display_sentences) else strip_tags(sentence)

    result.append({
        "text": display_sentence,
        "start": round(start_time, 2) if start_time is not None else None
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Sentence timing map saved to {OUTPUT_FILE} ({len(result)} sentences)")