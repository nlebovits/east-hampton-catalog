# Significant Coastal Fish and Wildlife Habitats: agent guide

Source: ArcGIS layer [21](https://eh-gis.ehamptonny.gov/arcgis/rest/services/MapServiceForOpenGov/MapServer/21) of the Town of East Hampton MapServiceForOpenGov service, extracted 2026-10-15. Producer: Town of East Hampton, Department of Information Technology, GIS Division.

## The file

- Data: `https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/significant-coastal-habitats/significant-coastal-habitats.parquet`
- Rows: 24, one per source feature.
- Geometry column: `geometry`. A `bbox` struct column supports bounding-box filters.
- CRS: EPSG:2263, NAD83 / New York Long Island, in US survey feet. Areas and lengths computed on this geometry come out in square feet and feet. Transform to EPSG:4326 before you join with longitude and latitude data.
- Blank text: many text columns hold a single space `' '` where the source has no value. Use `trim(col) = ''` to find them.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `OBJECTID` | int64 | ArcGIS object ID in the source layer. |
| `NAME` | string | State habitat name. A single space for a locally significant habitat. |
| `TXT` | string | The habitat name without spaces, for example NapeagueBeach. |
| `SCFWH` | string | State habitat code, for example EH-3. The value is 0 for a locally significant habitat. |
| `LOCALLYSIG` | string | Name of a locally significant habitat. A single space for a State habitat. |
| `Area_Sq_Ft` | double | Area in square feet, as the Town computed it. |
| `Acres` | double | Area in acres, as the Town computed it. |

## Query with DuckDB

```sql
INSTALL spatial; LOAD spatial;

-- Row count. Total area in acres. The CRS unit is the US survey foot.
SELECT count(*) AS n, round(sum(ST_Area(geometry)) / 43560, 1) AS acres
FROM read_parquet('https://data.source.coop/portolan-mirrors/east-hampton-catalog/coastal/significant-coastal-habitats/significant-coastal-habitats.parquet');
```

The catalog-level [AGENTS.md](../../AGENTS.md) explains the layout and the [terms](../../LICENSE.md).
