"""Chart of the last pursuit (Dracula XXVI): Galatz, the Pruth and the Sereth, Fundu, the
Bistritza up to the Borgo Pass, Veresti, Bistritz and the Castle — Natural Earth 10m
(public domain), drawn in the voyage chart's manner (map.py).
Two clips:
  python3 moldavia.py rivers <out.mp4>   XXVI cue 72–73, Mina reads the map (~62 s)
  python3 moldavia.py plan   <out.mp4>   XXVI cue 89, Van Helsing's plan (~70 s)
Needs /home/claude/vm/ne/ne_10m_{land,lakes,rivers_europe,rivers_lake_centerlines}.geojson
and the IM Fell / Old Standard fonts in /home/claude/vm/fonts (see map.py)."""
import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NE, F = '/home/claude/vm/ne/', '/home/claude/vm/fonts/'
W, H = 4368, 2457
LON0, LON1, LAT0, LAT1 = 21.0, 31.9, 44.3, 48.5
PAPER = (238, 230, 210); INK = (58, 42, 28); LAND = (216, 194, 150); WATER = (70, 92, 120)
RED, BLUE, BROWN = (150, 28, 22), (30, 44, 92), (92, 60, 26)
K = math.cos(math.radians(46.4))

def proj(lon, lat):
    sx = W / ((LON1 - LON0) * K); sy = H / (LAT1 - LAT0); s = min(sx, sy)
    x = W / 2 + (lon - (LON0 + LON1) / 2) * K * s
    y = H / 2 - (lat - (LAT0 + LAT1) / 2) * s
    return x, y

def feats(path):
    for f in json.load(open(NE + path))['features']:
        g = f['geometry']; p = f['properties']; n = p.get('name') or p.get('NAME') or ''
        if not g: continue
        if g['type'] in ('LineString', 'Polygon'): yield n, g['type'], [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
        else: yield n, g['type'], [c for part in g['coordinates'] for c in (part if g['type'] == 'MultiPolygon' else [part])]

def inbox(cs): return any(LON0 - 2 < x < LON1 + 2 and LAT0 - 2 < y < LAT1 + 2 for x, y in cs[::3] or cs)

RIV = {}
def base():
    im = Image.new('RGB', (W, H), PAPER)
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    for n, t, rings in feats('ne_10m_land.geojson'):
        for r in rings:
            if len(r) > 2 and inbox(r): md.polygon([proj(*p) for p in r], fill=255)
    for n, t, rings in feats('ne_10m_lakes.geojson'):
        for r in rings:
            if len(r) > 2 and inbox(r): md.polygon([proj(*p) for p in r], fill=0)
    land = Image.new('RGB', (W, H), LAND)
    # paper grain on land
    g = (np.random.default_rng(1).normal(0, 6, (H // 4, W // 4))).astype(np.float32)
    g = np.array(Image.fromarray(g).resize((W, H), Image.BICUBIC))
    la = np.clip(np.asarray(land).astype(np.float32) + g[..., None], 0, 255).astype(np.uint8)
    im.paste(Image.fromarray(la), (0, 0), mask)
    # water-lining along the coast (the period chart's ripple lines)
    sea = np.asarray(mask) == 0
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(sea)
    lines = np.zeros_like(dist, bool)
    for k in range(1, 8): lines |= (np.abs(dist - k * 16) < 1.1)
    arr = np.asarray(im).copy(); arr[lines & sea] = (np.array(PAPER) * .55 + np.array(INK) * .45).astype(np.uint8)
    edge = (np.asarray(mask.filter(ImageFilter.FIND_EDGES)) > 0)
    arr[edge] = INK
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    want = {'Danube', 'Prut', 'Siret', 'Bistrița', 'Bistrita', 'Moldova', 'Someșul Mare', 'Mures', 'Olt', 'Trotuș', 'Buzău', 'Dniester', 'Bratul Chillia', 'Bratul Sulina', 'Bratul Sfintu Gheorghe'}
    for src in ('ne_10m_rivers_lake_centerlines.geojson', 'ne_10m_rivers_europe.geojson'):
        for n, t, rings in feats(src):
            if n not in want: continue
            for r in rings:
                if not inbox(r): continue
                pts = [proj(*p) for p in r]
                d.line(pts, fill=WATER, width=5 if n in ('Danube',) else 3, joint='curve')
                RIV.setdefault(n, []).append(pts)
    return im

def fnt(n, s): return ImageFont.truetype(F + n, s)

PLACES = {'GALATZ': (28.05, 45.43), 'BISTRITZ': (24.49, 47.13), 'VERESTI': (26.13, 47.60), 'FUNDU': (26.98, 46.47),
          'BORGO PASS': (25.04, 47.26), 'CASTLE': (25.36, 47.38), 'BUCHAREST': (26.10, 44.43), 'VARNA': (27.92, 43.21)}

def labels(im):
    d = ImageDraw.Draw(im)
    for n, (lon, lat) in PLACES.items():
        if n in ('CASTLE', 'BORGO PASS', 'FUNDU', 'VARNA'): continue
        x, y = proj(lon, lat); d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=INK, width=4); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=INK)
        d.text((x + 16, y - 52), n.title() if n != 'BISTRITZ' else 'Bistritz', font=fnt('IMFeENsc28P.ttf', 54), fill=INK)
    it = fnt('IMFeENit28P.ttf', 50)
    for txt, ll, ang in [('Danube', (27.0, 44.05), 0), ('Pruth', (27.9, 46.7), -62), ('Sereth', (27.15, 45.95), -68),
                         ('Bistritza', (25.95, 46.95), -20), ('Black Sea', (30.4, 44.6), 0)]:
        x, y = proj(*ll); t = Image.new('RGBA', (600, 90), (0, 0, 0, 0)); ImageDraw.Draw(t).text((10, 10), txt, font=it, fill=WATER + (255,))
        t = t.rotate(ang, expand=True, resample=Image.BICUBIC); im.paste(t, (int(x - t.width / 2), int(y - t.height / 2)), t)
    big = fnt('IMFeENsc28P.ttf', 74)
    for txt, ll in [('MOLDAVIA', (26.9, 47.95)), ('WALLACHIA', (24.9, 44.95)), ('TRANSYLVANIA', (23.3, 46.35)), ('BESSARABIA', (29.3, 47.0))]:
        x, y = proj(*ll); d.text((x, y), txt, font=big, fill=(120, 96, 66), anchor='mm')
    # the Carpathians in hachures
    rng = np.random.default_rng(4)
    arc = [(24.6, 47.75), (25.4, 47.4), (25.9, 46.8), (26.1, 46.2), (26.2, 45.7), (25.6, 45.45), (24.6, 45.4), (23.6, 45.35)]
    for (a, b), (c, e) in zip(arc, arc[1:]):
        for k in range(18):
            u = k / 18; lon, lat = a + (c - a) * u + rng.normal(0, .06), b + (e - b) * u + rng.normal(0, .06)
            x, y = proj(lon, lat); s = 22 + rng.random() * 10
            d.line([(x - s, y + s * .5), (x, y - s * .5), (x + s, y + s * .5)], fill=(128, 104, 74), width=3)
    x, y = proj(24.2, 45.75)
    d.text((x, y), 'Carpathian Mountains', font=fnt('IMFeENit28P.ttf', 46), fill=(120, 96, 66), anchor='mm')

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def path_ll(pts, step=5):
    P = [proj(*p) for p in pts]; out = []
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    out.append(P[-1]); a = np.array(out)
    for _ in range(8): a[1:-1] = (a[:-2] + 2 * a[1:-1] + a[2:]) / 4
    return a

def river_path(name, start_ll, end_ll, names=None):
    """the drawn river between two places: shortest path through its densified points"""
    from scipy.spatial import cKDTree
    from scipy.sparse.csgraph import dijkstra
    from scipy.sparse import coo_matrix
    pts = []
    for nm in (names or [name]):
        for piece in RIV.get(nm, []):
            for (x0, y0), (x1, y1) in zip(piece, piece[1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 4))
                pts += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
            pts.append(piece[-1])
    pts = np.array(pts); tree = cKDTree(pts)
    pairs = np.array(list(tree.query_pairs(9)))
    dist = np.hypot(*(pts[pairs[:, 0]] - pts[pairs[:, 1]]).T)
    G = coo_matrix((np.r_[dist, dist], (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(len(pts),) * 2).tocsr()
    i0 = tree.query(proj(*start_ll))[1]; i1 = tree.query(proj(*end_ll))[1]
    _, pred = dijkstra(G, indices=i0, return_predecessors=True)
    path = [i1]
    while path[-1] != i0 and pred[path[-1]] >= 0: path.append(pred[path[-1]])
    a = pts[path[::-1]]
    for _ in range(3): a[1:-1] = (a[:-2] + 2 * a[1:-1] + a[2:]) / 4
    return a

def draw(d, a, frac, col, w, dash=None, offset=0):
    n = int(len(a) * max(0, min(1, frac)))
    if n < 2: return None
    s = a[:n]
    if offset:
        v = np.gradient(s, axis=0); nrm = np.stack([-v[:, 1], v[:, 0]], 1); nrm /= (np.hypot(*nrm.T)[:, None] + 1e-6); s = s + nrm * offset
    if dash:
        on, off = dash; L = 0
        for i in range(1, len(s)):
            L += math.hypot(*(s[i] - s[i - 1]))
            if (L % (on + off)) < on: d.line([tuple(s[i - 1]), tuple(s[i])], fill=col, width=w)
    else: d.line([tuple(p) for p in s], fill=col, width=w, joint='curve')
    return tuple(s[-1])

def stamp(im, x, y, text, sub, col, alpha=1.0):
    if alpha <= 0: return
    f1 = fnt('OldStandard-Bold.ttf', 50); f2 = fnt('IMFeENit28P.ttf', 44)
    m = ImageDraw.Draw(im); w = max(m.textlength(text, font=f1), m.textlength(sub, font=f2)) + 60
    t = Image.new('RGBA', (int(w), 150), (0, 0, 0, 0)); td = ImageDraw.Draw(t); A = lambda v: int(v * alpha)
    td.rounded_rectangle([4, 4, w - 5, 145], radius=18, fill=PAPER + (A(200),), outline=col + (A(225),), width=5)
    td.text((w / 2, 46), text, font=f1, fill=col + (A(235),), anchor='mm'); td.text((w / 2, 104), sub, font=f2, fill=col + (A(225),), anchor='mm')
    t = t.rotate(-3, expand=True, resample=Image.BICUBIC); im.paste(t, (int(x), int(y)), t)

def mark(d, ll, col, r=24, w=7):
    x, y = proj(*ll)
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=w)
    d.line([x - r * .6, y - r * .6, x + r * .6, y + r * .6], fill=col, width=w); d.line([x - r * .6, y + r * .6, x + r * .6, y - r * .6], fill=col, width=w)

def castle(d, ll, s=1.0):
    x, y = proj(*ll); k = 30 * s
    d.polygon([(x - k, y + k), (x - k, y - k * .4), (x - k * .6, y - k * .4), (x - k * .6, y - k), (x - k * .2, y - k), (x - k * .2, y - k * .3),
               (x + k * .2, y - k * .3), (x + k * .2, y - k * 1.5), (x + k * .6, y - k * 1.5), (x + k * .6, y - k * .4), (x + k, y - k * .4), (x + k, y + k)], fill=INK)

def run(out, dur, frame_fn, cam):
    FPS = 24; OW, OH = 1456, 816
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '22', '-preset', 'medium', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    import os
    only = [float(x) for x in os.environ.get('ONLY', '').split(',') if x]
    for i in ([int(x * FPS) for x in only] if only else range(int(dur * FPS))):
        t = i / FPS; im = frame_fn(t)
        for (t0, *a), (t1, *b) in zip(cam, cam[1:]):
            if t <= t1: e = ease((t - t0) / max(1e-6, t1 - t0)); cx, cy, w = [a[k] + (b[k] - a[k]) * e for k in range(3)]; break
        else: cx, cy, w = cam[-1][1:]
        h = w * OH / OW; cx = min(max(cx, w / 2), W - w / 2); cy = min(max(cy, h / 2), H - h / 2)
        fr = im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((OW, OH), Image.LANCZOS)
        if t < 1.0: fr = Image.blend(Image.new('RGB', fr.size), fr, t)
        if only: fr.convert('RGB').save(f'/tmp/mold-{t:.0f}.jpg', quality=82); continue
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    mode, out = sys.argv[1], sys.argv[2]
    B = base(); labels(B)
    G, FU, BI, BO, CA, VE = PLACES['GALATZ'], PLACES['FUNDU'], PLACES['BISTRITZ'], PLACES['BORGO PASS'], PLACES['CASTLE'], PLACES['VERESTI']
    gx, gy = proj(*G); fx, fy = proj(*FU); cx_, cy_ = proj(*CA)
    PRUT = river_path('Prut', (28.2, 45.47), (27.0, 48.0))
    SIRET = river_path('Siret', G, (26.3, 47.9))
    SER_F = river_path('Siret', G, FU)
    BIST = river_path('Bistrița', FU, (25.3, 47.45), names=['Bistrița', 'Bistrita'])
    bx, by = proj(*BI)
    vx, vy = proj(*VE)
    x0_, x1_, y0_, y1_ = min(bx, cx_) - 120, gx + 120, min(cy_, vy) - 230, gy + 150
    WIDE = ((x0_ + x1_) / 2, (y0_ + y1_) / 2, max((x1_ - x0_) * 1.3, (y1_ - y0_) * 1.3 * 1456 / 816))
    if mode == 'rivers':
        # cue 72 from 0 s ('either the Pruth or the Sereth' ~8 s); cue 73 at 36 s ('Pruth more easily navigated' ~45,
        # 'at Fundu, joined by the Bistritza' ~48, 'round the Borgo Pass' ~53, 'as close to Dracula's castle' ~57)
        def fr(t):
            im = B.copy(); d = ImageDraw.Draw(im)
            stamp(im, gx + 30, gy + 40, 'GALATZ', 'the box landed', RED, ease((t - 2) / 1))
            pr = ease((t - 8) / 4); se = ease((t - 12) / 4)
            pa = 1.0 if t < 44 else max(.35, 1 - (t - 44) / 2 * .65)
            draw(d, PRUT, pr, tuple(int(c * pa + 238 * (1 - pa)) for c in BLUE), 9, dash=(30, 16))
            draw(d, SIRET, se, BLUE, 9, dash=(30, 16))
            if t >= 47: draw(d, SER_F, ease((t - 47) / 2.5), RED, 12)
            if t >= 49.5: mark(d, FU, RED); stamp(im, fx + 40, fy - 40, 'FUNDU', 'the Bistritza joins', RED, ease((t - 49.5) / 1))
            if t >= 50: draw(d, BIST, ease((t - 50) / 4), RED, 12)
            if t >= 54: mark(d, BO, RED, 22, 6)
            if t >= 56.5:
                castle(d, CA, 1.1); x, y = proj(*CA); stamp(im, x + 60, y + 40, 'CASTLE DRACULA', 'as close as can be got by water', RED, ease((t - 57) / 1))
            return im
        cam = [(0, *WIDE), (6, gx - 200, gy - 200, 1900), (16, (gx + fx) / 2, (gy + fy) / 2 - 150, 2300), (44, (gx + fx) / 2, (gy + fy) / 2 - 150, 2300),
               (50, (fx + cx_) / 2 + 200, (fy + cy_) / 2, 2300), (58, *WIDE), (62, WIDE[0], WIDE[1], WIDE[2] * .97)]
        run(out, 62, fr, cam)
    else:
        # cue 89 from 'while you, my Lord Godalming' (0 s): launch 0–8; 'John and Quincey guard the bank' ~7–13;
        # 'I will take Madam Mina' ~12; 'from Bistritz over the Borgo' ~38–46; castle ~46; hold to 70
        LAUNCH = np.concatenate([SER_F, BIST])
        VH = np.concatenate([path_ll([G, (27.6, 46.2), (26.6, 47.0), VE]), path_ll([VE, (25.6, 47.45), BI]), path_ll([BI, BO, CA])])
        def fr(t):
            im = B.copy(); d = ImageDraw.Draw(im)
            stamp(im, gx + 30, gy + 40, 'GALATZ', '30 October', INK, 1.0)
            draw(d, SER_F, 1.0, (150, 120, 110), 5); draw(d, BIST, 1.0, (150, 120, 110), 5)
            hl = draw(d, LAUNCH, ease((t - .5) / 9), RED, 12)
            if t >= 4: stamp(im, fx - 560, fy + 120, 'THE LAUNCH', 'Godalming & Harker', RED, ease((t - 4) / 1))
            draw(d, SER_F, ease((t - 7) / 6), BLUE, 7, dash=(26, 14), offset=-34)
            if t >= 10: x, y = proj(27.45, 45.9); stamp(im, x + 40, y, 'ON HORSE', 'Seward & Morris, the bank', BLUE, ease((t - 10) / 1))
            draw(d, VH, ease((t - 14) / 27), BROWN, 9, dash=(14, 10))
            if t >= 24: x, y = proj(*VE); stamp(im, x - 420, y - 200, 'VAN HELSING & MINA', 'by Veresti and Bistritz', BROWN, ease((t - 24) / 1))
            if t >= 40: mark(d, BO, BROWN, 22, 6)
            if t >= 42:
                castle(d, CA, 1.2); x, y = proj(*CA); stamp(im, x + 60, y + 40, 'CASTLE DRACULA', 'over the Borgo', RED, ease((t - 42) / 1))
            return im
        cam = [(0, (gx + fx) / 2, (gy + fy) / 2 - 100, 2200), (12, (gx + fx) / 2, (gy + fy) / 2 - 100, 2300),
               (30, *WIDE), (42, *WIDE), (64, WIDE[0], WIDE[1], WIDE[2] * .96)]
        run(out, 64, fr, cam)
    print('wrote', out)
