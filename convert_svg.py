"""Convert Dan's Passages-shapes.svg (filled ribbons) into paths.json centerlines."""
import re, json
import numpy as np
from PIL import Image, ImageDraw
from svgpathtools import parse_path
from skimage.morphology import skeletonize, remove_small_objects
from collections import deque

SVG = "/Users/medwin/Documents/Thread Hiker/Passages-shapes.svg"
OUT = "/Users/medwin/Documents/Thread Hiker/paths.json"
DBG = "/private/tmp/claude-501/-Users-medwin/9afe5496-15d2-447e-b055-7a85b10f9d29/scratchpad/svg_debug.png"

SCALE = 3
VW, VH = 721, 725
W, H = VW * SCALE, VH * SCALE

svg = open(SVG).read()
paths = {}
for m in re.finditer(r'<path id="(\w+)"[^>]*? d="([^"]+)"', svg):
    paths[m.group(1)] = m.group(2)
print("found:", list(paths.keys()))

def rasterize_evenodd(d):
    """Fill a (possibly multi-subpath) path with even-odd rule via XOR."""
    acc = np.zeros((H, W), dtype=bool)
    path = parse_path(d)
    subpaths = path.continuous_subpaths()
    for sp in subpaths:
        L = sp.length()
        n = max(64, int(L / 0.6))
        pts = [sp.point(i / n) for i in range(n + 1)]
        poly = [(p.real * SCALE, p.imag * SCALE) for p in pts]
        img = Image.new("1", (W, H), 0)
        ImageDraw.Draw(img).polygon(poly, fill=1)
        acc ^= np.asarray(img, dtype=bool)
    return acc

NB = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def bfs_far(pts, start):
    seen = {start: None}
    q = deque([start]); last = start
    while q:
        p = q.popleft(); last = p
        for dy, dx in NB:
            n = (p[0]+dy, p[1]+dx)
            if n in pts and n not in seen:
                seen[n] = p; q.append(n)
    return last, seen

def diameter_path(sk):
    """Longest path through skeleton (ignores spurs)."""
    pts = set(zip(*np.nonzero(sk)))
    if not pts: return []
    a, _ = bfs_far(pts, next(iter(pts)))
    b, seen = bfs_far(pts, a)
    chain = []
    cur = b
    while cur is not None:
        chain.append(cur); cur = seen[cur]
    return [(x, y) for (y, x) in chain]

def skel_chains(sk):
    pts = set(zip(*np.nonzero(sk)))
    def nbrs(p, pool):
        return [(p[0]+dy, p[1]+dx) for dy, dx in NB if (p[0]+dy, p[1]+dx) in pool]
    junctions = {p for p in pts if len(nbrs(p, pts)) >= 3}
    seg = pts - junctions
    visited = set(); chains = []
    ends = [p for p in seg if len(nbrs(p, seg)) <= 1]
    def walk(s):
        ch = [s]; visited.add(s); cur = s
        while True:
            nxt = [q for q in nbrs(cur, seg) if q not in visited]
            if not nxt: break
            cur = nxt[0]; visited.add(cur); ch.append(cur)
        return ch
    for e in ends:
        if e not in visited: chains.append(walk(e))
    for p in seg:
        if p not in visited: chains.append(walk(p))
    for ch in chains:
        for ei in (0, -1):
            j = nbrs(ch[ei], junctions)
            if j:
                ch.insert(0, j[0]) if ei == 0 else ch.append(j[0])
    return [[(x, y) for (y, x) in c] for c in chains if len(c) >= 8]

def rdp(points, eps):
    if len(points) < 3: return points
    pts = np.array(points, dtype=float)
    keep = np.zeros(len(pts), dtype=bool); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1: continue
        seg = pts[b] - pts[a]
        L = np.hypot(*seg) + 1e-9
        rel = pts[a+1:b] - pts[a]
        d = np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / L
        i = np.argmax(d)
        if d[i] > eps:
            m = a + 1 + i
            keep[m] = True
            stack += [(a, m), (m, b)]
    return [tuple(p) for p in pts[keep]]

DRAW = {"red": (201,52,44), "orange": (224,142,27), "yellow": (222,195,43),
        "green": (60,156,58), "blue": (42,151,207), "purple": (157,124,201), "black": (33,31,29)}

result = {"size": W, "edges": []}
overlay = Image.new("RGB", (W, H), (250, 248, 245))
dr = ImageDraw.Draw(overlay)

for name, d in paths.items():
    mask = rasterize_evenodd(d)
    mask = remove_small_objects(mask, 200)
    sk = skeletonize(mask)
    if name == "black":
        chains = skel_chains(sk)
    else:
        chains = [diameter_path(sk)]
    for c in chains:
        if len(c) < 8: continue
        simp = rdp(c, 1.5)
        result["edges"].append({"color": name, "pts": [(round(x,1), round(y,1)) for x,y in simp]})
        dr.line([tuple(p) for p in simp], fill=DRAW[name], width=4)

with open(OUT, "w") as f:
    json.dump(result, f)
overlay.save(DBG)
from collections import Counter
print("edges:", Counter(e["color"] for e in result["edges"]))
print("pts:", sum(len(e["pts"]) for e in result["edges"]))
lens = {c: sum(len(e['pts']) for e in result['edges'] if e['color']==c) for c in DRAW}
print(lens)
