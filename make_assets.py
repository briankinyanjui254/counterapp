#!/usr/bin/env python3
"""Assets for the Kumenya Mucii card:
  border.svg   -> tribal saw-tooth border, SAME zigzag triangle band on ALL
                  four edges (top, bottom, left, right)
  shield.svg   -> traditional Kikuyu shield + crossed staves emblem
  pattern.svg  -> subtle repeating tribal triangle watermark (card background)
Colours follow the cream/brown design palette.
"""

N = 400
SLICE = 48
DARK = "#4A342A"   # dark brown (matches --brown-dark)
MED  = "#A67353"   # rose-brown (matches --rose-brown)
TAN  = "#B8966D"   # tan border line (matches --border)
CREAM = "#F3E9D7"

def poly(pts, fill):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}"/>'

# ============================================================= BORDER =========
parts = [f'<svg xmlns="https://i.etsystatic.com/16237790/r/il/7c30f0/6928494463/il_300x300.6928494463_qkp0.jpg" width="{N}" height="{N}" viewBox="0 0 {N} {N}">']

# continuous frame lines on all 4 sides
parts.append(f'<rect x="4" y="4" width="{N-8}" height="{N-8}" fill="none" stroke="{DARK}" stroke-width="2.4" rx="3"/>')
parts.append(f'<rect x="8" y="8" width="{N-16}" height="{N-16}" fill="none" stroke="{TAN}" stroke-width="1.3" rx="3"/>')
parts.append(f'<rect x="40" y="40" width="{N-80}" height="{N-80}" fill="none" stroke="{DARK}" stroke-width="2.6" rx="3"/>')
parts.append(f'<rect x="46" y="46" width="{N-92}" height="{N-92}" fill="none" stroke="{TAN}" stroke-width="1" rx="2"/>')

# --- zigzag triangle band (period 50) between inner=13 and outer=37 ---
P = 50
a, b = 13, 37   # band edges
def zig_h(flip=False):
    out = []
    for k in range(0, N // P + 1):
        x = k * P
        yb, yt = (b, a) if not flip else (N - b, N - a)
        out.append(poly([(x, yb), (x + 25, yb), (x + 12.5, yt)], MED))
        out.append(poly([(x + 25, yt), (x + 50, yt), (x + 37.5, yb)], DARK))
    return out
def zig_v(right=False):
    out = []
    for k in range(0, N // P + 1):
        y = k * P
        xb, xt = (b, a) if not right else (N - b, N - a)
        out.append(poly([(xb, y), (xb, y + 25), (xt, y + 12.5)], MED))
        out.append(poly([(xt, y + 25), (xt, y + 50), (xb, y + 37.5)], DARK))
    return out

parts.append(f'<clipPath id="ct"><rect x="{SLICE}" y="0" width="{N-2*SLICE}" height="{SLICE}"/></clipPath>')
parts.append(f'<clipPath id="cb"><rect x="{SLICE}" y="{N-SLICE}" width="{N-2*SLICE}" height="{SLICE}"/></clipPath>')
parts.append(f'<clipPath id="cl"><rect x="0" y="{SLICE}" width="{SLICE}" height="{N-2*SLICE}"/></clipPath>')
parts.append(f'<clipPath id="cr"><rect x="{N-SLICE}" y="{SLICE}" width="{SLICE}" height="{N-2*SLICE}"/></clipPath>')
parts.append('<g clip-path="url(#ct)">' + "".join(zig_h(False)) + '</g>')
parts.append('<g clip-path="url(#cb)">' + "".join(zig_h(True)) + '</g>')
parts.append('<g clip-path="url(#cl)">' + "".join(zig_v(False)) + '</g>')
parts.append('<g clip-path="url(#cr)">' + "".join(zig_v(True)) + '</g>')

# corner diamonds mask joints
for cx, cy in [(24, 24), (N-24, 24), (24, N-24), (N-24, N-24)]:
    parts.append(poly([(cx, cy-12), (cx+12, cy), (cx, cy+12), (cx-12, cy)], DARK))
    parts.append(poly([(cx, cy-6), (cx+6, cy), (cx, cy+6), (cx-6, cy)], CREAM))

parts.append('</svg>')
open("border.svg", "w").write("\n".join(parts))
print("border.svg written")

# ============================================================= SHIELD =========
# Traditional Kikuyu-style hide shield (ndomo) with crossed ceremonial staves.
shield = f'''<svg xmlns="https://placehold.co/1200x600/e2e8f0/1e293b?text=SVG_illustration_of_a_traditional_Kikuyu_style_hid" width="120" height="96" viewBox="0 0 120 96">
  <!-- crossed staves -->
  <g stroke="{DARK}" stroke-width="3" stroke-linecap="round">
    <line x1="18" y1="86" x2="102" y2="14"/>
    <line x1="102" y1="86" x2="18" y2="14"/>
  </g>
  <g fill="{MED}">
    <circle cx="18" cy="86" r="4"/><circle cx="102" cy="14" r="4"/>
    <circle cx="102" cy="86" r="4"/><circle cx="18" cy="14" r="4"/>
  </g>
  <!-- shield body -->
  <path d="M60 8 C74 20 84 22 92 22 C90 52 80 74 60 88 C40 74 30 52 28 22 C36 22 46 20 60 8 Z"
        fill="{CREAM}" stroke="{DARK}" stroke-width="3"/>
  <!-- central vertical band -->
  <path d="M60 12 C63 34 63 62 60 84 C57 62 57 34 60 12 Z" fill="{DARK}"/>
  <!-- side patches -->
  <path d="M42 30 C40 44 44 58 52 70 C46 54 46 42 48 30 Z" fill="{MED}"/>
  <path d="M78 30 C80 44 76 58 68 70 C74 54 74 42 72 30 Z" fill="{MED}"/>
  <!-- triangle accents -->
  <polygon points="60,26 65,36 55,36" fill="{TAN}"/>
  <polygon points="60,70 65,60 55,60" fill="{TAN}"/>
</svg>'''
open("shield.svg", "w").write(shield)
print("shield.svg written")

# ============================================================= PATTERN =========
# Subtle repeating triangle tile used as a faint card watermark (behind text).
pat = f'''<svg xmlns="https://i.etsystatic.com/45014349/r/il/0cf3bd/6815093435/il_fullxfull.6815093435_cum5.jpg" width="60" height="52" viewBox="0 0 60 52">
  <g fill="{MED}" opacity="0.9">
    <polygon points="0,0 20,0 10,17"/>
    <polygon points="30,0 50,0 40,17"/>
    <polygon points="15,26 35,26 25,43"/>
    <polygon points="45,26 60,26 55,43"/>
    <polygon points="0,26 5,26 2,43"/>
  </g>
</svg>'''
open("pattern.svg", "w").write(pat)
print("pattern.svg written")
