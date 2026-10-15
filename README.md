# East Hampton, NY catalog

The metadata for a [Portolan](https://www.portolan-sdi.org/) mirror of 38
layers from the Town of East Hampton, New York
[MapServiceForOpenGov](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer)
ArcGIS service. The catalog is published on Source Cooperative at
[portolan-mirrors/east-hampton-catalog](https://source.coop/portolan-mirrors/east-hampton-catalog).

The layers cover zoning and overlay districts, wetlands, coastal management
areas, the 2009 FEMA flood map, trails, and conservation easements. Each layer
is a GeoParquet file in EPSG:2263 with PMTiles, MapLibre styles, and a
thumbnail. [catalog/LICENSE.md](catalog/LICENSE.md) records the source terms
and the layers this mirror leaves out.

**`catalog/` is the published catalog.** Everything in it is published.
Everything outside it never is.

## Three kinds of file

| Kind | Where | Example |
|---|---|---|
| Tracked and published | inside `catalog/` | STAC JSON, `README.md`, `AGENTS.md`, styles, thumbnails |
| Tracked, never published | outside `catalog/` | `tools/`, `tests/`, `docs/`, this README, `catalog.publish.yaml` |
| Neither | gitignored, in `../east-hampton-staging` | GeoParquet, PMTiles |

## Where each part comes from

| File | Source | Edit |
|---|---|---|
| Titles, descriptions, providers, column meanings | `tools/layers.yaml` | Yes |
| `catalog/**/styles/*.json` | `tools/styles.py` | Edit the script |
| `catalog/AGENTS.md`, `catalog/LICENSE.md` | Hand-written | Yes |
| `collection.json`, `catalog.json`, `README.md`, collection `AGENTS.md` | `portolan` and `tools/build_catalog.py` | No. Regenerate them |
| Thumbnails | chiitiler, framed per `tools/thumbnails.tsv` | Re-render them |

## Refresh from the source

The commands run from the parent of this repository. They need
[portolan-cli](https://github.com/portolan-sdi/portolan-cli) 0.8.0, gpio,
tippecanoe, DuckDB, and uv.

1. Extract the layers into `east-hampton-raw`. Pass list positions to
   `--layers`, because of
   [portolan-cli#1003](https://github.com/portolan-sdi/portolan-cli/issues/1003).
   ```bash
   portolan extract arcgis \
     https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer \
     east-hampton-raw --auto --id east-hampton-catalog \
     --license other \
     --license-url https://source.coop/portolan-mirrors/east-hampton-catalog/LICENSE.md \
     --layers 0,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,28,32,35,36,38,39,40,43,45,46,55,56,57
   ```
2. Write the styles, check them against the data, and build the staging tree.
   ```bash
   cd east-hampton-catalog
   uv run tools/styles.py
   uv run tools/build_catalog.py prepare
   uv run tools/check_styles.py
   ```
3. Register the files and generate the tiles.
   ```bash
   cd ../east-hampton-staging
   portolan add . --pmtiles --force --no-thumbnails
   ```
4. Write the column descriptions and the agent guides, then the READMEs.
   ```bash
   cd ../east-hampton-catalog
   uv run tools/build_catalog.py enrich
   cd ../east-hampton-staging
   portolan readme
   ```
5. Render the thumbnails with the `portolan-thumbnails` skill and the frames in
   `tools/thumbnails.tsv`. Then refresh the checksums.
   ```bash
   portolan check --fix
   portolan check
   ```
6. Copy the generated metadata into `catalog/` and run the gates.
   ```bash
   cd ../east-hampton-catalog
   uv run tools/build_catalog.py sync
   python3 tests/run_all.py
   ```

## Publish

Uploads go through the `data.source.coop` gateway with the
`source-coop-proxy` AWS profile. Each script is a dry run until you pass
`--confirm`.

```bash
source-coop login
python3 tools/upload_data.py
python3 tools/upload_data.py --confirm
python3 tools/publish.py
python3 tools/publish.py --confirm
```

## Gates

`python3 tests/run_all.py` runs the link check, the publish and upload
contracts, STAC validation, and `rashid` conformance. CI runs the same gates
with `CI_LIGHT=1`, which skips the data files that are not in git.
