import re
import json
import os

STORY_FILE = os.environ.get("STORY_FILE")
if not STORY_FILE:
    raise SystemExit("STORY_FILE not set.")


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\u0900-\u097F\[])', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def strip_tags(text):
    return re.sub(r'\[.*?\]', '', text).strip()


with open(STORY_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
frontmatter_text, story_text = match.groups()

title_match = re.search(r"title:\s*(.+)", frontmatter_text)
title = title_match.group(1).strip() if title_match else "Untitled story"
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

final_text_path = f"content/audio/{slug}-en-final-text.txt"
timestamps_path = f"content/audio/{slug}-en-timestamps.json"
output_path = f"content/audio/{slug}-en-sentences.json"

with open(final_text_path, "r", encoding="utf-8") as f:
    final_text = f.read().strip()

with open(timestamps_path, "r", encoding="utf-8") as f:
    alignment = json.load(f)

characters = alignment["characters"]
start_times = alignment["character_start_times_seconds"]

# Clean the display text the same way the original Hanuman script did -
# strip markdown artifacts so sentence splitting matches the tagged text
display_text = story_text.replace("---", " ")
display_text = display_text.replace("*", "")
display_text = re.sub(r"\[.*?\]", "", display_text)  # strip audio tags too, for display
display_text = re.sub(r"\s+", " ", display_text).strip()

final_sentences = split_into_sentences(final_text)
display_sentences = split_into_sentences(display_text)

if len(final_sentences) != len(display_sentences):
    print(f"WARNING: sentence count mismatch - final text has {len(final_sentences)}, "
          f"display text has {len(display_sentences)}. Review before using this output.")

result = []
search_pos = 0
for i, sentence in enumerate(final_sentences):
    idx = final_text.find(sentence, search_pos)
    if idx == -1:
        print(f"WARNING: could not locate sentence {i} in final text, skipping timing for it.")
        continue
    search_pos = idx + len(sentence)

    start_time = None
    for char_idx in range(idx, min(idx + len(sentence), len(characters))):
        start_time = start_times[char_idx]
        break

    display_sentence = display_sentences[i] if i < len(display_sentences) else strip_tags(sentence)

    result.append({
        "text": display_sentence,
        "start": round(start_time, 2) if start_time is not None else None
    })

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Sentence timing map saved to {output_path} ({len(result)} sentences)")
