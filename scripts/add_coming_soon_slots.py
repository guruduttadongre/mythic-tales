import os
import re
import sys

COUNT = int(os.environ.get("SLOT_COUNT", sys.argv[1] if len(sys.argv) > 1 else 1))

coming_soon_block = '''
    <div class="story-card story-card--coming-soon">
      <div class="story-card__image story-card__image--placeholder"></div>
      <h2>Coming soon</h2>
    </div>'''

new_slots = coming_soon_block * COUNT

with open("site/index.html", "r", encoding="utf-8") as f:
    homepage = f.read()

# Insert the new slots right before the closing </main> tag
if "</main>" not in homepage:
    raise SystemExit("Could not find </main> tag in site/index.html")

new_homepage = homepage.replace("</main>", f"{new_slots}\n\n  </main>")

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(new_homepage)

print(f"Added {COUNT} 'Coming soon' slot(s) to site/index.html")
