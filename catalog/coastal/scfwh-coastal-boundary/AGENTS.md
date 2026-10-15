# SCFWH Coastal Boundary: agent guide

Source: ArcGIS layer [20](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/20) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/scfwh-coastal-boundary/scfwh-coastal-boundary.parquet`
- Rows: 3, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |

## Known issues

The source publishes no description of these lines.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total length in miles. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Length(geometry)) / 5280, 1) AS miles
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/scfwh-coastal-boundary/scfwh-coastal-boundary.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
