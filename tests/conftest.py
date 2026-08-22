"""Shared fixtures for the build tests.

`build-zip.py` has a hyphen in its name, so it cannot be imported normally —
importlib loads it by path instead. It is a script, not a module, and renaming it
would break the release workflow and every README that names it.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
ZIP_NAME = "trilium-presenter-plugin.zip"
TEST_VERSION = "v9.9.9-test"


def _load_build_script():
    spec = importlib.util.spec_from_file_location("build_zip", REPO / "build-zip.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {REPO / 'build-zip.py'}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bz = _load_build_script()


def build(version: str) -> pathlib.Path:
    """Run the real script and return the archive it wrote."""
    # Our own build script, run with this interpreter — no shell, no external input.
    subprocess.run(  # noqa: S603
        [sys.executable, str(REPO / "build-zip.py"), version],
        cwd=REPO, check=True, capture_output=True,
    )
    return REPO / ZIP_NAME


@pytest.fixture(scope="session", autouse=True)
def leave_a_dev_build_behind():
    """The script always writes into the repo, so restore a sanely-stamped
    archive afterwards rather than leaving a test version lying around."""
    yield
    build("dev")


@pytest.fixture(scope="session")
def archive():
    """The built archive, copied out of the repo so later builds cannot disturb it."""
    built = build(TEST_VERSION)
    copy = pathlib.Path(str(built) + ".undertest")
    copy.write_bytes(built.read_bytes())
    with zipfile.ZipFile(copy) as zf:
        meta = json.loads(zf.read("!!!meta.json"))
        names = set(zf.namelist())
        contents = {n: zf.read(n) for n in names if not n.endswith("/")}
    copy.unlink()
    return meta, names, contents


@pytest.fixture(scope="session")
def root(archive):
    meta, _names, _contents = archive
    return meta["files"][0]


def walk(node):
    """Every note in a built manifest, depth first."""
    yield node
    for child in node.get("children", []):
        yield from walk(child)


def walk_tree(node):
    """Every note in the TREE *declaration*, depth first."""
    yield node
    for kid in node.get("kids", []):
        yield from walk_tree(kid)


# Titles are not unique across the tree — "Title Slide" is both an example slide
# and a per-theme stylesheet — so anything comparing declaration against output
# has to key on the path, not the title.

def walk_paths(node, prefix=()):
    """(path, note) for a built manifest, where path is the tuple of titles."""
    path = prefix + (node["title"],)
    yield path, node
    for child in node.get("children", []):
        yield from walk_paths(child, path)


def walk_tree_paths(node, prefix=()):
    """(path, note) for the TREE declaration."""
    path = prefix + (node["title"],)
    yield path, node
    for kid in node.get("kids", []):
        yield from walk_tree_paths(kid, path)


def labels(node):
    return {a["name"]: a["value"] for a in node["attributes"]}


def find(root_node, title):
    return next(n for n in walk(root_node) if n["title"] == title)
