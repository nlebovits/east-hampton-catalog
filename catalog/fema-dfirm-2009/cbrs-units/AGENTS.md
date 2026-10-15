# Coastal Barrier Resources System Units: agent guide

Source: ArcGIS layer [34](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/34) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: U.S. Fish and Wildlife Service, Coastal Barrier Resources System.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/fema-dfirm-2009/cbrs-units/cbrs-units.parquet`
- Rows: 211, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `Unit` | string | CBRS unit number. An Otherwise Protected Area number ends in P. |
| `CBRS_Type` | string | "System Unit", where most new federal spending and federal flood insurance are prohibited. "Otherwise Protected Area", where only federal flood insurance is prohibited. |
| `FI_Date` | timestamp[us] | "The date on which the prohibition on Federal flood insurance first took effect for a given area" (USFWS CBRS metadata). |
| `SU_Date` | timestamp[us] | "The date on which prohibitions on Federal expenditures besides flood insurance ... went into effect" (USFWS CBRS metadata). Null for an Otherwise Protected Area. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/fema-dfirm-2009/cbrs-units/cbrs-units.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
