# Recreational Overlay District: agent guide

Source: ArcGIS layer [68](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/68) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/zoning/recreational-overlay/recreational-overlay.parquet`
- Rows: 1, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `BTCAMP` | double | Unlabeled number from the source, 4. The meaning is not published. |
| `ZONING` | string | Underlying use district code, A5. |
| `ROD` | double | Unlabeled number from the source, 1. The meaning is not published. |
| `DSBL19` | string | Suffolk County tax map number (district, section, block, lot) as a 19-character string. |

## Known issues

The source publishes no meaning for BTCAMP or ROD.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/zoning/recreational-overlay/recreational-overlay.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
