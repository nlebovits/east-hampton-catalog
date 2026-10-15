#!/usr/bin/env python3
"""Every relative link and asset href resolves to a file that exists.

This catches the most common hand-edit mistake: adding a child link before the
directory it points at exists. Dependency-free and offline, so it runs in
milliseconds on a clean checkout.

CI clones the metadata and not the bytes, because .gitignore keeps data out of
git. Set CI_LIGHT=1 there. It exempts hrefs with a data suffix, in links (such
as rel:pmtiles) and in assets, and nothing else. Every structural link still
resolves. Leave CI_LIGHT unset locally. The gate then checks every href, and
it looks for a data file under data_dir from catalog.publish.yaml, which
mirrors the catalog layout.

Run: python3 tests/test_links.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from publish import load_config  # noqa: E402

config = load_config()
BASE = ROOT / config["publish_dir"]
DATA = (ROOT / config["data_dir"]).resolve() if config.get("data_dir") else None

errors: list[str] = []
skipped = 0

CI_LIGHT = os.environ.get("CI_LIGHT") == "1"
# The exemption reads the suffix and nothing else. A directory rule or a path
# prefix rule widens on its own as the catalog grows. This tuple does not.
DATA_SUFFIXES = (
    ".parquet", ".pmtiles", ".tif", ".tiff", ".copc.laz", ".laz", ".gpkg",
    ".zarr", ".geojsonl", ".shp", ".zip",
)


def is_remote(href: str) -> bool:
    return "://" in href or href.startswith(("#", "mailto:"))


def is_unpublished_data(href: str) -> bool:
    """True when href points at a file kept out of git on purpose."""
    return CI_LIGHT and href.lower().endswith(DATA_SUFFIXES)


def resolves(doc_path: Path, href: str) -> bool:
    """True when href exists in the catalog, or as a staged data file."""
    target = (doc_path.parent / href).resolve()
    if target.exists():
        return True
    if DATA is None or not href.lower().endswith(DATA_SUFFIXES):
        return False
    try:
        rel = target.relative_to(BASE.resolve())
    except ValueError:
        return False
    return (DATA / rel).exists()


def stac_documents() -> list[Path]:
    """Every STAC object under the published directory."""
    out = []
    for path in sorted(BASE.rglob("*.json")):
        if any(part.startswith(".") for part in path.relative_to(BASE).parts):
            continue
        if path.name.endswith(".style.json") or "styles" in path.parts:
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
            continue
        if isinstance(doc, dict) and doc.get("type") in {
            "Catalog", "Collection", "Feature"
        }:
            out.append(path)
    return out


documents = stac_documents()
checked = 0

for path in documents:
    doc = json.loads(path.read_text())
    rel_path = path.relative_to(ROOT)

    for link in doc.get("links", []):
        href = link.get("href", "")
        if not href or is_remote(href):
            continue
        if is_unpublished_data(href):
            skipped += 1
            continue
        checked += 1
        if not resolves(path, href):
            errors.append(
                f"{rel_path}: rel:{link.get('rel')} -> {href} does not exist"
            )

    for key, asset in (doc.get("assets") or {}).items():
        href = asset.get("href", "")
        if not href or is_remote(href):
            continue
        if is_unpublished_data(href):
            skipped += 1
            continue
        checked += 1
        if not resolves(path, href):
            errors.append(f"{rel_path}: asset {key} -> {href} does not exist")

if skipped:
    print(
        f"note   {skipped} data href(s) not checked: CI_LIGHT is set and the "
        "bytes live in\n       object storage, not git. Run without CI_LIGHT "
        "locally to check them."
    )

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)

print(f"OK: {checked} relative href(s) across {len(documents)} object(s)")
