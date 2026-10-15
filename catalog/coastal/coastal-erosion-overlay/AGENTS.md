# Coastal Erosion Overlay District Zones: agent guide

Source: ArcGIS layer [13](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/13) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/coastal-erosion-overlay/coastal-erosion-overlay.parquet`
- Rows: 478, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `Zone` | int16 | Coastal Erosion Overlay District zone. 1 is the ocean littoral zone, mostly free of erosion control structures. 2 is the bay littoral zone, mostly free of erosion control structures. 3 is the bay littoral zone with isolated erosion control structures. 4 is the bay littoral zone with numerous erosion control structures. |
| `Object_ID` | int64 | A second object ID from the source. Its origin is not published. |
| `ZoneSheets` | string | Map sheet number, as text. The source does not name the map series. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total length in miles. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Length(geometry)) / 5280, 1) AS miles
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/coastal-erosion-overlay/coastal-erosion-overlay.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
