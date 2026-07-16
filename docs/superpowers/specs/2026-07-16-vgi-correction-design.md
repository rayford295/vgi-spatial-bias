# VGI Correction Pipeline — Design Spec (2026-07-16)

## Goal

Turn detected OSM omissions (547 building gaps from the LiDAR+NAIP consensus) into
**machine-proposed fixes**, and compare three correction approaches head-to-head.
Deliverable: research method + paper-grade validation (no direct OSM submission;
outputs comply with the OSM Automated Edits Code of Conduct by remaining research
artifacts for human review).

## Key asset

Temporal validation gives free labels: of the 547 gaps detected in 2019,
**352 were filled by the OSM community by 2026** (geometry truth = what the community
actually drew) and **195 remain unmapped** (deployment targets). This lets us score
both proposal geometry (IoU vs community polygons) and proposal confidence
(does it predict community acceptance?) without any manual annotation.

## Approaches compared (the paper ablation)

|  | Geometry | Confidence |
|---|---|---|
| **A** | rule regularization | rule tiers (area/height/NAIP-support thresholds) |
| **B** | learned (U-Net on NAIP RGBN + CHM, trained on 352 community polygons) | mask probability |
| **C** | rule regularization (same as A) | learned GBM "acceptance scorer" |

## Components (all in `src/`, notebook gains Stage 7)

- `propose_geometry.py` — shared rule regularization: minimum-rotated-rectangle when
  fill-ratio ≥ 0.8, else rotate-to-principal-axis + simplify + orthogonalize edge walk;
  fallback to simplified hull with `regularized=false`. Tags: `building=yes`,
  `height` from LiDAR. Also produces the gap↔2026-community matching (labels + truth).
- `propose_learned.py` — small U-Net, 5-channel 0.5 m patches (NAIP R,G,B,N + CHM),
  west-half training with flip/rot augmentation, inference on all gaps → polygonize →
  same regularization exit.
- `acceptance_scorer.py` — features: area, height, NAIP impervious fraction,
  distance to nearest 2019 road, 100 m neighborhood OSM completeness, shape
  regularity. GBM classifier vs rule tiers, west/east split.
- `correction_benchmark.py` — east-half evaluation: geometry (median IoU, centroid
  offset, area ratio vs community polygons) and confidence (AUC, precision@50);
  example-gallery figure + still-unmapped deployment map;
  `results/correction/correction_benchmark.json`.
- `deploy_priority.py` — statewide county priority = staleness × population exposure
  from `results/statewide/county_metrics.csv` → choropleth + top-10 table.

## Evaluation protocol

- Spatial split at tile midline (x = 656,000 m, EPSG:6350), matching the DGCNN split:
  train west, evaluate east. Applies to B and C; A has no training.
- Geometry metrics computed only on filled gaps (truth exists); the 195 still-unmapped
  get proposals for the deployment map but never enter the metric tables.

## Error handling

- Regularization failure → convex-hull fallback, flagged and counted.
- U-Net small-sample risk (352) → augmentation + honest reporting; stage skippable
  (RUN_LEARNED flag) on CPU-only platforms.

## Success criteria

Pipeline runs end-to-end in the notebook (Stage 7); benchmark table produced;
geometry median IoU meaningfully above 0.3; learned scorer AUC above rule tiers or
the difference honestly reported.
