# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "duckdb>=1.1"]
# ///
"""Check every style's match values against the staged data.

A legend that lists a category the data does not hold misleads the reader.
This check fails on any match value with no rows. It reports, without
failing, populated values that the match leaves to the fallback color.

    uv run tools/check_styles.py [STAGING]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import yaml

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "catalog"


def matches(node):
    """Yield (input expression, values) for every match expression in node."""
    if isinstance(node, list):
        if node and node[0] == "match":
            values = [node[i] for i in range(2, len(node) - 1, 2)]
            yield node[1], values
        for child in node:
            yield from matches(child)
    elif isinstance(node, dict):
        for child in node.values():
            yield from matches(child)


def sql_input(expr) -> str:
    if expr[0] == "get":
        return f'"{expr[1]}"'
    if expr[0] == "slice" and expr[1][0] == "get":
        return f'substr("{expr[1][1]}", {expr[2] + 1}, {expr[3] - expr[2]})'
    raise ValueError(f"unsupported match input {expr}")


def main() -> int:
    staging = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / "east-hampton-staging"
    cfg = yaml.safe_load((REPO / "tools" / "layers.yaml").read_text())
    con = duckdb.connect()
    failed = False
    for col in cfg["collections"]:
        data = staging / col["group"] / col["id"] / f"{col['id']}.parquet"
        for path in sorted((CATALOG / col["group"] / col["id"] / "styles").glob("*.json")):
            body = json.loads(path.read_text())
            for expr, values in matches(body["layers"]):
                column = sql_input(expr)
                rows = dict(con.execute(
                    f"SELECT CAST({column} AS VARCHAR), count(*) "
                    f"FROM read_parquet('{data}') GROUP BY 1"
                ).fetchall())
                empty = [v for v in values if rows.get(str(v), 0) == 0]
                left = {k: n for k, n in rows.items()
                        if k not in {str(v) for v in values}}
                label = f"{col['id']}/{path.name} {column}"
                if empty:
                    failed = True
                    print(f"FAIL {label}: no rows for {empty}")
                else:
                    print(f"ok   {label}: {len(values)} values")
                if left:
                    print(f"     fallback color draws {left}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
