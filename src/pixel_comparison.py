"""
Per-PIXEL building comparison: LiDAR footprints vs a reference layer, rasterized to a
fine grid (default 0.2 m; pass 0.1 for 0.1 m).  Answers "compare notes on each pixel".

For every pixel it records agreement category:
  0 neither (both background)   1 both (agree building)
  2 LiDAR-only                  3 reference-only
Writes a category GeoTIFF (load in ArcGIS/QGIS to click any pixel), a full-extent map,
a zoom crop at true resolution, and pixel-level metrics (agreement, IoU, kappa).

Usage:  python src/pixel_comparison.py <reference.shp|.geojson> [resolution_m]

NOTE: building footprints are POLYGONS, so they rasterize cleanly at 0.1 m even though
the point cloud (20 pts/m^2, ~0.22 m spacing) could not support a 0.1 m *point-derived*
raster. Our LiDAR footprints were detected on a 0.5 m grid, so sub-0.5 m edge
disagreements partly reflect that extraction quantization, not true error.
"""
import os, sys, json, numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.crs import CRS
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "comparison", "pixel"); os.makedirs(OUT, exist_ok=True)
LIDAR = os.path.join(ROOT, "outputs", "detection", "buildings.geojson")
if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    sys.exit("usage: python src/pixel_comparison.py <reference.shp|.geojson> [resolution_m]")
REF = sys.argv[1]
RES = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
tag = f"{RES:g}m".replace(".", "p")
CMAP = ListedColormap(["#f0f0f0", "#4c9f70", "#d1483f", "#3b6fb0"])  # neither/both/lidar/ref
LABELS = ["neither", "both (agree)", "LiDAR-only", "reference-only"]

lid = gpd.read_file(LIDAR).to_crs(6350); lid["geometry"] = lid.buffer(0)
ref = gpd.read_file(REF).to_crs(6350);   ref["geometry"] = ref.buffer(0)
xmin, ymin, xmax, ymax = lid.total_bounds
nx = int(round((xmax - xmin) / RES)); ny = int(round((ymax - ymin) / RES))
transform = from_origin(xmin, ymax, RES, RES)
print(f"[{tag}] grid {ny} x {nx} = {ny*nx/1e6:.0f} M pixels")

def burn(gdf):
    return rasterize(((g, 1) for g in gdf.geometry), out_shape=(ny, nx),
                     transform=transform, fill=0, dtype="uint8", all_touched=False)
mL = burn(lid); mR = burn(ref)
cat = np.zeros((ny, nx), np.uint8)
cat[(mL == 1) & (mR == 1)] = 1
cat[(mL == 1) & (mR == 0)] = 2
cat[(mL == 0) & (mR == 1)] = 3

both = int((cat == 1).sum()); lo = int((cat == 2).sum())
ro = int((cat == 3).sum());   neither = int((cat == 0).sum())
total = ny * nx; pa = RES * RES
a, b = mL.astype(bool), mR.astype(bool)
pL, pR = a.mean(), b.mean(); po = (both + neither) / total
pe = pL * pR + (1 - pL) * (1 - pR)
metrics = dict(resolution_m=RES, grid=[ny, nx],
    building_pixel_IoU=round(both / (both + lo + ro), 4),
    pixel_agreement_OA=round(po, 4),
    cohen_kappa=round((po - pe) / (1 - pe), 4),
    agree_building_m2=round(both * pa, 1),
    lidar_only_m2=round(lo * pa, 1), reference_only_m2=round(ro * pa, 1),
    disagreement_m2=round((lo + ro) * pa, 1))
json.dump(metrics, open(os.path.join(OUT, f"pixel_metrics_{tag}.json"), "w"), indent=2)
print(json.dumps(metrics, indent=2))

with rasterio.open(os.path.join(OUT, f"pixel_diff_{tag}.tif"), "w", driver="GTiff",
                   height=ny, width=nx, count=1, dtype="uint8", crs=CRS.from_epsg(6350),
                   transform=transform, nodata=255, compress="lzw") as dst:
    dst.write(cat, 1)
    dst.write_colormap(1, {0:(240,240,240),1:(76,159,112),2:(209,72,63),3:(59,111,176)})

# full-extent map (display-downsampled)
step = max(1, nx // 2000)
fig, ax = plt.subplots(figsize=(10, 10), dpi=130)
ax.imshow(cat[::step, ::step], cmap=CMAP, vmin=0, vmax=3,
          extent=[xmin, xmax, ymin, ymax], origin="upper", interpolation="nearest")
ax.set_title(f"Per-pixel building agreement @ {RES:g} m\n"
             f"IoU {metrics['building_pixel_IoU']:.3f} · OA {metrics['pixel_agreement_OA']:.3f} · "
             f"κ {metrics['cohen_kappa']:.3f} · disagree {metrics['disagreement_m2']:,.0f} m²")
ax.legend(handles=[Patch(color=CMAP(i), label=LABELS[i]) for i in range(4)],
          loc="lower center", ncol=4, fontsize=8)
ax.ticklabel_format(style="plain"); fig.tight_layout()
fig.savefig(os.path.join(OUT, f"pixel_diff_{tag}.png")); plt.close(fig)

# zoom crop (120 m window) at true resolution
cxr, cyr = 656100, 1926100; half = 60
c0 = int((cxr - half - xmin) / RES); c1 = int((cxr + half - xmin) / RES)
r0 = int((ymax - (cyr + half)) / RES); r1 = int((ymax - (cyr - half)) / RES)
crop = cat[r0:r1, c0:c1]
fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
ax.imshow(crop, cmap=CMAP, vmin=0, vmax=3,
          extent=[cxr-half, cxr+half, cyr-half, cyr+half], origin="upper", interpolation="nearest")
ax.set_title(f"Zoom (120 m) @ {RES:g} m — red/blue = edge disagreement")
ax.ticklabel_format(style="plain"); fig.tight_layout()
fig.savefig(os.path.join(OUT, f"pixel_diff_zoom_{tag}.png")); plt.close(fig)
print("done ->", OUT)
