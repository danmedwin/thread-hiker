"""Convert Passages-shapes-2.svg (stroked centerlines) into paths.json.

This is the preferred pipeline: Dan draws each thread as a single stroked
path in Pixelmator; we flatten the curves directly — no rasterizing, no
skeletonizing, full precision. Colors are read from the stroke attribute.

Needs: pip install svgpathtools numpy
"""
import re, json
import numpy as np
from svgpathtools import parse_path

SVG = "/Users/medwin/Documents/Thread Hiker/Passages-shapes-2.svg"
OUT = "/Users/medwin/Documents/Thread Hiker/paths.json"

SCALE = 3          # keep the same coordinate space as the v0.7 course
SIZE = 721 * SCALE
SPACING = 2.0      # sample every ~2 viewBox px

STROKE_TO_NAME = {
    "#ed230d": "red", "#ff9400": "orange", "#f9e231": "yellow",
    "#1eb100": "green", "#00a1fe": "blue", "#a410fb": "purple",
    "#000000": "black",
}

svg = open(SVG).read()
edges = []
for m in re.finditer(r'<path\b([^>]*?)/?>', svg):
    attrs = m.group(1)
    stroke = re.search(r'stroke="([^"]+)"', attrs)
    d = re.search(r' d="([^"]+)"', attrs)
    if not stroke or not d or stroke.group(1) == "none":
        continue
    name = STROKE_TO_NAME.get(stroke.group(1).lower())
    if not name:
        print("WARNING: unmapped stroke", stroke.group(1))
        continue
    path = parse_path(d.group(1))
    L = path.length()
    n = max(8, int(L / SPACING))
    pts = []
    for i in range(n + 1):
        p = path.point(i / n)
        pts.append((round(p.real * SCALE, 1), round(p.imag * SCALE, 1)))
    edges.append({"color": name, "pts": pts})
    print(name, "len(viewBox px):", round(L, 1), "pts:", len(pts))

with open(OUT, "w") as f:
    json.dump({"size": SIZE, "edges": edges}, f)
from collections import Counter
print("edges:", Counter(e["color"] for e in edges))
