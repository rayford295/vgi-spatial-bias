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

## For the actual study
1. Supply **OSM `building=*` polygons** as the reference:
   `python src/vgi_comparison.py osm_buildings_2019.geojson`
   — use the **2019** snapshot (temporally matched to the LiDAR), not 2026.
2. This 2×2 km campus tile is ~fully mapped in OSM, so completeness will sit near 100%
   here regardless. The **spatial-bias signal** only emerges over an urban→rural gradient;
   extend the study area accordingly.
