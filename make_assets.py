#!/usr/bin/env python3
"""Generate a tileable tribal border (9-slice border-image) + cowrie shell SVGs
matching Invitation (1).png."""

S = 400          # svg canvas
BAND = 46        # border-image slice thickness
DARK = "#3F2513"   # outer line dark brown
MED  = "#6E4A2E"   # triangles / medium brown
LINE2 = "#8A6238"  # thin accent line

def tri(pts, fill):
    p = " ".join(f"{x},{y}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}"/>'

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">')

# ---- outer + inner frame lines ----
parts.append(f'<rect x="5" y="5" width="{S-10}" height="{S-10}" fill="none" stroke="{DARK}" stroke-width="3.5" rx="4"/>')
parts.append(f'<rect x="12" y="12" width="{S-24}" height="{S-24}" fill="none" stroke="{LINE2}" stroke-width="1.4" rx="3"/>')
parts.append(f'<rect x="41" y="41" width="{S-82}" height="{S-82}" fill="none" stroke="{DARK}" stroke-width="2.4" rx="3"/>')
parts.append(f'<rect x="47" y="47" width="{S-94}" height="{S-94}" fill="none" stroke="{LINE2}" stroke-width="1" rx="2"/>')

# ---- saw-tooth triangle band, period 40, between y=17 and y=35 ----
P = 40
outer, inner = 17, 35     # band edges
for k in range(0, S // P):
    x = k * P
    # top edge: downward triangle
    parts.append(tri([(x, outer), (x + P, outer), (x + P/2, inner)], MED))
    # bottom edge: upward triangle
    parts.append(tri([(x, S-outer), (x + P, S-outer), (x + P/2, S-inner)], MED))
    # left edge: rightward triangle
    parts.append(tri([(outer, x), (outer, x + P), (inner, x + P/2)], MED))
    # right edge: leftward triangle
    parts.append(tri([(S-outer, x), (S-outer, x + P), (S-inner, x + P/2)], MED))

# ---- corner diamonds (mask the joints) ----
for cx, cy in [(26, 26), (S-26, 26), (26, S-26), (S-26, S-26)]:
    parts.append(tri([(cx, cy-11), (cx+11, cy), (cx, cy+11), (cx-11, cy)], DARK))
    parts.append(tri([(cx, cy-6), (cx+6, cy), (cx, cy+6), (cx-6, cy)], "#F2E6CC"))

parts.append('</svg>')
open("border.svg", "w").write("\n".join(parts))
print("border.svg written, slice =", BAND)

# --------------------------------------------------------------------------
# Cowrie shell (bead) SVG — reusable symbol
# --------------------------------------------------------------------------
cowrie = '''<svg xmlns="https://i.etsystatic.com/20212866/r/il/4421cd/6742484306/il_300x300.6742484306_qaps.jpg" width="46" height="32" viewBox="0 0 46 32">
  <ellipse cx="23" cy="16" rx="21" ry="14" fill="#F0E4CB" stroke="#B08A52" stroke-width="1.4"/>
  <ellipse cx="23" cy="16" rx="21" ry="14" fill="url(#g)" opacity="0.5"/>
  <defs><radialGradient id="g" cx="0.5" cy="0.35" r="0.7">
     <stop offset="0" stop-color="#FFFDF7"/><stop offset="1" stop-color="#D8C199"/>
  </radialGradient></defs>
  <path d="M23 4 C24 10 24 22 23 28" stroke="#5B4327" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  <g stroke="#8A6A3E" stroke-width="1.3" stroke-linecap="round">
    <path d="M23 7 l-4 2 M23 10 l-4 2 M23 13 l-4 1.5 M23 16 l-4 1.5 M23 19 l-4 1.5 M23 22 l-4 2 M23 25 l-4 2"/>
    <path d="M23 7 l4 2 M23 10 l4 2 M23 13 l4 1.5 M23 16 l4 1.5 M23 19 l4 1.5 M23 22 l4 2 M23 25 l4 2"/>
  </g>
</svg>'''
open("cowrie.svg", "w").write(cowrie)
print("cowrie.svg written")
