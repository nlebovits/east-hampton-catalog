# Coastal Erosion Hazard Area Line: agent guide

Source: ArcGIS layer [30](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/30) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/ceha-line/ceha-line.parquet`
- Rows: 61, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `LENGTH` | double | Segment length, as the source records it. |
| `PHOTO` | string | Photo identifier, as the source records it, for example 7-398-83. |
| `SHEET` | string | Map sheet, as the source records it, for example "1 of 59". |
| `TOWN` | string | Town name. East Hampton in every row. |
| `VILLAGE` | string | Village name. A single space outside a village. |
| `COUNTY` | string | County name. Suffolk in every row. |

## Known issues

The Town publishes no definition of this layer. The source does not name the map series behind PHOTO and SHEET, or the unit of LENGTH.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total length in miles. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Length(geometry)) / 5280, 1) AS miles
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/ceha-line/ceha-line.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
