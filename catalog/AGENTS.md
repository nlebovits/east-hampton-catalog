# AGENTS.md: Town of East Hampton, NY GIS Layers

Guidance for AI agents and automated clients that work with this catalog.

**One rule survives every edit to this file.** Every claim here is quoted from
a source or measured from the data. If you cannot point at where a fact came
from, it does not belong in this file.

## What this catalog holds

The catalog mirrors 38 layers of the Town of East Hampton, New York
[MapServiceForOpenGov](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer)
ArcGIS service, extracted on 2026-10-15. The public root is
`https://data.source.coop/portolan-mirrors/east-hampton-catalog/catalog.json`.

The Town states that the service "contains draft data that may be
incomplete". Nothing here is an official Town record. Read the
[terms](LICENSE.md) before you redistribute the data.

The catalog has six subcatalogs. Each collection holds one GeoParquet file and
one PMTiles file at `<subcatalog>/<collection>/<collection>.parquet`.

| Subcatalog | Collections |
|---|---|
| `base-layers` | town-boundary, villages, gardiners-island, municipal-boundary-lines, fire-districts, school-districts, historic-districts, waterbodies |
| `zoning` | zoning-districts, harbor-protection-overlay, water-recharge-overlay, agricultural-overlay, recreational-overlay, special-groundwater-protection-areas, groundwater-zone-v, critical-environmental-areas |
| `coastal` | coastal-erosion-overlay, ceha-line, lwrp-reaches, significant-coastal-habitats, ecological-complexes, scfwh-coastal-boundary |
| `fema-dfirm-2009` | flood-zones, limwa, cbrs-units, shoreline |
| `wetlands` | town-wetlands, watercourses, upland-areas, dec-tidal-wetlands, dec-freshwater-wetlands, nwi-wetlands |
| `conservation` | scenic-conservation-easements, protected-vegetation-buffers, trails, soils, pep-cnras, pep-boundary |

Each collection has its own `AGENTS.md` with the column meanings.

The mirror omits the Town's tax parcel layers, building footprints, and pool
points. [LICENSE.md](LICENSE.md) gives the reasons.

## How to read it

Every GeoParquet file is GeoParquet 1.1 with a `geometry` column and a `bbox`
covering column. These DuckDB queries ran against the published files.

```sql
INSTALL spatial; LOAD spatial;
SET VARIABLE base =
  'https://data.source.coop/portolan-mirrors/east-hampton-catalog';

-- Acres by zoning district (PC 13,004.2 and A5 10,412.7 lead)
SELECT Zoning, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet(getvariable('base')
  || '/zoning/zoning-districts/zoning-districts.parquet')
GROUP BY Zoning ORDER BY acres DESC;

-- Zoning acres inside the 2009 Special Flood Hazard Area.
-- The flood layer covers all of Suffolk County, so clip to the Town first.
WITH town AS (
  SELECT ST_Union_Agg(geometry) AS g
  FROM read_parquet(getvariable('base')
    || '/base-layers/town-boundary/town-boundary.parquet')
), sfha AS (
  SELECT f.geometry
  FROM read_parquet(getvariable('base')
    || '/fema-dfirm-2009/flood-zones/flood-zones.parquet') f, town
  WHERE f.SFHA_TF = 'T' AND ST_Intersects(f.geometry, town.g)
)
SELECT z.Zoning,
       round(sum(ST_Area(ST_Intersection(z.geometry, s.geometry)))
             / 43560, 1) AS sfha_acres
FROM read_parquet(getvariable('base')
  || '/zoning/zoning-districts/zoning-districts.parquet') z
JOIN sfha s ON ST_Intersects(z.geometry, s.geometry)
GROUP BY z.Zoning ORDER BY sfha_acres DESC;

-- Open trail miles by type (Hiking Trail 147.5, Dirt Road 47.9)
SELECT Trail_Type, round(sum(Miles), 1) AS miles
FROM read_parquet(getvariable('base')
  || '/conservation/trails/trails.parquet')
WHERE Trail_Stat = 'Open'
GROUP BY Trail_Type ORDER BY miles DESC;
```

## Join keys

No attribute key joins two collections. Join them on geometry, as the flood
zone query does. Every file uses the same CRS, so a spatial join needs no
transform.

`recreational-overlay.DSBL19` holds a 19-character Suffolk County tax map
number. The parcels it points to are not in this catalog.

## Quirks that produce silently wrong answers

- **The CRS is EPSG:2263, in US survey feet.** `ST_Area` returns square feet
  and `ST_Length` returns feet. Divide by 43,560 for acres and 5,280 for
  miles. Transform to EPSG:4326 before you join with longitude and latitude.
- **Blank text is a single space.** Many text columns hold `' '` where the
  source has no value, not NULL. Filter with `trim(col) = ''`.
- **The FEMA layers cover the county.** `flood-zones`, `limwa`, `cbrs-units`,
  and `shoreline` cover all of Suffolk County. Clip to `town-boundary` before
  you total anything for the Town.
- **The 2009 flood map is not current.** FEMA publishes current flood zones
  in the [National Flood Hazard Layer](https://www.fema.gov/flood-maps/national-flood-hazard-layer).
- **`Area_Sq_Ft` and `Acres` come from the Town.** They are stored values and
  can differ from an area that you compute from the geometry.
- **Zoning is not the legal zoning.** The Town states that the zoning layer
  "is not the official zoning for the Town".

## Structure

Assets and structural links resolve relative to the object that carries
them. The root catalog carries an absolute `self` link. Each collection
carries a `via` link to its source ArcGIS layer. The catalog metadata lives in
the [nlebovits/east-hampton-catalog](https://github.com/nlebovits/east-hampton-catalog)
repository.
