# Methodology — Detecting & Correcting Spatial Bias in VGI Using Remote Sensing

## Goal
Use remote sensing as an objective reference to **detect** where OpenStreetMap (a VGI
source) under- or mis-maps the built environment, and to **correct** it by augmenting OSM
with RS-derived features.

## Sources (three, one is evaluated, two are the reference)
| Source | Role | Extraction |
|--------|------|------------|
| **OSM** (VGI) | **evaluated** layer | vector `building=*`, `highway=*` |
| **LiDAR** (USGS 3DEP QL1, 2019) | RS reference | DGCNN semantic segmentation → building footprints (done) |
| **NAIP** (aerial imagery) | RS reference | object detection / image segmentation |

**Key framing (not a symmetric 3-way):** the two RS sources form the ground truth, OSM is
measured against it.
> **RS consensus (LiDAR ∩ NAIP) = confident ground truth → evaluate OSM completeness/bias against it.**
NAIP does not "compare again"; it *corroborates* LiDAR so a feature is trusted only when
both remote sensors agree, which makes the OSM gap defensible.

## Feature × source matrix (not every feature comes from every source)
| Feature | OSM | LiDAR | NAIP | Comparison |
|---------|-----|-------|------|------------|
| **Buildings** | ✅ | ✅ (DGCNN) | ✅ (harder in top-down RGB) | 3-way; LiDAR primary, NAIP corroborates |
| **Roads** | ✅ | ✖ (no road class) | ✅ | **OSM vs NAIP** (LiDAR DTM only a weak cue) |

## Pipeline
1. **Extract** features from each source (LiDAR → DGCNN; OSM → vector tags; NAIP → segmentation).
2. **Rasterize** all layers to a **common grid** — EPSG:6350 (equal-area m), 0.2 m
   (0.1 m adds no information for polygon footprints; point clouds are ~0.22 m spacing).
3. **Pixel-wise comparison** → per-pixel agreement categories + completeness / commission,
   a gridded completeness surface (the spatial-bias map), and an omissions layer.
4. **Correct**: fill OSM gaps with RS-consensus features; report reduced spatial disparity.

## Temporal alignment (critical)
All three sources must be contemporaneous with the **2019** LiDAR:
- OSM → 2019-12-02 full-history snapshot (NOT the 2026 extract).
- NAIP → the flight nearest 2019 for Illinois.
Otherwise construction/demolition is confounded with mapping bias.

## Study area
The 2 × 2 km campus tile is the **methodology pilot** (it is ~fully OSM-mapped, so
completeness ≈ 100% with no gradient). The spatial-bias signal only emerges over an
**urban→rural gradient**; scale to the broader `IL_8County_PlusChampaign_2019` footprint
via a stratified transect for the actual bias analysis.

## Status
| Stage | State |
|-------|-------|
| LiDAR → DGCNN semantic segmentation | ✅ done (val OA 0.93, mIoU 0.77) |
| LiDAR building footprints → rasterize → pixel comparison (0.1/0.2 m) | ✅ done |
| OSM feature extraction (buildings, roads) | ⏳ pending real OSM-2019 |
| NAIP object detection / segmentation | ⬜ not started |
| 3-way RS-consensus vs OSM comparison | ◐ 2-way pipeline built; awaiting OSM + NAIP |

See [`src/`](src) for code and [`outputs/`](outputs/README.md) for results.
