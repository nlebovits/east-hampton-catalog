# FEMA Flood Zones, 2009: agent guide

Source: ArcGIS layer [36](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/36) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Federal Emergency Management Agency.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/fema-dfirm-2009/flood-zones/flood-zones.parquet`
- Rows: 4796, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `FLD_ZONE` | string | Flood zone. A, AE, AO, V, and VE are Special Flood Hazard Areas, the 1-percent-annual-chance flood. V and VE also carry wave action. "0.2 PCT ANNUAL CHANCE FLOOD HAZARD" lies between the 1-percent and 0.2-percent-annual-chance floods. See the [FEMA flood zone glossary](https://www.fema.gov/about/glossary/flood-zones). |
| `SFHA_TF` | string | T when the zone is a Special Flood Hazard Area, F otherwise. |
| `STATIC_BFE` | double | Base flood elevation. -9999 means no value. |
| `V_DATUM` | string | Vertical datum of STATIC_BFE, NAVD88 or a single space. |
| `LEN_UNIT` | string | Unit of STATIC_BFE, FEET or a single space. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/fema-dfirm-2009/flood-zones/flood-zones.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
