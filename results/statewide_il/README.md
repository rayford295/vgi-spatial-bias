# Statewide spatial-bias analysis — OSM 2019 IL major roads

**Input**: `OSM_2019_Major_Roads` shapefile (375,754 segments, 235,064 km;
fclass = residential/tertiary/secondary/primary; county-joined via ArcGIS).
Belongs with the [`osm-il-2019` release](https://github.com/rayford295/vgi-spatial-bias/releases/tag/osm-il-2019)
(too large to commit). Auxiliary: Census 2019 gazetteer (land area),
co-est2019 (county population), cb_2019_us_county_20m (boundaries).

**Script**: `src/statewide_bias.py <roads_shp> <aux_dir> <out_dir>`

## Question

Does OSM road data quality vary systematically with who lives there?
(Project research question 1, at Level-4 "spatial bias" in `docs/METRICS.md`,
scaled from campus to all 102 Illinois counties.)

## Metrics (per county)

- **Attribute completeness**: % of segments tagged with maxspeed / surface / ref / name
- **Edit recency**: median `lastchange` year; % of segments edited 2017+
- **Supply**: road length density (km/km²), km per 1,000 residents

## Findings (`bias_tests.csv`)

| metric | Spearman ρ vs pop density | urban mean | rural mean |
|---|---|---|---|
| % maxspeed tagged | **0.50** (p<1e-7) | 3.1 | 1.2 |
| % surface tagged | **0.60** | 2.5 | 1.6 |
| % named | **0.65** | 92.3 | 71.5 |
| % edited 2017+ | **0.70** | 29.9 | 9.3 |
| median edit year | **0.59** | 2014.2 | 2012.3 |
| road density (km/km²) | **0.71** | 3.60 | 1.31 |

(urban = ≥100 persons/km², 24 counties)

1. **Attribute completeness is strongly urban-biased.** Statewide, only 3.3% of
   segments carry a usable maxspeed and 2.8% a surface tag; both rates rise
   monotonically with population density.
2. **Rural OSM is stale.** In rural counties 90%+ of segments were last touched
   before 2017; several downstate counties (White, Edgar, Wayne) have median
   last-edit year **2008** — essentially untouched since the TIGER import.
   Urban counties (Cook, DuPage, Will: median 2016) are actively maintained.
3. **Single-contributor hotspot**: Sangamon County (Springfield) has 33.9%
   maxspeed / 36.3% surface tagging — 3–10× any other county — a signature of
   one dedicated local mapper/import, not general community coverage. Bias is
   not a smooth urban→rural gradient; individual contributors create spikes.
4. **Geometric supply is near-complete everywhere** (km per 1,000 residents is
   *higher* in rural counties, ρ = −0.97, as expected from the TIGER import),
   confirming the campus-scale finding: in the US the bias lives in
   **attributes and currency, not in whether the line exists**.

## Outputs

- `county_metrics.csv` — 102 counties × all metrics
- `bias_tests.csv` — Spearman ρ, p-values, urban/rural means
- `choropleth_completeness.png` — 4-panel county maps (tag rates capped at
  95th percentile so Sangamon doesn't flatten the ramp)
- `scatter_bias.png` — completeness/recency vs. log population density
