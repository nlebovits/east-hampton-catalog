# Soils: agent guide

Source: ArcGIS layer [31](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/31) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: USDA Natural Resources Conservation Service.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/conservation/soils/soils.parquet`
- Rows: 545, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `MUSYM` | string | Soil map unit symbol. For example, BgA is Bridgehampton silt loam, 0 to 2 percent slopes. MkB is Montauk loam, 3 to 8 percent slopes. |
| `Acres` | double | Area in acres, as the Town computed it. |

## Known issues

MfA and MfB are not in the current NY103 soil survey legend. MfB is the second most common symbol in the layer, with 77 polygons. The Town layer can predate the current survey.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/conservation/soils/soils.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
