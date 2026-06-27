"""Trilium Notes MCP Server — slide and presentation management via ETAPI."""

import os
import json
import time
import logging
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

TRILIUM_URL = os.getenv("TRILIUM_URL", "http://localhost:8080")
TRILIUM_API_KEY = os.getenv("TRILIUM_API_KEY", "")
DEFAULT_PARENT = os.getenv("TRILIUM_DEFAULT_PARENT", "root")

if not TRILIUM_API_KEY:
    raise EnvironmentError(
        "TRILIUM_API_KEY is not set.\n"
        "Generate a token in Trilium: Options → ETAPI → Create new token.\n"
        "Then set it in the MCP server env block in claude_desktop_config.json."
    )

logger = logging.getLogger("trilium-mcp")

mcp = FastMCP("trilium-presenter")


def _headers() -> dict:
    return {"Authorization": TRILIUM_API_KEY, "Content-Type": "application/json"}


def _get(path: str) -> dict:
    r = httpx.get(f"{TRILIUM_URL}/etapi/{path}", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict) -> dict:
    r = httpx.post(f"{TRILIUM_URL}/etapi/{path}", headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def _patch(path: str, body: dict) -> dict:
    r = httpx.patch(f"{TRILIUM_URL}/etapi/{path}", headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json() if r.content else {}


def _put_content(note_id: str, content: str) -> None:
    r = httpx.put(
        f"{TRILIUM_URL}/etapi/notes/{note_id}/content",
        headers={**_headers(), "Content-Type": "text/plain"},
        content=content.encode(),
        timeout=10,
    )
    r.raise_for_status()


def _delete(path: str) -> None:
    r = httpx.delete(f"{TRILIUM_URL}/etapi/{path}", headers=_headers(), timeout=10)
    r.raise_for_status()


def _get_content(note_id: str) -> str:
    r = httpx.get(
        f"{TRILIUM_URL}/etapi/notes/{note_id}/content",
        headers={"Authorization": TRILIUM_API_KEY},
        timeout=10,
    )
    r.raise_for_status()
    return r.text


def _search(query: str, limit: int = 20) -> list[dict]:
    r = httpx.get(
        f"{TRILIUM_URL}/etapi/notes",
        headers=_headers(),
        params={"search": query, "limit": limit},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else data.get("results", [])


def _set_attribute(note_id: str, name: str, value: str) -> dict:
    # Check if attribute exists first
    note = _get(f"notes/{note_id}")
    for attr in note.get("attributes", []):
        if attr["name"] == name and attr["type"] == "label":
            r = httpx.patch(
                f"{TRILIUM_URL}/etapi/attributes/{attr['attributeId']}",
                headers=_headers(),
                json={"value": value},
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
    # Create new attribute
    return _post("attributes", {
        "noteId": note_id,
        "type": "label",
        "name": name,
        "value": value,
    })


# ── Presentations ──────────────────────────────────────────────────────────────

@mcp.tool()
def create_presentation(title: str, parent_note_id: str = DEFAULT_PARENT) -> str:
    """Create a new presentation container note.

    Args:
        title: Title of the presentation.
        parent_note_id: Parent note ID where the presentation will be created.
                        Defaults to the configured default parent.
    Returns:
        JSON with noteId of the created presentation.
    """
    result = _post("create-note", {
        "parentNoteId": parent_note_id,
        "title": title,
        "type": "text",
        "content": "",
    })
    return json.dumps({"noteId": result["note"]["noteId"], "title": title})


@mcp.tool()
def list_presentations(parent_note_id: str = DEFAULT_PARENT) -> str:
    """List child notes under a parent, as a tree navigator.

    In Trilium Presenter any note with children is presentable — there is no
    dedicated "presentation" marker. This tool therefore lists the direct
    children of a parent and reports `hasChildren`/`childCount` so a caller can
    drill down through organisational folders to reach an actual deck. To get
    the slides that a node would present, call `list_slides` on it.

    Args:
        parent_note_id: Parent note ID to list children from.
    Returns:
        JSON array of notes with noteId, title, type, childCount, hasChildren.
    """
    note = _get(f"notes/{parent_note_id}")
    results = []
    for child_id in note.get("childNoteIds", []):
        child = _get(f"notes/{child_id}")
        child_ids = child.get("childNoteIds", [])
        results.append({
            "noteId": child_id,
            "title": child["title"],
            "type": child["type"],
            "childCount": len(child_ids),
            "hasChildren": bool(child_ids),
        })
    return json.dumps(results)


@mcp.tool()
def get_note_info(note_id: str) -> str:
    """Get metadata for a note (title, type, children, attributes).

    Args:
        note_id: The Trilium note ID.
    Returns:
        JSON with note metadata.
    """
    return json.dumps(_get(f"notes/{note_id}"))


# ── Slides ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def create_slide(
    presentation_id: str,
    title: str,
    content: str,
    slide_type: str = "content",
) -> str:
    """Create a new slide (child note) under a presentation.

    Slides are Markdown code notes. When writing `content`, follow the slide
    format appended to this description below — it is loaded live from the
    Trilium #presenterSlideFormat note, so it is the authoritative, up-to-date
    source for structure, conventions and voice.

    Args:
        presentation_id: Note ID of the parent presentation.
        title: Slide title (shown in the Trilium tree).
        content: Markdown content of the slide.
        slide_type: Slide type label — 'title', 'content', or a custom type.
    Returns:
        JSON with noteId of the created slide.
    """
    result = _post("create-note", {
        "parentNoteId": presentation_id,
        "title": title,
        "type": "code",
        "mime": "text/x-markdown",
        "content": content,
        "prefix": "Folie",
    })
    note_id = result["note"]["noteId"]
    _set_attribute(note_id, "slideType", slide_type)
    return json.dumps({"noteId": note_id, "title": title, "slideType": slide_type})


@mcp.tool()
def get_slide(note_id: str) -> str:
    """Get the Markdown content of a slide.

    Args:
        note_id: The note ID of the slide.
    Returns:
        The raw Markdown content.
    """
    return _get_content(note_id)


@mcp.tool()
def update_slide(
    note_id: str,
    content: str | None = None,
    title: str | None = None,
    slide_type: str | None = None,
) -> str:
    """Update a slide's title, content, or slide type.

    Args:
        note_id: The note ID of the slide.
        content: New Markdown content (optional).
        title: New title (optional).
        slide_type: New slide type label (optional).
    Returns:
        JSON confirming the update.
    """
    if content is not None:
        _put_content(note_id, content)
    if title is not None:
        _patch(f"notes/{note_id}", {"title": title})
    if slide_type is not None:
        _set_attribute(note_id, "slideType", slide_type)
    return json.dumps({"noteId": note_id, "updated": True})


def _sorted_child_branches(note: dict) -> list[tuple[str, str]]:
    """Return (branchId, childNoteId) pairs for a note, sorted by notePosition.

    Mirrors the widget's getSortedChildren so list_slides yields slides in the
    exact order they will be presented.
    """
    branches = []
    for branch_id in note.get("childBranchIds", []):
        branch = _get(f"branches/{branch_id}")
        branches.append((branch.get("notePosition", 0), branch_id, branch["noteId"]))
    branches.sort(key=lambda b: b[0])
    return [(branch_id, note_id) for _pos, branch_id, note_id in branches]


def _collect_slides(note_id: str, branch_id: str, visited: set, slides: list, depth: int) -> None:
    """Depth-first pre-order slide collection — mirrors collectSlides in widget.js.

    `text` notes are HTML containers: skipped as slides but recursed into.
    `image`/`file` notes are skipped entirely. Everything else (code/markdown)
    is emitted as a slide and still recursed into. A visited set guards against
    circular clones.
    """
    if note_id in visited:
        return
    visited.add(note_id)

    note = _get(f"notes/{note_id}")
    note_type = note["type"]

    if note_type in ("image", "file"):
        return

    if note_type != "text":  # a slide (code / markdown), not a container
        slide_type = next(
            (a["value"] for a in note.get("attributes", []) if a["name"] == "slideType"),
            None,
        )
        if not slide_type:
            slide_type = "title" if not slides else "content"
        child_ids = note.get("childNoteIds", [])
        slides.append({
            "noteId": note_id,
            "branchId": branch_id,
            "title": note["title"],
            "slideType": slide_type,
            "type": note_type,
            "mime": note.get("mime", ""),
            "depth": depth,
            "hasChildren": bool(child_ids),
            "contentLength": len(_get_content(note_id)),
        })

    for child_branch_id, child_id in _sorted_child_branches(note):
        _collect_slides(child_id, child_branch_id, visited, slides, depth + 1)


@mcp.tool()
def list_slides(presentation_id: str, recursive: bool = True) -> str:
    """List the slides a presentation node would actually present.

    By default this performs the same depth-first, pre-order traversal as the
    "Present" button (see widget.js collectSlides): it descends the whole
    subtree, treating `text` notes as HTML containers (skipped but recursed
    into) and emitting `code`/Markdown notes as slides, in notePosition order.
    This means deep folder structures (Topic → Subtopic → slides) resolve to
    the real slide list instead of intermediate container notes.

    Set `recursive=False` for the legacy flat behaviour (direct children only),
    which does not skip containers.

    Args:
        presentation_id: Note ID of the presentation (any note with children).
        recursive: Walk the full subtree like the presenter (default True).
    Returns:
        JSON array of slides with noteId, branchId, title, slideType, type,
        mime, depth, hasChildren, and contentLength. branchId is required for
        move_slide.
    """
    note = _get(f"notes/{presentation_id}")

    if recursive:
        slides: list = []
        visited: set = set()
        for branch_id, child_id in _sorted_child_branches(note):
            _collect_slides(child_id, branch_id, visited, slides, 0)
        return json.dumps(slides)

    results = []
    for branch_id in note.get("childBranchIds", []):
        branch = _get(f"branches/{branch_id}")
        child_id = branch["noteId"]
        child = _get(f"notes/{child_id}")
        slide_type = next(
            (a["value"] for a in child.get("attributes", []) if a["name"] == "slideType"),
            "content",
        )
        results.append({
            "noteId": child_id,
            "branchId": branch_id,
            "title": child["title"],
            "slideType": slide_type,
            "type": child["type"],
            "mime": child.get("mime", ""),
        })
    return json.dumps(results)


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Delete a note (slide or presentation).

    Args:
        note_id: The note ID to delete.
    Returns:
        JSON confirming deletion.
    """
    _delete(f"notes/{note_id}")
    return json.dumps({"noteId": note_id, "deleted": True})


# ── Master / Sets workflow ─────────────────────────────────────────────────────

@mcp.tool()
def clone_slide(note_id: str, target_presentation_id: str) -> str:
    """Clone a slide into another presentation (Master → Sets workflow).

    Creates a new branch so the slide appears in the target presentation.
    Editing the cloned note updates it everywhere it appears.

    Args:
        note_id: The note ID of the slide to clone.
        target_presentation_id: The presentation note ID to clone into.
    Returns:
        JSON with the new branchId.
    """
    result = _post("branches", {
        "noteId": note_id,
        "parentNoteId": target_presentation_id,
        "prefix": "Folie",
    })
    return json.dumps({"branchId": result["branchId"], "noteId": note_id})


@mcp.tool()
def move_slide(branch_id: str, new_position: int) -> str:
    """Change the position (order) of a slide within its presentation.

    Use list_slides to get the branchId for each slide.

    Args:
        branch_id: The branch ID of the slide to move.
        new_position: New position index (higher = later in presentation).
    Returns:
        JSON confirming the move.
    """
    _patch(f"branches/{branch_id}", {"notePosition": new_position * 10})
    return json.dumps({"branchId": branch_id, "newPosition": new_position})


# ── Search ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def search_notes(query: str, limit: int = 20) -> str:
    """Search Trilium notes by title or content.

    Supports Trilium's search syntax, e.g.:
    - Plain text: "introduction"
    - By attribute: "#slideType=title"
    - By label: "#presenterTheme"

    Args:
        query: Search query string.
        limit: Maximum number of results (default 20).
    Returns:
        JSON array of matching notes with noteId and title.
    """
    notes = _search(query, limit)
    return json.dumps([{"noteId": n["noteId"], "title": n["title"]} for n in notes])


# ── Prompts ────────────────────────────────────────────────────────────────────

SLIDE_FORMAT_LABEL = "presenterSlideFormat"

_TOOL_WORKFLOW_HEADER = f"""# Trilium Presenter — Slide Creation

## Tool workflow
1. `create_presentation(title, parent_note_id)` → returns the presentation `noteId`.
2. `create_slide(presentation_id, title, content, slide_type)` for each slide.
   First slide: `slide_type="title"`; all others: `slide_type="content"`.
3. For the Master/Sets workflow, reuse slides with `clone_slide` and reorder with `move_slide`.

The slide format and authoring conventions below are loaded live from the Trilium
note labelled `#{SLIDE_FORMAT_LABEL}`, so the author can maintain them in one place.
"""


@mcp.prompt()
def slide_creation_guide() -> list[TextContent]:
    """Style guide and instructions for creating Trilium Presenter slides.

    Loads the slide format from the Trilium note labelled #presenterSlideFormat
    (the single source of truth, shipped with the plugin and author-editable),
    prefixed with the tool workflow. If that note cannot be loaded this returns
    a STOP notice — never a silent built-in substitute — so a missing or
    unreachable format can never masquerade as the real thing.
    """
    fmt, source_id = _fetch_slide_format()
    if source_id:
        body = f"{fmt}\n\n_Format source: Trilium note {source_id} (#{SLIDE_FORMAT_LABEL})_"
    else:
        body = fmt  # already the loud unavailable notice
    return [TextContent(type="text", text=f"{_TOOL_WORKFLOW_HEADER}\n{body}")]


# ── Live slide format in tool descriptions ───────────────────────────────────
# The slide_creation_guide prompt above already exposes #presenterSlideFormat,
# but MCP *prompts* are not reliably injected into the model's context — only
# tool names, descriptions and schemas are guaranteed to arrive. So we also
# embed the format note directly into the create_slide / update_slide
# descriptions at tools/list time. The Trilium note stays the single source of
# truth; editing it changes what the model sees on the next connection.

_FORMAT_TOOLS = ("create_slide", "update_slide")
_FORMAT_CACHE_TTL = 60.0  # seconds — avoid hammering ETAPI during a tools/list burst
_format_cache: dict[str, object] = {"text": None, "source": None, "ts": 0.0}
_base_descriptions: dict[str, str] = {}

_FORMAT_UNAVAILABLE = f"""\
⚠️ SLIDE FORMAT UNAVAILABLE — DO NOT GUESS
The authoritative #{SLIDE_FORMAT_LABEL} note could not be loaded from Trilium
(label missing or ETAPI unreachable). This note ships with the plugin and is the
single source of truth for slide structure, conventions and voice. Do NOT invent
a format or rely on remembered rules. Stop, tell the author the format note is
unreachable, and let them fix it before any slide is created or updated."""


def _fetch_slide_format() -> tuple[str, str | None]:
    """Return (format_text, source_note_id) for the #presenterSlideFormat note.

    The note is shipped with the plugin, so it is expected to exist. If it is
    missing or ETAPI is unreachable we return (_FORMAT_UNAVAILABLE, None) — a
    loud do-not-guess notice — rather than a built-in format that could silently
    drift from the author's source of truth. Only successful loads are cached;
    failures are not, so a transient ETAPI blip recovers on the next call.
    """
    now = time.monotonic()
    cached = _format_cache["text"]
    if isinstance(cached, str) and now - float(_format_cache["ts"]) < _FORMAT_CACHE_TTL:
        return cached, _format_cache["source"]  # type: ignore[return-value]
    try:
        notes = _search(f"#{SLIDE_FORMAT_LABEL}", limit=1)
        if notes:
            note_id = notes[0]["noteId"]
            content = _get_content(note_id).strip()
            if content:
                _format_cache.update(text=content, source=note_id, ts=now)
                return content, note_id
        logger.warning("#%s note not found — returning unavailable notice", SLIDE_FORMAT_LABEL)
    except Exception as exc:  # never let format lookup break the tool list
        logger.warning("Could not load #%s: %s", SLIDE_FORMAT_LABEL, exc)
    return _FORMAT_UNAVAILABLE, None


@mcp._mcp_server.list_tools()
async def _list_tools_with_live_format():
    """list_tools handler that embeds the live slide format into the
    create_slide / update_slide descriptions (overrides FastMCP's default)."""
    fmt, source_id = _fetch_slide_format()
    if source_id:
        block = (
            f"--- Slide format (live from Trilium #{SLIDE_FORMAT_LABEL}, "
            f"note {source_id}) ---\n{fmt}"
        )
    else:
        block = fmt  # already the loud unavailable notice
    for tool in mcp._tool_manager.list_tools():
        if tool.name in _FORMAT_TOOLS:
            base = _base_descriptions.setdefault(tool.name, tool.description)
            tool.description = f"{base}\n\n{block}"
    return await mcp.list_tools()


if __name__ == "__main__":
    mcp.run()
