"""The import zip must match the note tree it declares.

This exists because of a bug that actually shipped here. While `meta.json` was
exported from a live Trilium and the files were copied next to it by a separate
shell script, the two drifted for months: the release archive would have carried
a **Slide Format** note without `#notecastType`, leaving the MCP server unable to
author slides on a fresh install. `build-zip.py` collapsed that into one source;
these tests keep it honest, because nothing about a zip fails loudly on its own.

The presenter's tree is the richer of the two — attachments, multi-note theme
containers, templates — so it has more places for a declaration to go missing.
"""
import io
import json
import re
import zipfile

import pytest
from conftest import (
    REPO,
    TEST_VERSION,
    build,
    bz,
    find,
    labels,
    walk,
    walk_paths,
    walk_tree,
    walk_tree_paths,
)

# ── the archive matches its manifest ─────────────────────────────────────────


def test_meta_json_is_present_and_well_formed(archive):
    meta, names, _contents = archive
    assert "!!!meta.json" in names
    assert meta["formatVersion"] == 2
    assert len(meta["files"]) == 1


def test_every_declared_data_file_exists_in_the_archive(archive, root):
    """Trilium reads dataFileName from the manifest; a member that is not there
    is a note that imports empty."""
    _meta, names, _contents = archive
    basenames = {n.rsplit("/", 1)[-1] for n in names}
    missing = [
        (node["title"], node["dataFileName"])
        for node in walk(root)
        if "dataFileName" in node and node["dataFileName"] not in basenames
    ]
    assert missing == []


def test_every_attachment_file_exists_in_the_archive(archive, root):
    """Attachments carry their own dataFileName — a separate path through
    build(), and therefore a separate way to ship a broken archive."""
    _meta, names, _contents = archive
    basenames = {n.rsplit("/", 1)[-1] for n in names}
    missing = [
        (node["title"], att["title"], att["dataFileName"])
        for node in walk(root)
        for att in node.get("attachments", [])
        if att["dataFileName"] not in basenames
    ]
    assert missing == []


def test_the_plugin_ships_attachments_at_all(root):
    """Guards the test above from passing because the loop found nothing."""
    total = sum(len(n.get("attachments", [])) for n in walk(root))
    assert total > 0


def test_no_archive_member_is_orphaned(archive, root):
    """The reverse direction: a file nobody declares is dead weight, and usually
    a sign that a note was removed from TREE but its source file was not."""
    _meta, names, _contents = archive
    declared = {n["dataFileName"] for n in walk(root) if "dataFileName" in n}
    declared |= {
        att["dataFileName"] for n in walk(root) for att in n.get("attachments", [])
    }
    orphans = [
        n for n in names
        if not n.endswith("/") and n != "!!!meta.json" and n.rsplit("/", 1)[-1] not in declared
    ]
    assert orphans == []


def test_every_note_with_children_ships_a_content_file(root):
    """A parent that contributes no archive member is a parent Trilium never
    creates.

    This one shipped: the archive holds no directory entries, so a note is only
    created from its `dataFileName`. **Documentation** and **Example
    Presentation** had children but no file of their own, and the import died on
    their first child with `Parent note 'xHqd4KJi3wPo' was not found.` — a fresh,
    Trilium-generated id every attempt, which is what made it look like a
    problem with the target note rather than with the zip.
    """
    childless = [
        node["title"] for node in walk(root)
        if node.get("children") and "dataFileName" not in node
    ]
    assert childless == []


def test_the_builder_refuses_a_container_without_a_file():
    """Guards the rule at its source, so a new TREE entry cannot reintroduce it."""
    broken = {"title": "Orphan Maker", "mime": bz.HTML,
              "kids": [{"title": "Kid", "mime": bz.HTML,
                        "file": "assets/container-html/Themes.html"}]}
    with zipfile.ZipFile(io.BytesIO(), "w") as zf, pytest.raises(ValueError, match="Orphan Maker"):
        bz.build(broken, zf, [], [], "", 10)


def test_every_source_file_referenced_by_the_tree_exists():
    """Catches a renamed or deleted source file before a build drops its note."""
    missing = [
        node["file"] for node in walk_tree(bz.TREE)
        if "file" in node and not (REPO / node["file"]).exists()
    ]
    assert missing == []


def test_every_attachment_source_exists():
    missing = [
        src for node in walk_tree(bz.TREE)
        for _title, src in node.get("attach", [])
        if not (REPO / src).exists()
    ]
    assert missing == []


def test_note_count_matches_the_declaration(root):
    assert len(list(walk(root))) == len(list(walk_tree(bz.TREE)))


# ── labels survive into the manifest — the bug this file exists for ──────────

def test_every_declared_label_survives_into_the_manifest(root):
    """Compare TREE against the emitted manifest, note by note.

    A label declared and not emitted is exactly what shipped before: the note
    arrives, looks right in the tree, and is invisible to the tool that resolves
    it by label.
    """
    emitted = {path: labels(node) for path, node in walk_paths(root)}
    for path, declared in walk_tree_paths(bz.TREE):
        where = " → ".join(path)
        assert path in emitted, f"note declared but not emitted: {where}"
        for name, value in declared.get("label", {}).items():
            assert name in emitted[path], f"{where}: label #{name} was lost"
            assert emitted[path][name] == value, f"{where}: #{name} value changed"


def test_the_widget_note_carries_the_widget_label(root):
    widget = find(root, "Widget")
    assert "widget" in labels(widget)
    assert widget["mime"] == "application/javascript;env=frontend"
    assert widget["type"] == "code"


def test_slide_format_note_carries_the_full_notecast_contract(root):
    """The one note two repos share: the presenter documents the slide format for
    humans, the MCP reads the same note as its authoring instructions. Losing any
    of these labels is the exact failure that shipped."""
    note = find(root, "Slide Format")
    got = labels(note)

    assert got["notecastType"] == "slide"
    assert got["notecastTargetType"] == "code"
    assert got["notecastMime"] == "text/x-markdown"
    assert got["notecastApplyLabels"] == "slideType=content"
    assert got["notecastPrefix"] == "Folie"
    # Legacy label, kept until the MCP is proven end to end.
    assert "presenterSlideFormat" in got


def test_the_slide_format_note_declares_its_own_attributes():
    """The labels are parsed out of the note's `## Attributes` table, so the
    note humans copy is the note that says what it carries."""
    declared = bz.attributes(REPO / "docs/slide-format.md")
    assert declared["notecastType"] == "slide"
    assert declared["presenterSlideFormat"] == ""


def test_the_manifest_labels_are_what_the_note_declares(root):
    """The other end of the parse.

    `test_slide_format_note_carries_the_full_notecast_contract` asserts the
    values a reader would expect; this one asserts they came from the note
    itself, which is what makes it the single source.
    """
    assert labels(find(root, "Slide Format")) == bz.attributes(REPO / "docs/slide-format.md")


@pytest.mark.parametrize("table,complaint", [
    ("| `#presenterTypo` | `x` |", "unknown label"),
    ("| `#notecastType` | `x` |\n| `#notecastType` | `y` |", "declared twice"),
    ("| `#notecastTargetType` | `code` |", "nothing defines the id"),
    ("| `#notecastType` | `x` |\n| `#notecastTargetType` | `binary` |", "not text|code"),
    ("| `#notecastType` | `x` |\n| `#notecastMime` | `text/x-markdown` |",
     "on a text type is never read"),
    ("| `#notecastType` | `x` |\n| `#notecastTargetType` | `code` |", "code type needs"),
    ("| notecastType | x |", "cannot read attribute row"),
])
def test_a_broken_attributes_table_fails_the_build(tmp_path, table, complaint):
    """Every one of these is stored by Trilium without complaint and only shows
    up later, as a slide created in the wrong shape — so the build has to be the
    thing that refuses."""
    md = tmp_path / "broken.md"
    md.write_text(f"# Broken\n\n## Attributes\n\n| Label | Value |\n|---|---|\n{table}\n")
    with pytest.raises(ValueError, match=re.escape(complaint)):
        bz.attributes(md)


def test_a_note_without_an_attributes_section_fails_the_build(tmp_path):
    md = tmp_path / "silent.md"
    md.write_text("# Silent\n\nA format that never says what it is.\n")
    with pytest.raises(ValueError, match="no '## Attributes' section"):
        bz.attributes(md)


def test_exactly_one_note_claims_the_slide_type(root):
    """Two notes carrying #notecastType=slide make the MCP refuse as ambiguous —
    so the plugin must never ship a second one."""
    claimants = [n["title"] for n in walk(root) if labels(n).get("notecastType") == "slide"]
    assert claimants == ["Slide Format"]


def test_themes_are_discoverable(root):
    themes = [n for n in walk(root) if "presenterTheme" in labels(n)]
    assert {t["title"] for t in themes} == {"Default", "Dark"}


def test_each_theme_ships_every_slide_role(root):
    """A theme missing a role renders that slide type unstyled."""
    required = {"Base", "Title Slide", "Content Slide", "Chapter Slide"}
    for theme in (n for n in walk(root) if "presenterTheme" in labels(n)):
        got = {kid["title"] for kid in theme.get("children", [])}
        assert required <= got, f"{theme['title']} is missing {required - got}"
        for kid in theme["children"]:
            assert kid["mime"] == "text/css", kid["title"]


def test_templates_are_discoverable_and_typed(root):
    """Every template names its slideType. Without one the widget applies a
    fallback, and it has two that disagree: in a deck the first slide becomes
    `title`, in the single-slide view everything is `content`. A note made from
    the Agenda template then rendered differently depending on how it was opened."""
    templates = [n for n in walk(root) if "template" in labels(n)]
    assert len(templates) == 11
    for tmpl in templates:
        assert tmpl["mime"] == "text/x-markdown", tmpl["title"]
        assert labels(tmpl).get("slideType"), f"{tmpl['title']}: no slideType"


def test_slide_type_values_are_ones_the_widget_renders(root):
    """`slideType` becomes a CSS class (`${type}-slide`), so an unknown value is
    a slide that silently falls back to unstyled."""
    known = {"title", "content", "chapter"}
    for node in walk(root):
        value = labels(node).get("slideType")
        if value:
            assert value in known, f"{node['title']}: unknown slideType {value!r}"


def test_no_note_ships_a_notecast_theme_label(root):
    """`#notecastTheme` is the render plugin's namespace — the presenter's
    on-screen themes are `#presenterTheme`. Mixing them would make the renderer
    offer on-screen themes for printing."""
    assert not [n["title"] for n in walk(root) if "notecastTheme" in labels(n)]


# ── version stamping ─────────────────────────────────────────────────────────

def test_root_note_carries_the_build_version(root):
    assert labels(root)["version"] == TEST_VERSION


def test_version_defaults_to_dev():
    with zipfile.ZipFile(build("dev")) as zf:
        meta = json.loads(zf.read("!!!meta.json"))
    assert labels(meta["files"][0])["version"] == "dev"


# ── file naming ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("title,expected", [
    ("Simple", "Simple"),
    ("A & B", "A and B"),
    # `?` is illegal on Windows, so a zip carrying it cannot be unpacked there.
    ("What?", "What"),
    ("a/b", "ab"),
    ('q"uote', "quote"),
    ("a<b>c:d|e*f", "abcdef"),
    ("  spaced   out  ", "spaced out"),
])
def test_safe_name(title, expected):
    assert bz.safe_name(title) == expected


def test_no_two_siblings_collide_into_one_file_name():
    """Two titles differing only in stripped characters would overwrite each
    other inside the archive, silently losing a note."""
    def check(node, path="root"):
        kids = node.get("kids", [])
        names = [bz.safe_name(k["title"]) for k in kids]
        assert len(names) == len(set(names)), f"collision under {path}: {names}"
        for kid in kids:
            check(kid, f"{path}/{kid['title']}")

    check(bz.TREE)


def test_archive_holds_no_windows_hostile_paths(archive):
    _meta, names, _contents = archive
    for name in names:
        assert not set(name) & set('<>:"\\|?*'), name


# ── determinism ──────────────────────────────────────────────────────────────

def test_note_ids_are_stable_and_unique(root):
    """Ids are derived from the note path, so a rebuild must not churn them."""
    with zipfile.ZipFile(build("v1")) as zf:
        ids_a = [n["noteId"] for n in walk(json.loads(zf.read("!!!meta.json"))["files"][0])]
    with zipfile.ZipFile(build("v2")) as zf:
        ids_b = [n["noteId"] for n in walk(json.loads(zf.read("!!!meta.json"))["files"][0])]

    assert ids_a == ids_b
    assert len(ids_a) == len(set(ids_a)), "note ids must be unique within the tree"


def test_attachment_ids_are_unique(root):
    ids = [att["attachmentId"] for n in walk(root) for att in n.get("attachments", [])]
    assert len(ids) == len(set(ids))
