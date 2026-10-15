# National Wetlands Inventory: agent guide

Source: ArcGIS layer [29](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/29) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: U.S. Fish and Wildlife Service, National Wetlands Inventory.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/nwi-wetlands/nwi-wetlands.parquet`
- Rows: 2625, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `ATTRIBUTE` | string | Cowardin classification code. The first letter is the system. E is Estuarine, P is Palustrine, M is Marine, L is Lacustrine, and R is Riverine. |
| `Acres` | double | Area in acres, as the Town computed it. |

## Known issues

173 rows hold the ATTRIBUTE value U. The NWI code list does not define U as a wetland class, and the Town does not explain it.

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/wetlands/nwi-wetlands/nwi-wetlands.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
