#!/usr/bin/env python3
"""Generate a tileable tribal border (9-slice border-image) that replicates
Invitation (2).png:
  - top & bottom edges  -> zigzag of alternating solid triangles (thin line
    above, thick line below)
  - left & right edges  -> vertical column of nested triangles + solid diamonds
  - continuous outer + inner frame lines, corner diamonds to mask joints
"""

N = 400          # svg canvas
SLICE = 48       # border-image slice
DARK = "#43281A" # main dark brown (lines + solids)
MED  = "#6E4526" # medium brown (triangle fills)

def poly(pts, fill, stroke=None, sw=0):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<polygon points="{p}" fill="{fill}"{s}/>'

parts = [f'<svg xmlns="https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorials/SVG_from_scratch/Fills_and_strokes/svg_stroke_linejoin_example.png" width="{N}" height="{N}" viewBox="0 0 {N} {N}">']

# ---------- continuous frame lines (all 4 sides) ----------
# very outer thin line
parts.append(f'<rect x="4" y="4" width="{N-8}" height="{N-8}" fill="none" stroke="{DARK}" stroke-width="2.4" rx="3"/>')
# band OUTER bounding line
parts.append(f'<rect x="8" y="8" width="{N-16}" height="{N-16}" fill="none" stroke="{DARK}" stroke-width="2" rx="3"/>')
# band INNER bounding line (thick)
parts.append(f'<rect x="40" y="40" width="{N-80}" height="{N-80}" fill="none" stroke="{DARK}" stroke-width="3" rx="3"/>')
# inner thin accent line
parts.append(f'<rect x="46" y="46" width="{N-92}" height="{N-92}" fill="none" stroke="{DARK}" stroke-width="1" rx="2"/>')

# ============ TOP & BOTTOM edges: zigzag triangles ============
# band between y_top=13 (below outer line) and y_bot=37 (above inner line)
P = 50
yt, yb = 13, 37
def h_zigzag(flip=False):
    out = []
    for k in range(0, N // P + 1):
        x = k * P
        if not flip:
            # up triangle
            out.append(poly([(x, yb), (x + 25, yb), (x + 12.5, yt)], MED))
            # down triangle
            out.append(poly([(x + 25, yt), (x + 50, yt), (x + 37.5, yb)], DARK))
        else:
            out.append(poly([(x, N - yb), (x + 25, N - yb), (x + 12.5, N - yt)], MED))
            out.append(poly([(x + 25, N - yt), (x + 50, N - yt), (x + 37.5, N - yb)], DARK))
    return out

# clip the zigzag to the top / bottom middle strips so it doesn't bleed into corners
parts.append(f'<clipPath id="ctop"><rect x="{SLICE}" y="0" width="{N-2*SLICE}" height="{SLICE}"/></clipPath>')
parts.append(f'<clipPath id="cbot"><rect x="{SLICE}" y="{N-SLICE}" width="{N-2*SLICE}" height="{SLICE}"/></clipPath>')
parts.append('<g clip-path="url(#ctop)">' + "".join(h_zigzag(False)) + '</g>')
parts.append('<g clip-path="url(#cbot)">' + "".join(h_zigzag(True)) + '</g>')

# ============ LEFT & RIGHT edges: nested triangle + diamond ============
# band between x=13 and x=37
P2 = 64
xl, xr = 13, 37
def v_motif(right=False):
    out = []
    for k in range(0, N // P2 + 2):
        y = k * P2
        # nested right-pointing triangle (solid MED + cream notch look via DARK outline)
        if not right:
            out.append(poly([(xl, y + 3), (xl, y + 31), (xr, y + 17)], MED))
            out.append(poly([(xl + 4, y + 11), (xl + 4, y + 23), (xr - 6, y + 17)], "#F3E9D7"))
            # solid diamond
            cy = y + 48
            out.append(poly([(24, cy - 8), (31, cy), (24, cy + 8), (17, cy)], DARK))
        else:
            X = N - xl; XR = N - xr
            out.append(poly([(X, y + 3), (X, y + 31), (XR, y + 17)], MED))
            out.append(poly([(X - 4, y + 11), (X - 4, y + 23), (XR + 6, y + 17)], "#F3E9D7"))
            cy = y + 48
            cx = N - 24
            out.append(poly([(cx, cy - 8), (cx - 7, cy), (cx, cy + 8), (cx + 7, cy)], DARK))
    return out

parts.append(f'<clipPath id="clft"><rect x="0" y="{SLICE}" width="{SLICE}" height="{N-2*SLICE}"/></clipPath>')
parts.append(f'<clipPath id="crgt"><rect x="{N-SLICE}" y="{SLICE}" width="{SLICE}" height="{N-2*SLICE}"/></clipPath>')
parts.append('<g clip-path="url(#clft)">' + "".join(v_motif(False)) + '</g>')
parts.append('<g clip-path="url(#crgt)">' + "".join(v_motif(True)) + '</g>')

# ============ corner diamonds (mask the joints) ============
for cx, cy in [(24, 24), (N - 24, 24), (24, N - 24), (N - 24, N - 24)]:
    parts.append(poly([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)], DARK))
    parts.append(poly([(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)], "#F3E9D7"))

parts.append('</svg>')
open("border.svg", "w").write("\n".join(parts))
print("border.svg written, slice =", SLICE)
