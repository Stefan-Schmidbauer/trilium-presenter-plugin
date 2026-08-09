#!/usr/bin/env python3
"""Build the Trilium import zip.

The note tree is declared once, in TREE, and everything follows from it: the
files that go into the archive and the `!!!meta.json` that gives Trilium each
note's title, type, mime and — the part that matters — its labels.

This replaces the earlier split of "meta.json exported from a live Trilium, plus
a shell script that copies files next to it". That split meant two places to
update for one new note, and forgetting the second one shipped a note without its
labels. It did exactly that: meta.json went stale for months, and the release zip
would have carried a Slide Format note with no #notecastType — leaving the MCP
server unable to author slides on a fresh install.

The ids here are derived from each note's path. That is not a loss of fidelity:
Trilium assigns fresh ids on import anyway (verified — none of the ids in the old
exported meta.json matched the live instance), so they only ever had to be
consistent with one another.

Usage:  python3 build-zip.py [version]
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import zipfile

HERE = pathlib.Path(__file__).parent

MD = "text/x-markdown"
CSS = "text/css"
HTML = "text/html"
JS = "application/javascript;env=frontend"
SVG = "image/svg+xml"
EXT = {MD: ".mkd", CSS: ".css", HTML: ".html", JS: ".js"}


def slide(title: str, md: str, slide_type: str | None = None, **kw) -> dict:
    """An example-presentation slide."""
    label = {"slideType": slide_type} if slide_type else {}
    return dict(title=title, mime=MD, file=f"example/{md}", label=label, **kw)


def template(title: str, md: str, slide_type: str | None = None) -> dict:
    """A slide template, discoverable by #template."""
    label = {"template": ""}
    if slide_type:
        label["slideType"] = slide_type
    return dict(title=title, mime=MD, file=f"templates/{md}", label=label)


def theme(title: str, folder: str) -> dict:
    """A presenter theme: a container note holding one CSS note per slide role.

    This multi-note shape is why presenter themes stay on #presenterTheme and are
    not Notecast themes — a #notecastTheme is a single note whose content is the
    stylesheet. See the label contract in the MCP repo.
    """
    bg = f"assets/backgrounds/{folder}"
    return dict(
        title=title, mime=HTML, file=f"assets/container-html/{title}-Theme.html",
        label={"presenterTheme": ""}, kids=[
            dict(title="Base", mime=CSS, file=f"themes/{folder}/base.css"),
            dict(title="Title Slide", mime=CSS, file=f"themes/{folder}/title-slide.css",
                 attach=[("background.svg", f"{bg}/Title Slide_background.svg")]),
            dict(title="Content Slide", mime=CSS, file=f"themes/{folder}/content-slide.css",
                 attach=[("background.svg", f"{bg}/Content Slide_background.svg")]),
            dict(title="Chapter Slide", mime=CSS, file=f"themes/{folder}/chapter-slide.css"),
        ])


TREE = dict(
    title="Trilium Presenter", mime=HTML,
    file="assets/container-html/Trilium Presenter.html", kids=[

        dict(title="Widget", mime=JS, file="src/widget.js", label={"widget": ""}),

        dict(title="Documentation", mime=HTML,
             file="assets/container-html/Documentation.html", kids=[
            dict(title="Getting Started", mime=MD, file="docs/getting-started.md"),
            # The one note two tools share: the presenter documents the slide
            # format for humans, the MCP reads the same note as its authoring
            # instructions. #presenterSlideFormat is the legacy label, kept
            # until the MCP is proven end to end; #notecastType=slide is live.
            dict(title="Slide Format", mime=MD, file="docs/slide-format.md", label={
                "presenterSlideFormat": "",
                "notecastType": "slide",
                "notecastTargetType": "code",
                "notecastMime": MD,
                "notecastApplyLabels": "slideType=content",
                "notecastPrefix": "Folie",
            }),
            dict(title="Slide Content", mime=MD, file="docs/slide-content.md"),
            dict(title="Themes", mime=MD, file="docs/themes.md"),
            dict(title="Content Organization", mime=MD, file="docs/content-organization.md"),
            dict(title="About", mime=MD, file="docs/about.md"),
            dict(title="MCP Server", mime=MD, file="docs/mcp.md"),
        ]),

        dict(title="Example Presentation", mime=HTML,
             file="assets/container-html/Example Presentation.html", kids=[
            slide("Title Slide", "title-slide.md", "title"),
            slide("What is Trilium Presenter?", "what-is-trilium-presenter.md", "content"),
            slide("Getting Started", "before-vs-after.md", "content"),
            slide("Markdown & Layouts", "under-the-hood.md", "chapter", kids=[
                slide("Markdown Syntax", "how-it-works.md"),
                slide("Columns and Speaker Notes", "architecture.md"),
            ]),
            slide("Images in Slides", "image-demo.md", "content",
                  attach=[("workflow.svg", "assets/images/workflow.svg")]),
            # "Two", not "Three": the handout was the third way and now lives in
            # trilium-notecast-render. The title has to track the slide's own
            # heading — they are shown together in the tree and on screen.
            slide("Two Ways to Present", "presenter-mode.md", "content"),
            slide("Reusable Slides", "clone-workflow.md", "chapter", kids=[
                slide("Build a Slide Library", "master-library.md"),
                slide("How Clones Work", "clones-explained.md"),
            ]),
            slide("Get Started", "thank-you.md", "title"),
        ]),

        dict(title="Themes", mime=HTML, file="assets/container-html/Themes.html", kids=[
            theme("Default", "default"),
            theme("Dark", "dark"),
        ]),

        dict(title="Templates", mime=HTML,
             file="assets/container-html/Templates.html", kids=[
                 template("Title", "title.md", "title"),
                 template("Agenda", "agenda.md"),
                 template("Bullet Points", "bullet-points.md"),
                 template("Two Columns", "two-columns.md"),
                 template("Three Columns", "three-columns.md"),
                 template("Image", "image.md"),
                 template("Image with Text", "image-with-text.md"),
                 template("Code", "code.md"),
                 template("Quote", "quote.md"),
                 template("Chapter", "section-break.md", "chapter"),
                 template("Thank You", "thank-you.md", "title"),
             ]),
    ])


def _id(text: str) -> str:
    return hashlib.sha1(text.encode(), usedforsecurity=False).hexdigest()[:12]


def safe_name(title: str) -> str:
    """Turn a note title into a file name, the way Trilium's own export does.

    Two rules, both taken from the previously exported meta.json: `&` spells out
    as "and", and characters a file system rejects are dropped. The second matters
    beyond cosmetics — `?` is illegal on Windows, so a zip carrying it cannot be
    unpacked there at all.
    """
    name = title.replace("&", "and")
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    return " ".join(name.split())


def build(node: dict, zf: zipfile.ZipFile, path: list[str], ids: list[str],
          folder: str, position: int) -> dict:
    """Write one note (and its attachments) into the archive; return its entry."""
    key = "/".join(path + [node["title"]])
    nid = _id(key)
    mime = node["mime"]

    # A note with children must bring a content file of its own. The archive
    # holds no directory entries, so a parent that contributes no member is one
    # Trilium never creates — it then fails on that note's first child with
    # "Parent note '...' was not found." and aborts the whole import. Shipped
    # exactly that way once, with Documentation and Example Presentation.
    if "kids" in node and "file" not in node:
        raise ValueError(f"container note {key!r} has children but no content file")

    entry = {
        "isClone": False,
        "noteId": nid,
        "notePath": ids + [nid],
        "title": node["title"],
        "notePosition": position,
        "prefix": None,
        "isExpanded": False,
        "type": "text" if mime == HTML else "code",
        "mime": mime,
        # Trilium marks every text note as html, container notes included.
        **({"format": "html"} if mime == HTML else {}),
        "attributes": [
            {"type": "label", "name": name, "value": value,
             "isInheritable": False, "position": (i + 1) * 10}
            for i, (name, value) in enumerate(node.get("label", {}).items())
        ],
        "attachments": [],
    }

    def write(name: str, data: bytes) -> None:
        zf.writestr(f"{folder}/{name}" if folder else name, data)

    if "file" in node:
        filename = safe_name(node["title"]) + EXT[mime]
        entry["dataFileName"] = filename
        if mime == HTML:
            entry["format"] = "html"
        write(filename, (HERE / node["file"]).read_bytes())

    # Attachments keep the source file's name: within one folder that is already
    # unique (the presenter prefixes them by slide role), which is exactly what
    # the old export produced.
    for i, (title, src) in enumerate(node.get("attach", [])):
        data_name = pathlib.Path(src).name
        entry["attachments"].append({
            "attachmentId": _id(f"{key}#{title}"),
            "title": title,
            "role": "image",
            "mime": SVG,
            "position": (i + 1) * 10,
            "dataFileName": data_name,
        })
        write(data_name, (HERE / src).read_bytes())

    if "kids" in node:
        entry["dirFileName"] = safe_name(node["title"])
        sub = f"{folder}/{entry['dirFileName']}" if folder else entry["dirFileName"]
        entry["children"] = [
            build(kid, zf, path + [node["title"]], ids + [nid], sub, (i + 1) * 10)
            for i, kid in enumerate(node["kids"])
        ]

    return entry


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "dev"
    out = HERE / "trilium-presenter-plugin.zip"

    # Stamp the version onto the root note as #version. Without this the
    # argument only reached the line printed below, so two zips built from
    # different tags were byte-identical and an installed plugin gave no way to
    # tell which release it came from.
    tree = {**TREE, "label": {**TREE.get("label", {}), "version": version}}

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        root = build(tree, zf, [], [], "", 120)
        zf.writestr("!!!meta.json", json.dumps(
            {"formatVersion": 2, "appVersion": "0.102.1", "files": [root]},
            indent=4, ensure_ascii=False))

    def count(node: dict) -> int:
        return 1 + sum(count(c) for c in node.get("children", []))

    print(f"Built {out.name} ({version}) — {count(root)} notes")


if __name__ == "__main__":
    main()
