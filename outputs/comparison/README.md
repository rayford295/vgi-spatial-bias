# comparison/ — VGI-vs-LiDAR building comparison

Produced by [`../../src/vgi_comparison.py`](../../src/vgi_comparison.py). Matches
LiDAR-detected building footprints against a **reference** building layer via IoU
(threshold 0.3, in EPSG:6350), and reports completeness (recall), commission, a gridded
completeness surface (the spatial-bias map), and an `omissions.geojson` layer
(LiDAR buildings absent from the reference).

## ⚠️ Current run is a PIPELINE TEST, not the VGI result
The reference layer used here is a **LiDAR-derived** ArcGIS building extraction
(`ObjectCode=6`, `MIN_Z/MAX_Z`, same tile bounds), **not OSM**. So the numbers below are a
**cross-method check** (our detection vs an independent LiDAR extraction), which is why
agreement is near-total:

| completeness (count) | completeness (area) | median IoU | LiDAR-only | reference-only |
|---|---|---|---|---|
| 99.8% | 100.0% | 0.94 | 3 | 61 |

This validates (a) our building detection and (b) the matching pipeline. It is **not**
evidence about OSM completeness.

## Per-pixel comparison (`pixel/`, `src/pixel_comparison.py`)
Rasterizes both building layers to a fine grid and records a per-pixel agreement category
(both / LiDAR-only / reference-only / neither) → `pixel_diff_<res>.tif` (load in
ArcGIS/QGIS to inspect any pixel), plus metrics and a zoom crop.

| res | pixels | building-pixel IoU | pixel OA | Cohen κ | disagreement |
|-----|--------|-------------------|----------|---------|--------------|
| 0.2 m | 100 M | 0.9612 | 0.9907 | 0.9741 | 37,306 m² |
| 0.1 m | 400 M | 0.9612 | 0.9907 | 0.9741 | 37,255 m² |

**0.1 m and 0.2 m give identical metrics** — because both footprint layers are polygons
extracted at ≥0.5 m, a 0.1 m grid only resamples the same edges (no new information) at 4×
the file size. Disagreement (~37,300 m², ~4% of building area) is a **thin edge fringe**
(zoom crop); interiors agree 100%. Point density (20 pts/m², 0.22 m spacing) means 0.1 m
is only meaningful for polygon rasterization, not point-derived surfaces (~82% empty pixels).
→ **0.2 m is the sensible fine output; going to 0.1 m buys nothing here.** Genuinely finer
footprints would require re-detecting from points at ~0.2 m, not resampling.

## For the actual study
1. Supply **OSM `building=*` polygons** as the reference:
   `python src/vgi_comparison.py osm_buildings_2019.geojson`
   — use the **2019** snapshot (temporally matched to the LiDAR), not 2026.
2. This 2×2 km campus tile is ~fully mapped in OSM, so completeness will sit near 100%
   here regardless. The **spatial-bias signal** only emerges over an urban→rural gradient;
   extend the study area accordingly.
