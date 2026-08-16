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

clean_text = re.sub(r"\[.*?\]", "", story_text)
clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_text)
clean_text = re.sub(r"---", " ", clean_text)
clean_text = re.sub(r"\s+", " ", clean_text).strip()
first_sentence_match = re.match(r"(.+?[.!?])\s", clean_text)
description = first_sentence_match.group(1) if first_sentence_match else clean_text[:150]

new_card = f'''    <a href="{slug}.html" class="story-card story-card--available">
      <div class="story-card__image" style="background-image: url('images/{slug}-card.png'); background-size: cover; background-position: center;"></div>
      <h2>{title}</h2>
      <p>{description}</p>
    </a>'''

coming_soon_pattern = re.compile(
    r'    <div class="story-card story-card--coming-soon">\s*'
    r'<div class="story-card__image story-card__image--placeholder"></div>\s*'
    r'<h2>Coming soon</h2>\s*'
    r'</div>',
)

with open("site/index.html", "r", encoding="utf-8") as f:
    homepage = f.read()

new_homepage, count = coming_soon_pattern.subn(new_card, homepage, count=1)

if count == 0:
    raise SystemExit("No 'Coming soon' slot found to replace. Check site/index.html structure.")

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(new_homepage)

print(f"Homepage updated: replaced one 'Coming soon' slot with '{title}'.")
