import os
import re
import shutil

STORY_FILE = os.environ.get("STORY_FILE")
if not STORY_FILE:
    raise SystemExit("STORY_FILE not set. Example: content/hanuman-leap-of-faith.md")

with open(STORY_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", raw, re.DOTALL)
frontmatter_text, _ = match.groups()

title_match = re.search(r"title:\s*(.+)", frontmatter_text)
title = title_match.group(1).strip() if title_match else "Untitled story"
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

archive_dir = f"content/archive/{slug}"
os.makedirs(archive_dir, exist_ok=True)

files_to_archive = [
    f"site/{slug}.html",
    f"site/audio/{slug}-en.mp3",
    f"site/audio/{slug}-en-sentences.json",
    f"site/images/{slug}-card.png",
]

moved = []
for filepath in files_to_archive:
    if os.path.exists(filepath):
        dest = os.path.join(archive_dir, os.path.basename(filepath))
        shutil.move(filepath, dest)
        moved.append(f"{filepath} -> {dest}")
    else:
        print(f"Note: {filepath} not found, skipping.")

with open("site/index.html", "r", encoding="utf-8") as f:
    homepage = f.read()

card_pattern = re.compile(
    rf'    <a href="{re.escape(slug)}\.html" class="story-card story-card--available">.*?</a>',
    re.DOTALL
)

coming_soon_block = '''    <div class="story-card story-card--coming-soon">
      <div class="story-card__image story-card__image--placeholder"></div>
      <h2>Coming soon</h2>
    </div>'''

new_homepage, count = card_pattern.subn(coming_soon_block, homepage, count=1)

if count == 0:
    print(f"WARNING: could not find '{title}' card in site/index.html to remove.")
else:
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(new_homepage)
    print(f"Homepage updated: '{title}' card replaced with 'Coming soon'.")

print(f"\nArchived {len(moved)} file(s) to {archive_dir}:")
for m in moved:
    print(f"  {m}")
print(f"\n'{title}' has been taken down from the live site.")
