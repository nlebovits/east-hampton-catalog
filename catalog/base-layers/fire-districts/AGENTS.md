# Fire Districts: agent guide

Source: ArcGIS layer [9](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/9) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/base-layers/fire-districts/fire-districts.parquet`
- Rows: 11, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `ID` | string | District number, 10 to 18, as the source records it. |
| `Fire_Dist_Name` | string | District name. |
| `Area_Sq_Ft` | double | Area in square feet, as the Town computed it. |
| `Acres` | double | Area in acres, as the Town computed it. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/base-layers/fire-districts/fire-districts.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
