# UIUC Campus LiDAR — Object Detection & Segmentation

Inputs: `UIUC_campus_LiDAR_merged_2x2km.laz` (80.8 M pts, EPSG:6350, NAVD88 heights).
Two complementary layers were produced. Run with `python3 detect_classical.py` and
`python3 dl_semseg.py` (from the parent folder).

## 1. Classical detection (instance-level, runs on CPU, ~2 min)
`detect_classical.py` — one 0.5 m rasterization pass feeds three detectors.

| Target | Method | Result | Files |
|--------|--------|--------|-------|
| **Ground / DTM** | min-Z of class 2 + nearest-fill | bare-earth terrain | `dtm.tif`, `chm.tif`, `ground_dtm.png` |
| **Buildings** | class-6 raster → morphology → connected components; height from CHM | **1,312 buildings**, 0.94 km² footprint, median 8.3 m | `buildings.geojson`, `buildings_detected.png` |
| **Trees** | CHM local-maxima (≥3 m, 3 m spacing) + watershed crowns | **11,777 trees**, median 12 m, 21.5 m² crown | `trees.geojson`, `trees_detected.png` |

GeoJSON is in WGS84 lon/lat (EPSG:4326) — drop straight into QGIS / JOSM / iD.
Per-object attributes: buildings → `area_m2`, `height_m`; trees → `height_m`, `crown_m2`.

## 2. Deep-learning semantic segmentation (PyTorch, MPS, ~4 min)
`dl_semseg.py` — block-wise PointNet predicts the 5 ASPRS semantic classes.
Ground truth = the classification already in the LAZ. **Spatial split** (west half
train, east half validation) so there is no train/val leakage.

Key feature: **height-above-ground** (z − DTM) — removes the 14 m campus elevation
gradient so ground≈0, buildings=plateau, trees=tall spread.

**Validation results (held-out east half): OA = 0.913, mIoU = 0.707**

| Class | IoU | Precision | Recall |
|-------|-----|-----------|--------|
| Ground   | 0.96 | 0.97 | 0.99 |
| High Veg | 0.85 | 0.90 | 0.94 |
| Building | 0.78 | 0.92 | 0.84 |
| Med Veg  | 0.57 | 0.68 | 0.77 |
| Low Veg  | 0.39 | 0.69 | 0.47 |

Errors are "adjacent-class" only (Low Veg↔Ground, Med↔High Veg); Building↔Ground ≈ 0.01.
Files: `dl_metrics.json`, `dl_confusion.png`, `dl_prediction.png`, `dl_pointnet.pt`.

### Known limitations / next steps
- Vanilla PointNet has **no cross-block context** → the prediction map shows faint
  40 m block seams and slightly blurred building edges. Upgrading to **PointNet++ /
  KPConv** (with local neighborhood aggregation) would sharpen this; needs a CUDA GPU
  for reasonable speed.
- Low/Med veg confusion is data-inherent (fuzzy ASPRS height cutoffs).
- For *instance* segmentation via DL (individual buildings/trees, not just class),
  add an offset-prediction head + clustering, or fuse with the classical instances here.
