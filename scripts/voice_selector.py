import json
import sys


def get_voice_for_source(source_text, voices_path="content/voices.json"):
    """
    Given a story's source text (e.g. 'Ramayana (Sundara Kanda)'),
    return the matching voice's (name, voice_id) from voices.json.
    Falls back to the 'folklore' voice if nothing else matches.
    """
    with open(voices_path, "r", encoding="utf-8") as f:
        voices = json.load(f)

    source_lower = source_text.lower()

    # Check every category except folklore for an explicit match first
    for category, voice in voices.items():
        if category == "folklore":
            continue
        for keyword in voice.get("matches_sources", []):
            if keyword.lower() in source_lower:
                return voice["name"], voice["voice_id"], category

    # No match found - use folklore as the default fallback
    fallback = voices["folklore"]
    return fallback["name"], fallback["voice_id"], "folklore (default)"


if __name__ == "__main__":
    # Standalone test: pass a source string as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/voice_selector.py \"<source text>\"")
        sys.exit(1)

    test_source = sys.argv[1]
    name, voice_id, category = get_voice_for_source(test_source)
    print(f"Source: '{test_source}'")
    print(f"Matched category: {category}")
    print(f"Selected voice: {name} ({voice_id})")
