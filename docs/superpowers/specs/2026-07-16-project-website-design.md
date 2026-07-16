# Project Website — Design Spec (2026-07-16)

## Goal
Single-page English project site for the research, served by GitHub Pages from
`docs/` on `main` → https://rayford295.github.io/vgi-spatial-bias/.

## Content (one scrolling page)
1. Hero — title, one-line claim, buttons (Notebook · GitHub · I-GUIDE element),
   stat band (2 regions · 102 counties · 375,754 road segments · 2,816 buildings detected).
2. The problem — one paragraph + campus bias map teaser.
3. Pipeline — 7-step flow (reference → optical → detect → validate → scale →
   correct → generalize), pure CSS.
4. Findings — the 7 key findings as cards (big number + one-line takeaway + figure).
5. Two regions — UIUC vs Colorado Springs side-by-side (temporal maps + metric table).
6. Correction — A/B/C table, gallery figure, label-volume flip.
7. Data & reproducibility — release cards, citation block, I-GUIDE attribution.

## Visual direction — "Cartographic Editorial"
Parchment ground (#f6f1e7), deep green-black ink, ochre/terracotta accent,
contour-line SVG texture, Fraunces display serif + Archivo body + mono for
figures/coordinates. Scroll-reveal animations, responsive.

## Technical
- One self-contained `docs/index.html` (inline CSS/JS; Google Fonts allowed).
- Figures: web-optimized JPEG copies (max width 1600 px) in `docs/assets/` so the
  site never breaks if `results/` moves.
- Pages enabled from `main:/docs` (via gh API; manual fallback documented).
- Existing markdown files in docs/ are unaffected.
