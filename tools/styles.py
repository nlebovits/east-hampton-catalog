# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Write the MapLibre styles for every collection into catalog/.

Each collection gets styles/default.json. A collection with a second reading
of its data also gets a named style. The default style carries the `default`
role when portolan registers it.

The data browser draws a legend only from a fill or circle layer whose color
is a `match` or `step` expression. Every match value below was checked
against the data. See the style plan in catalog/AGENTS.md.

    uv run tools/styles.py
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "catalog"

# Fill styles with a categorical legend: column, then value -> color pairs.
CATEGORICAL_FILLS = {
    "zoning-districts": ("Zoning", "Use district", [
        ("A10", "#fff7bc"), ("A5", "#fee391"), ("A3", "#fec44f"),
        ("A2", "#fe9929"), ("A", "#ec7014"), ("B", "#cc4c02"),
        ("MF", "#8c2d04"), ("CB", "#b2182b"), ("NB", "#d6604d"),
        ("RS", "#f4a582"), ("CS", "#c51b7d"), ("CI", "#762a83"),
        ("WF", "#2166ac"), ("PC", "#1b7837"),
    ]),
    "flood-zones": ("FLD_ZONE", "Flood zone", [
        ("VE", "#08306b"), ("V", "#2171b5"), ("AE", "#4292c6"),
        ("A", "#6baed6"), ("AO", "#9ecae1"),
        ("0.2 PCT ANNUAL CHANCE FLOOD HAZARD", "#deebf7"),
        ("OPEN WATER", "#a6bddb"),
    ]),
    "dec-tidal-wetlands": ("TWCAT74", "Tidal wetland category", [
        ("IM", "#1b7837"), ("HM", "#5aae61"), ("FM", "#a6dba0"),
        ("FC", "#c2a5cf"), ("SM", "#dfc27d"), ("LZ", "#deebf7"),
        ("AA", "#d9d9d9"), ("DS", "#8c510a"), ("HL", "#f7f7f7"),
    ]),
    "dec-freshwater-wetlands": ("CLASS", "Freshwater wetland class", [
        ("1", "#01665e"), ("2", "#35978f"), ("3", "#80cdc1"), ("0", "#c7eae5"),
    ]),
    "soils": ("MUSYM", "Soil map unit", [
        ("BgA", "#8c6d31"), ("BgB", "#bd9e39"), ("BhB", "#e7cb94"),
        ("MkA", "#637939"), ("MkB", "#8ca252"), ("MfA", "#b5cf6b"),
        ("MfB", "#cedb9c"), ("HaA", "#843c39"), ("HaB", "#ad494a"),
        ("He", "#d6616b"), ("PsA", "#e7ba52"), ("RdA", "#7b4173"),
        ("RdB", "#a55194"), ("ScB", "#5254a3"), ("SdA", "#6b6ecf"),
        ("SdB", "#9c9ede"), ("Su", "#de9ed6"),
    ]),
    "cbrs-units": ("CBRS_Type", "CBRS unit type", [
        ("System Unit", "#e6550d"), ("Otherwise Protected Area", "#9e9ac8"),
    ]),
    "fire-districts": ("Fire_Dist_Name", "Fire district", [
        ("Amagansett Fire", "#4e79a7"), ("Bridgehampton Fire", "#f28e2b"),
        ("East Hampton Road Fire Protection", "#e15759"),
        ("East Hampton Water Supply", "#76b7b2"), ("Montauk Fire", "#59a14f"),
        ("Montauk Fire Protection", "#edc948"),
        ("Northwest Fire Protection", "#b07aa1"),
        ("Promised Land Fire Protection", "#ff9da7"), ("Springs Fire", "#9c755f"),
    ]),
    "school-districts": ("ID", "School district", [
        ("AMAGANSETT SD", "#66c2a5"), ("EAST HAMPTON SD", "#fc8d62"),
        ("MONTAUK SD", "#8da0cb"), ("SPRINGS SD", "#e78ac3"),
        ("WAINSCOTT SD", "#a6d854"),
    ]),
    "historic-districts": ("Historic_District", "Historic district", [
        ("Amagansett", "#a6611a"), ("Bluff Road", "#dfc27d"),
        ("Montauk", "#80cdc1"), ("Springs", "#018571"),
    ]),
    "villages": ("Village", "Village", [
        ("East Hampton Village", "#d53e4f"), ("Sag Harbor Village", "#5e4fa2"),
    ]),
    # The fallback color draws the 19 State habitats. The legend lists the
    # five locally significant habitats by name.
    "significant-coastal-habitats": ("LOCALLYSIG", "Locally significant habitat", [
        ("THREE MILE HARBOR", "#c7e9c0"), ("GEORGICA POND", "#a1d99b"),
        ("WAINSCOTT POND", "#74c476"),
        ("FRESH POND BELL ESTATE WETLAND", "#d9f0a3"),
        ("MONTAUK POINT", "#addd8e"),
    ]),
    "critical-environmental-areas": ("AGENCY", "Designating agency", [
        ("Suffolk County", "#fdae6b"), ("Long Island Regional Planning", "#9ecae1"),
        ("East Hampton, Town of", "#a1d99b"),
    ]),
    "lwrp-reaches": ("ID", "LWRP reach", [
        (f"REACH {n}", c) for n, c in zip(range(1, 13), [
            "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462",
            "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f",
        ])
    ]),
}

# Fallback fill for features whose value is not in the match list.
FALLBACK = {"significant-coastal-habitats": "#238b45"}

# Categorical line styles. The browser draws no legend for a line layer.
CATEGORICAL_LINES = {
    "coastal-erosion-overlay": ("Zone", "Erosion zone", [
        (1, "#d73027"), (2, "#fc8d59"), (3, "#91bfdb"), (4, "#4575b4"),
    ]),
    "trails": ("Trail_Type", "Trail type", [
        ("Hiking Trail", "#1a9850"), ("Dirt Road", "#a6761d"),
        ("Woods Dirt Road", "#8c510a"), ("Paved Road", "#636363"),
        ("Paved Path", "#969696"), ("Old Road", "#bf812d"),
        ("MV Trail", "#d95f02"), ("Horse Trail", "#7570b3"), ("Other", "#e7298a"),
    ]),
}

SINGLE_FILLS = {
    "town-boundary": ("#d4b483", "#5c4a32", 0.6),
    "gardiners-island": ("#74c476", "#00441b", 0.65),
    "waterbodies": ("#6baed6", "#2171b5", 0.8),
    "harbor-protection-overlay": ("#8c96c6", "#6e016b", 0.6),
    "water-recharge-overlay": ("#7fcdbb", "#225ea8", 0.55),
    "agricultural-overlay": ("#78c679", "#238443", 0.8),
    "recreational-overlay": ("#fdbb84", "#d7301f", 0.8),
    "special-groundwater-protection-areas": ("#6baed6", "#08519c", 0.45),
    "groundwater-zone-v": ("#41ab5d", "#006d2c", 0.45),
    "town-wetlands": ("#41ae76", "#005824", 0.8),
    "upland-areas": ("#bf812d", "#8c510a", 0.85),
    "scenic-conservation-easements": ("#74c476", "#006d2c", 0.8),
    "protected-vegetation-buffers": ("#31a354", "#00441b", 0.9),
    "pep-boundary": ("#6baed6", "#3182bd", 0.35),
    "pep-cnras": ("#fc9272", "#cb181d", 0.6),
}

SINGLE_LINES = {
    "ceha-line": ("#e31a1c", 2.0, None),
    "limwa": ("#ff7f00", 1.5, None),
    "shoreline": ("#08519c", 1.0, None),
    "watercourses": ("#2171b5", 2.5, None),
    "municipal-boundary-lines": ("#252525", 3.0, [3, 1.5]),
    "ecological-complexes": ("#31a354", 2.0, None),
    "scfwh-coastal-boundary": ("#006d2c", 2.0, [3, 2]),
}

# Second styles: collection -> (file stem, title, column, label, pairs, kind).
EXTRA = {
    "flood-zones": ("sfha", "Special Flood Hazard Area", "SFHA_TF",
                    "In a Special Flood Hazard Area (T) or not (F)",
                    [("T", "#d7301f"), ("F", "#d9d9d9")], "fill"),
    "trails": ("status", "Trail status", "Trail_Stat", "Trail status",
               [("Open", "#1a9850"), ("Closed", "#d73027"),
                ("NotPublic", "#fdae61"), ("Proposed", "#4575b4"),
                ("Trial", "#74add1"), ("Other", "#969696")], "line"),
}

# NWI: color by Cowardin system, the first letter of ATTRIBUTE. The Marine
# polygons are large open-water blocks, so they get the palest blue and the
# wetlands stay visible over them.
NWI_SYSTEMS = [
    ("P", "#238b45"), ("E", "#2b8cbe"), ("M", "#deebf7"),
    ("L", "#9ecae1"), ("R", "#6baed6"), ("U", "#d9d9d9"),
]


def style(name: str, description: str, layers: list[dict]) -> dict:
    return {
        "version": 8,
        "name": name,
        "metadata": {"description": description},
        "sources": {"data": {"type": "vector"}},
        "layers": layers,
    }


def match(input_expr, pairs, fallback):
    expr = ["match", input_expr]
    for value, color in pairs:
        expr += [value, color]
    return expr + [fallback]


def fill_layers(layer: str, color, outline: str, opacity: float = 0.75) -> list[dict]:
    return [
        {
            "id": f"{layer}-fill",
            "type": "fill",
            "source": "data",
            "source-layer": layer,
            "paint": {"fill-color": color, "fill-opacity": opacity},
        },
        {
            "id": f"{layer}-outline",
            "type": "line",
            "source": "data",
            "source-layer": layer,
            "paint": {"line-color": outline, "line-width": 0.6, "line-opacity": 0.8},
        },
    ]


def line_layers(layer: str, color, width: float, dash=None) -> list[dict]:
    paint = {"line-color": color, "line-width": width}
    if dash:
        paint["line-dasharray"] = dash
    return [{
        "id": f"{layer}-line",
        "type": "line",
        "source": "data",
        "source-layer": layer,
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": paint,
    }]


def build(cid: str, title: str) -> dict[str, dict]:
    """Return {file stem: style} for one collection."""
    out: dict[str, dict] = {}
    if cid in CATEGORICAL_FILLS:
        column, label, pairs = CATEGORICAL_FILLS[cid]
        color = match(["get", column], pairs, FALLBACK.get(cid, "#bdbdbd"))
        out["default"] = style(
            f"{title} by {label.lower()}",
            f"Fill color shows the `{column}` column. See the column "
            f"description for the meaning of each code.",
            fill_layers(cid, color, "#ffffff"),
        )
    elif cid in CATEGORICAL_LINES:
        column, label, pairs = CATEGORICAL_LINES[cid]
        color = match(["get", column], pairs, "#bdbdbd")
        out["default"] = style(
            f"{title} by {label.lower()}",
            f"Line color shows the `{column}` column.",
            line_layers(cid, color, 1.6),
        )
    elif cid == "nwi-wetlands":
        color = match(["slice", ["get", "ATTRIBUTE"], 0, 1], NWI_SYSTEMS, "#bdbdbd")
        out["default"] = style(
            f"{title} by Cowardin system",
            "Fill color shows the first letter of `ATTRIBUTE`: P Palustrine, "
            "E Estuarine, M Marine, L Lacustrine, R Riverine, U undefined.",
            fill_layers(cid, color, "#ffffff"),
        )
    elif cid in SINGLE_FILLS:
        fill, outline, opacity = SINGLE_FILLS[cid]
        out["default"] = style(title, f"{title} in one color.",
                               fill_layers(cid, fill, outline, opacity))
    elif cid in SINGLE_LINES:
        color, width, dash = SINGLE_LINES[cid]
        out["default"] = style(title, f"{title} in one color.",
                               line_layers(cid, color, width, dash))
    else:
        raise SystemExit(f"no style defined for {cid}")

    if cid in EXTRA:
        stem, name, column, label, pairs, kind = EXTRA[cid]
        color = match(["get", column], pairs, "#bdbdbd")
        layers = (fill_layers(cid, color, "#ffffff") if kind == "fill"
                  else line_layers(cid, color, 1.6))
        out[stem] = style(f"{title}: {name.lower()}",
                          f"Color shows the `{column}` column. {label}.", layers)
    return out


def main() -> None:
    cfg = yaml.safe_load((REPO / "tools" / "layers.yaml").read_text())
    for col in cfg["collections"]:
        target = CATALOG / col["group"] / col["id"] / "styles"
        target.mkdir(parents=True, exist_ok=True)
        for stem, body in build(col["id"], col["title"]).items():
            (target / f"{stem}.json").write_text(json.dumps(body, indent=2) + "\n")
        print(f"styles {col['group']}/{col['id']}")


if __name__ == "__main__":
    main()
