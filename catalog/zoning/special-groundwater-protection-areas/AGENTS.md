# Special Groundwater Protection Areas: agent guide

Source: ArcGIS layer [16](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/16) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/zoning/special-groundwater-protection-areas/special-groundwater-protection-areas.parquet`
- Rows: 2, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `LOCATION` | string | Area name. South Fork or Hither Hills. |
| `NAME` | string | Designation type. The value is SGPA in both rows. |
| `AGENCY` | string | Agency, as the source records it. The value is "Long Island Regional Planning" in both rows. |
| `DATE_` | string | Date, as text in M-D-YY form. The value is 3-19-93 in both rows. |
| `REGION` | string | Region label from the source. The value is 1 in both rows. |
| `REASON` | string | Reason for the designation, as the source records it. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/zoning/special-groundwater-protection-areas/special-groundwater-protection-areas.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
