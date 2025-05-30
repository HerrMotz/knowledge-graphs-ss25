#!/usr/bin/env python3
"""
Normalise ingredient lists inside OpenAI batch-response JSON files.

Works with:
  • JSON array files:        [ {…}, {…}, … ]
  • NDJSON / JSON-Lines:     {…}\n{…}\n…

Usage:
    python clean_pizza_json.py path/to/file.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------------------
# 1️⃣  Configure your replacements here
# --------------------------------------------------------------------------------------
RENAMES: dict[str, str] = {
    "banana pepper": "bell pepper",
    "1000 island dressing": "island dressing",
    "brazil nut parmesan": "parmesan",
    "Italian bread": "bread",
}
REMOVE: set[str] = {
    "dough",
    "1 topping",
    "2 toppings",
    "2 topping",
}
# --------------------------------------------------------------------------------------


def clean_ingredients(items: list[str]) -> list[str]:
    """Rename, drop and deduplicate ingredients (case-insensitive)."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        item = RENAMES.get(item.lower(), item)  # rename if a synonym exists
        if item.lower() in REMOVE:              # drop unwanted
            continue
        key = item.lower()
        if key not in seen:                     # deduplicate
            seen.add(key)
            out.append(item)
    return out


def clean_message_content(content: str) -> str:
    """Pull JSON out of ```json ...```, clean it, put it back (unchanged if none)."""
    m = re.search(r"```json\s*(.*?)\s*```", content, flags=re.S)
    if not m:
        return content  # nothing to do
    raw_json = m.group(1)
    parsed: Any = json.loads(raw_json)

    def _process(entry: Any) -> Any:
        if (
            isinstance(entry, dict)
            and isinstance(entry.get("ingredients"), list)
        ):
            entry["ingredients"] = clean_ingredients(entry["ingredients"])
        return entry

    if isinstance(parsed, list):
        parsed = [_process(e) for e in parsed]
    else:
        parsed = _process(parsed)

    pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
    return f"```json\n{pretty}\n```"


# ---------------------------  File I/O helpers  ---------------------------------------


def read_objects(path: Path) -> list[dict[str, Any]]:
    """Return list of JSON objects from either array-file or NDJSON."""
    text = path.read_text()
    text_strip = text.lstrip()
    try:
        # Try whole-file first (array or single object)
        loaded = json.loads(text_strip)
        return loaded if isinstance(loaded, list) else [loaded]
    except json.JSONDecodeError:
        # Fallback = NDJSON
        objects: list[dict[str, Any]] = []
        for n, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue  # skip blanks
            try:
                objects.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Line {n} is not valid JSON: {e.msg}"
                ) from e
        return objects


def write_objects(path: Path, objects: Iterable[dict[str, Any]], ndjson: bool) -> None:
    """Write list of objects back in same format (array or NDJSON)."""
    if ndjson:
        path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in objects) + "\n")
    else:
        path.write_text(json.dumps(list(objects), indent=2, ensure_ascii=False) + "\n")


# ---------------------------  Main cleaning routine  ----------------------------------


def main(file_path: str) -> None:
    path = Path(file_path)
    objs = read_objects(path)
    # Remember the original format to preserve it on write
    original_was_ndjson = not path.read_text().lstrip().startswith("[")
    for wrapper in objs:
        body = wrapper.get("response", {}).get("body")
        if not body:
            continue
        for choice in body.get("choices", []):
            msg = choice.get("message", {})
            if "content" in msg:
                msg["content"] = clean_message_content(msg["content"])
    write_objects(path, objs, ndjson=original_was_ndjson)
    print("✓ File cleaned in-place.")


# ---------------------------  Entry point  --------------------------------------------

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    sys.exit("Usage: python clean_pizza_json.py <batch.json>")
    #main(sys.argv[1])
    main("results_15_complete.jsonl")