# NYSDEC Freshwater Wetlands: agent guide

Source: ArcGIS layer [28](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/28) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: New York State Department of Environmental Conservation.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/dec-freshwater-wetlands/dec-freshwater-wetlands.parquet`
- Rows: 592, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `WETID` | string | NYSDEC wetland identifier. |
| `Acres` | double | Area in acres, as the Town computed it. |
| `CLASS` | string | NYSDEC wetland class, 1 to 4. One row holds 0. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/dec-freshwater-wetlands/dec-freshwater-wetlands.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
