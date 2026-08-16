import os
import re

STORY_FILE = os.environ.get("STORY_FILE")
if not STORY_FILE:
    raise SystemExit("STORY_FILE not set.")

with open(STORY_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
frontmatter_text, story_text = match.groups()

title_match = re.search(r"title:\s*(.+)", frontmatter_text)
title = title_match.group(1).strip() if title_match else "Untitled story"

slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

# Use the first real sentence of the story as a description, cleaned up
clean_text = re.sub(r"\[.*?\]", "", story_text)
clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_text)
clean_text = re.sub(r"---", " ", clean_text)
clean_text = re.sub(r"\s+", " ", clean_text).strip()
first_sentence_match = re.match(r"(.+?[.!?])\s", clean_text)
description = first_sentence_match.group(1) if first_sentence_match else clean_text[:150]

audio_file = f"{slug}-en.mp3"
image_file = f"{slug}-card.png"

with open("site/story-template.html", "r", encoding="utf-8") as f:
    template = f.read()

page = template.replace("{{TITLE}}", title)
page = page.replace("{{DESCRIPTION}}", description)
page = page.replace("{{SLUG}}", slug)
page = page.replace("{{AUDIO_FILE}}", audio_file)
page = page.replace("{{IMAGE_FILE}}", image_file)

output_path = f"site/{slug}.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(page)

print(f"Story page generated: {output_path}")
