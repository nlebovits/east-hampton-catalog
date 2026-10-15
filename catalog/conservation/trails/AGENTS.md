# Trails: agent guide

Source: ArcGIS layer [43](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/43) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/conservation/trails/trails.parquet`
- Rows: 1108, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `Trail_Name` | string | Trail name. Null for 230 segments. |
| `Trail_Loca` | string | Trail location or area name. |
| `Trail_Type` | string | Trail type, for example Hiking Trail or Dirt Road. |
| `Trail_Blaz` | string | Blaze color and shape, as free text. |
| `Trail_Stat` | string | Status. Open, Closed, NotPublic, Proposed, Trial, or Other. |
| `Miles` | double | Segment length in miles. |
| `Feet` | double | Segment length in feet. |

## Known issues

Trail_Blaz is free text. It holds 91 distinct values with inconsistent spelling and some junk values.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total length in miles. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Length(geometry)) / 5280, 1) AS miles
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/conservation/trails/trails.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
