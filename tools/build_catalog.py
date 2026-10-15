# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=17", "pyyaml>=6", "duckdb>=1.1"]
# ///
"""Build the East Hampton catalog from a raw extraction.

The catalog has two halves. The data (GeoParquet, PMTiles) lives in a staging
directory outside git and uploads with tools/upload_data.py. The metadata
lives in catalog/ and publishes with tools/publish.py.

tools/layers.yaml is the source of truth for titles, descriptions, providers,
and column meanings. Hand-written files (styles, LICENSE.md) live in catalog/.
This script moves content between the three places:

    prepare  raw extraction + layers.yaml + catalog/ -> staging
    enrich   layers.yaml -> staging collection.json and AGENTS.md
    sync     staging catalog.json, collection.json, README.md, AGENTS.md
             and thumbnails -> catalog/

A full refresh:

    portolan extract arcgis <service> ../east-hampton-raw ...   (see README)
    uv run tools/build_catalog.py prepare
    cd ../east-hampton-staging && portolan add . --pmtiles --force
    uv run tools/build_catalog.py enrich
    cd ../east-hampton-staging && portolan readme
    uv run tools/build_catalog.py sync
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import yaml

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "tools" / "layers.yaml"
CATALOG = REPO / "catalog"
RAW = (REPO / ".." / "east-hampton-raw").resolve()
STAGING = (REPO / ".." / "east-hampton-staging").resolve()

GITHUB = "https://github.com/nlebovits/east-hampton-catalog"

# Files in catalog/ that a person writes. prepare copies them into staging so
# that portolan registers them. sync never overwrites them.
HAND_WRITTEN = ("LICENSE.md",)
HAND_WRITTEN_DIRS = ("styles",)

# Files that portolan generates in staging. sync copies them into catalog/.
GENERATED = ("catalog.json", "collection.json", "README.md", "AGENTS.md")
THUMBNAIL_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text())


def collection_dir(root: Path, col: dict) -> Path:
    return root / col["group"] / col["id"]


def raw_parquet(layer: int) -> Path:
    report = json.loads((RAW / ".portolan" / "extraction-report.json").read_text())
    for entry in report["layers"]:
        if entry["id"] == layer:
            return RAW / entry["output_path"]
    sys.exit(f"layer {layer} is not in the raw extraction report")


def providers(cfg: dict, col: dict) -> list[dict]:
    producer = dict(cfg["producers"][col["producer"]])
    result = [producer]
    if col["producer"] != "town":
        result.append(dict(cfg["town_processor"]))
    result.append(dict(cfg["host"]))
    return result


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=78))


def base_metadata(cfg: dict) -> dict:
    return {
        "contact": cfg["contact"],
        "license": "other",
        "license_url": cfg["license_url"],
    }


def clean_parquet(src: Path, dest: Path, drop: list[str]) -> list[str]:
    """Copy src to dest without the drop columns, then Hilbert-sort it.

    Returns the names of the columns removed. Skips the rewrite when dest is
    newer than src, so that a metadata-only rerun does not force a retile.
    """
    removed = [c for c in drop if c in pq.read_schema(src).names]
    if dest.exists() and dest.stat().st_mtime > src.stat().st_mtime:
        return removed
    table = pq.read_table(src)
    table = table.drop_columns(removed)
    dest.parent.mkdir(parents=True, exist_ok=True)
    unsorted = dest.with_suffix(".unsorted.parquet")
    # The schema metadata holds the GeoParquet "geo" key, so it survives.
    pq.write_table(table, unsorted, compression="zstd")
    subprocess.run(
        ["gpio", "sort", "hilbert", str(unsorted), str(dest), "--overwrite"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    unsorted.unlink()
    return removed


def prepare(cfg: dict) -> None:
    if not (STAGING / "catalog.json").exists():
        subprocess.run(
            [
                "portolan", "init", str(STAGING), "--auto",
                "--id", cfg["catalog"]["id"],
                "--title", cfg["catalog"]["title"],
                "--license", "other", "--license-url", cfg["license_url"],
            ],
            check=True,
        )

    root_meta = base_metadata(cfg) | {
        "title": cfg["catalog"]["title"],
        "description": cfg["catalog"]["description"],
        "keywords": cfg["catalog"]["keywords"],
        "providers": [cfg["producers"]["town"], cfg["host"]],
        "source_url": cfg["source_service"],
        "attribution": "Town of East Hampton, NY",
        "processing_notes": " ".join(cfg["catalog"]["processing_notes"].split()),
        "known_issues": " ".join(cfg["catalog"]["known_issues"].split()),
    }
    write_yaml(STAGING / ".portolan" / "metadata.yaml", root_meta)

    for name in HAND_WRITTEN:
        if (CATALOG / name).exists():
            shutil.copy2(CATALOG / name, STAGING / name)

    for group, sub in cfg["subcatalogs"].items():
        write_yaml(
            STAGING / group / ".portolan" / "metadata.yaml",
            base_metadata(cfg) | {
                "title": sub["title"],
                "description": " ".join(sub["description"].split()),
                "keywords": sub["keywords"],
            },
        )

    for col in cfg["collections"]:
        dest = collection_dir(STAGING, col)
        drop = cfg["drop_columns"] + col.get("drop", [])
        removed = clean_parquet(raw_parquet(col["layer"]), dest / f"{col['id']}.parquet", drop)
        layer_url = f"{cfg['source_service']}/{col['layer']}"
        notes = (
            f"Extracted from [ArcGIS layer {col['layer']}]({layer_url}) of the "
            f"Town's MapServiceForOpenGov service on {cfg['extracted']} with "
            f"`portolan extract arcgis`. Kept in the source CRS, EPSG:2263. "
            f"Removed columns that hold no data or that ArcGIS computes from "
            f"the geometry: {', '.join(removed) or 'none'}. Rows sorted on a "
            f"Hilbert curve with gpio. Built by `tools/build_catalog.py` in "
            f"[nlebovits/east-hampton-catalog]({GITHUB})."
        )
        description = (
            " ".join(col["description"].split())
            + " Read [AGENTS.md](AGENTS.md) for the column meanings and "
            "tested queries."
        )
        meta = base_metadata(cfg) | {
            "title": col["title"],
            "description": description,
            "keywords": cfg["subcatalogs"][col["group"]]["keywords"],
            "providers": providers(cfg, col),
            "source_url": layer_url,
            "attribution": cfg["producers"][col["producer"]]["name"],
            "processing_notes": notes,
        }
        if col.get("known_issues"):
            meta["known_issues"] = col["known_issues"]
        write_yaml(dest / ".portolan" / "metadata.yaml", meta)

        for sub in HAND_WRITTEN_DIRS:
            src = collection_dir(CATALOG, col) / sub
            if src.is_dir():
                shutil.copytree(src, dest / sub, dirs_exist_ok=True)
        print(f"prepared {col['group']}/{col['id']} (removed: {', '.join(removed) or '-'})")


def agents_md(cfg: dict, col: dict, stac: dict) -> str:
    """The agent guide for one collection, built from layers.yaml and the STAC."""
    rel = f"{col['group']}/{col['id']}/{col['id']}.parquet"
    url = f"https://data.source.coop/portolan-mirrors/east-hampton-catalog/{rel}"
    columns = stac.get("table:columns", [])
    rows = stac.get("table:row_count")
    lines = [
        f"# {col['title']}: agent guide",
        "",
        f"Source: ArcGIS layer [{col['layer']}]({cfg['source_service']}/{col['layer']}) "
        f"of the Town of East Hampton MapServiceForOpenGov service, "
        f"extracted {cfg['extracted']}. Producer: "
        f"{cfg['producers'][col['producer']]['name']}.",
        "",
        "## The file",
        "",
        f"- Data: `{url}`",
        f"- Rows: {rows}, one per source feature.",
        "- Geometry column: `geometry`. A `bbox` struct column supports "
        "bounding-box filters.",
        "- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. "
        "Areas and lengths computed on this geometry come out in square feet "
        "and feet. Transform to EPSG:4326 before you join with longitude and "
        "latitude data.",
        "- Blank text: many text columns hold a single space `' '` where the "
        "source has no value. Use `trim(col) = ''` to find them.",
        "",
        "## Columns",
        "",
        "| Column | Type | Meaning |",
        "|---|---|---|",
    ]
    for c in columns:
        if c["name"] in ("geometry", "bbox"):
            continue
        desc = " ".join(str(c.get("description", "")).split()).replace("|", "\\|")
        lines.append(f"| `{c['name']}` | {c.get('type', '')} | {desc} |")
    if col.get("known_issues"):
        lines += ["", "## Known issues", "", " ".join(col["known_issues"].split())]
    if "Line" in stac.get("geoparquet:geometry_type", ""):
        measure = ("Total length in miles. The CRS unit is the US survey foot.",
                   "round(sum(ST_Length(geometry)) / 5280, 1) AS miles")
    else:
        measure = ("Total area in acres. The CRS unit is the US survey foot.",
                   "round(sum(ST_Area(geometry)) / 43560, 1) AS acres")
    lines += [
        "",
        "## Query with DuckDB",
        "",
        "```sql",
        "INSTALL spatial; LOAD spatial;",
        "",
        f"-- Row count. {measure[0]}",
        f"SELECT count(*) AS n, {measure[1]}",
        f"FROM read_parquet('{url}');",
    ]
    for recipe in col.get("recipes", []):
        lines += ["", f"-- {recipe['title']}", recipe["sql"].strip().replace("{url}", url) ]
    lines += ["```", ""]
    lines += [
        "The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout "
        "and the [terms](../../LICENSE.md).",
        "",
    ]
    return "\n".join(lines)


def enrich(cfg: dict) -> None:
    for col in cfg["collections"]:
        path = collection_dir(STAGING, col) / "collection.json"
        stac = json.loads(path.read_text())
        meanings = col.get("columns", {})
        for c in stac.get("table:columns", []):
            if c["name"] in meanings:
                c["description"] = " ".join(meanings[c["name"]].split())
            elif c["name"] == "geometry":
                c["description"] = "Feature geometry in EPSG:2263 (US survey feet)."
            elif c["name"] == "bbox":
                c["description"] = "Bounding box of the geometry, for spatial filters."
        missing = [
            c["name"] for c in stac.get("table:columns", []) if not c.get("description")
        ]
        if missing:
            sys.exit(f"{col['id']}: no description for {missing} in layers.yaml")
        path.write_text(json.dumps(stac, indent=2) + "\n")
        (path.parent / "AGENTS.md").write_text(agents_md(cfg, col, stac))
        print(f"enriched {col['group']}/{col['id']}")

    root = STAGING / "catalog.json"
    stac = json.loads(root.read_text())
    keep = [l for l in stac["links"] if l["rel"] not in ("self", "vcs", "issues")]
    keep += [
        {
            "rel": "self",
            "href": "https://data.source.coop/portolan-mirrors/east-hampton-catalog/catalog.json",
            "type": "application/json",
        },
        {"rel": "vcs", "href": GITHUB, "title": "Source repository"},
        {"rel": "issues", "href": f"{GITHUB}/issues", "title": "Issue tracker"},
    ]
    stac["links"] = keep
    root.write_text(json.dumps(stac, indent=2) + "\n")
    shutil.copy2(CATALOG / "AGENTS.md", STAGING / "AGENTS.md")
    print("enriched catalog.json links")


def sync(cfg: dict) -> None:
    for path in sorted(STAGING.rglob("*")):
        rel = path.relative_to(STAGING)
        if any(part.startswith(".") for part in rel.parts) or not path.is_file():
            continue
        is_generated = path.name in GENERATED
        is_thumbnail = path.suffix.lower() in THUMBNAIL_SUFFIXES
        if not (is_generated or is_thumbnail):
            continue
        # The root AGENTS.md is hand-written in catalog/.
        if rel == Path("AGENTS.md"):
            continue
        dest = CATALOG / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    print(f"synced generated metadata into {CATALOG}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=["prepare", "enrich", "sync"])
    args = parser.parse_args()
    cfg = load_config()
    {"prepare": prepare, "enrich": enrich, "sync": sync}[args.stage](cfg)


if __name__ == "__main__":
    main()
