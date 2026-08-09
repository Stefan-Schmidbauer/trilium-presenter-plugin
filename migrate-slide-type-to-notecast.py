#!/usr/bin/env python3
"""Migrate the Slide Format note to the Notecast `#notecastType=slide` contract.

Background: the MCP server (trilium-notecast-mcp) no longer reads
`#presenterSlideFormat` — it resolves note types by `#notecastType=<id>`. The
slide format note therefore needs the Notecast labels so the MCP can keep
authoring slides. The presenter *widget* never read `#presenterSlideFormat`, so
this change does not touch presentation; only the MCP-facing contract moves.

This is **additive and idempotent**: it adds the five Notecast labels if missing
and leaves `#presenterSlideFormat` in place. Remove that old label once you have
verified the MCP resolves the slide type end to end.

Themes are intentionally NOT migrated: presenter themes stay on `#presenterTheme`
(their multi-CSS structure does not map onto Notecast's single-CSS-note theme,
and the widget discovers them by that label).

Run (credentials from .trilium-env):
    set -a; . ./.trilium-env; set +a
    python3 migrate-slide-type-to-notecast.py

The import zip carries these labels independently: they are declared in
build-zip.py, on the Slide Format note. Nothing needs re-exporting.
"""
import os
import sys

import httpx

URL = os.environ["TRILIUM_URL"].rstrip("/")
KEY = os.environ["TRILIUM_API_KEY"]
H = {"Authorization": KEY, "Content-Type": "application/json"}

# The slide type definition, as read by the MCP's create_note.
LABELS = {
    "notecastType": "slide",
    "notecastTargetType": "code",
    "notecastMime": "text/x-markdown",
    "notecastApplyLabels": "slideType=content",
    "notecastPrefix": "Folie",
}


def search(query: str) -> list[dict]:
    r = httpx.get(f"{URL}/etapi/notes", headers=H,
                  params={"search": query, "limit": 5}, timeout=10)
    r.raise_for_status()
    d = r.json()
    return d if isinstance(d, list) else d.get("results", [])


def main() -> None:
    # Prefer an already-migrated note; otherwise locate the legacy one.
    hits = search("#notecastType=slide") or search("#presenterSlideFormat")
    if len(hits) != 1:
        sys.exit(f"Expected exactly one slide-format note, found {len(hits)}. "
                 "Resolve the ambiguity in Trilium first.")
    note_id = hits[0]["noteId"]

    # Fresh read for a reliable idempotency check.
    r = httpx.get(f"{URL}/etapi/notes/{note_id}", headers=H, timeout=10)
    r.raise_for_status()
    note = r.json()
    existing = {a["name"] for a in note.get("attributes", []) if a["type"] == "label"}
    print(f"note {note_id} ({note.get('title')!r}) — existing labels: {sorted(existing)}")

    for name, value in LABELS.items():
        if name in existing:
            print(f"  skip  #{name} (already present)")
            continue
        a = httpx.post(f"{URL}/etapi/attributes", headers=H, json={
            "noteId": note_id, "type": "label", "name": name, "value": value,
        }, timeout=10)
        a.raise_for_status()
        print(f"  add   #{name}={value!r}")

    print("done. #presenterSlideFormat left in place — remove it once verified.")


if __name__ == "__main__":
    main()
