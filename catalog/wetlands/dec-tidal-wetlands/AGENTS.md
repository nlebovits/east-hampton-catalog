# NYSDEC Tidal Wetlands: agent guide

Source: ArcGIS layer [27](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/27) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: New York State Department of Environmental Conservation.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/dec-tidal-wetlands/dec-tidal-wetlands.parquet`
- Rows: 466, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `TWCAT74` | string | 1974 tidal wetland category. IM is Intertidal Marsh. HM is High Marsh or Salt Meadow. FM is Coastal Fresh Marsh. FC is Formerly Connected. SM is Coastal Shoals, Bars and Mudflats. LZ is Littoral Zone. AA is Adjacent Area. DS is Dredged Spoil. HL is a hole area with no tidal wetland, as TW_Desig states. |
| `ACREAGE74` | double | Area in acres, as the source records it. |
| `TW_Desig` | string | The category name, as text. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/dec-tidal-wetlands/dec-tidal-wetlands.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
