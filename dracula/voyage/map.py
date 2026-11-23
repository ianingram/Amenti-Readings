"""Period chart for the Czarina Catherine voyage (Natural Earth, public domain)."""
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

W, H = 2912, 1638
LON0, LON1, LAT0, LAT1 = -13.0, 37.0, 32.6, 55.0
F = '/home/claude/vm/fonts/'
PAPER = (238, 230, 210); INK = (58, 42, 28); LAND = (216, 194, 150); SEA_LINE = (120, 108, 92)

# simple conic-ish: x by lon * cos(mid lat), y by Mercator
def merc(lat): return math.log(math.tan(math.pi/4 + math.radians(lat)/2))
_ym0, _ym1 = merc(LAT0), merc(LAT1)
_k = math.radians(LON1 - LON0)
def P(lon, lat):
    x = (math.radians(lon - LON0)) / _k * W
    y = (_ym1 - merc(lat)) / (_ym1 - _ym0) * H
    return x, y
# keep aspect: scale x by ratio so the map isn't stretched
_asp = (_k / (_ym1 - _ym0)) / (W / H)

def proj(lon, lat):
    x, y = P(lon, lat)
    cx = W / 2
    return cx + (x - cx) * _asp, y

def polys(path):
    g = json.load(open(path))
    for f in g['features']:
        geo = f['geometry']
        cs = geo['coordinates'] if geo['type'] == 'MultiPolygon' else [geo['coordinates']]
        for poly in cs:
            yield poly

def lines(path, names=None):
    g = json.load(open(path))
    for f in g['features']:
        n = f['properties'].get('name') or ''
        if names and n not in names: continue
        geo = f['geometry']
        cs = geo['coordinates'] if geo['type'] == 'MultiLineString' else [geo['coordinates']]
        for l in cs: yield n, l

def base():
    ne = '/home/claude/vm/ne/'
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    for poly in polys(ne + 'ne_50m_land.geojson'):
        md.polygon([proj(*p) for p in poly[0]], fill=255)
        for hole in poly[1:]: md.polygon([proj(*p) for p in hole], fill=0)
    for poly in polys(ne + 'ne_50m_lakes.geojson'):
        md.polygon([proj(*p) for p in poly[0]], fill=0)
    m = np.array(mask) > 127
    dist = ndimage.distance_transform_edt(~m)
    img = np.zeros((H, W, 3), np.float32) + PAPER
    # water lining: thin lines at growing intervals from the shore
    lvls = [7, 15, 24, 35, 49, 66, 88]
    for i, L in enumerate(lvls):
        band = np.abs(dist - L) < 1.15
        a = 0.55 * (1 - i / len(lvls) * 0.75)
        img[band] = img[band] * (1 - a) + np.array(SEA_LINE) * a
    img[m] = img[m] * 0 + LAND
    din = ndimage.distance_transform_edt(m)
    rib = m & (din < 14)
    img[rib] = img[rib] * 0.86 + np.array((176, 150, 108)) * 0.14
    sea = ~m
    img[sea] = img[sea] * 0.93 + np.array((205, 212, 205)) * 0.07
    # coast edge
    edge = m & ~ndimage.binary_erosion(m, iterations=2)
    img[edge] = INK
    # paper grain
    rng = np.random.default_rng(3)
    n = ndimage.gaussian_filter(rng.normal(0, 1, (H, W)), 1.2)[..., None] * 6
    blot = ndimage.gaussian_filter(rng.normal(0, 1, (H // 8, W // 8)), 6)
    blot = np.array(Image.fromarray(((blot - blot.min()) / (np.ptp(blot)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC))[..., None] / 255.0
    img = img + n - blot * 18
    yy, xx = np.mgrid[0:H, 0:W]
    vig = ((xx / W - .5) ** 2 + (yy / H - .5) ** 2) ** .5
    img = img * (1 - 0.35 * vig[..., None] ** 2)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # rivers (Danube, Rhine, Seine, Thames)
    for n_, l in lines(ne + 'ne_50m_rivers_lake_centerlines.geojson', {'Danube', 'Rhine', 'Seine', 'Rhône', 'Po', 'Thames', 'Elbe', 'Dniester', 'Tisza', 'Sava', 'Ebro', 'Tagus', 'Loire', 'Dnieper', 'Prut', 'Siret', 'Drava', 'Main', 'Oder', 'Vistula'}):
        d.line([proj(*p) for p in l], fill=(80, 90, 110), width=3)
    # graticule
    gcol = (150, 130, 105)
    for lon in range(-10, 40, 5):
        pts = [proj(lon, la / 4) for la in range(int(LAT0 * 4), int(LAT1 * 4) + 1)]
        d.line(pts, fill=gcol, width=1)
    for lat in range(35, 56, 5):
        pts = [proj(lo / 4, lat) for lo in range(int(LON0 * 4), int(LON1 * 4) + 1)]
        d.line(pts, fill=gcol, width=1)
    # border frame
    for i, w in ((14, 6), (30, 2)):
        d.rectangle([i, i, W - i, H - i], outline=INK, width=w)
    return im

CITIES = [  # name, lon, lat, dx, dy (label offset), size
    ('LONDON', -0.12, 51.51, 22, -60, 40), ('PARIS', 2.35, 48.86, 24, -14, 36),
    ('Gibraltar', -5.35, 36.14, -40, 26, 34), ('Lisbon', -9.14, 38.72, 22, -20, 28),
    ('Marseilles', 5.37, 43.3, -30, 18, 28), ('Malta', 14.5, 35.9, 18, 10, 28),
    ('VIENNA', 16.37, 48.21, 18, -48, 34), ('BUDA-PESTH', 19.04, 47.5, 20, -10, 32),
    ('Munich', 11.58, 48.14, -20, 16, 28), ('Bucharest', 26.1, 44.43, -150, -46, 28),
    ('VARNA', 27.92, 43.21, -140, 4, 36), ('GALATZ', 28.05, 45.43, -40, -56, 36),
    ('CONSTANTINOPLE', 28.98, 41.01, 18, 6, 30), ('Athens', 23.73, 37.98, -100, 4, 28),
    ('Bistritz', 24.5, 47.13, 16, -30, 28), ('Naples', 14.27, 40.85, 16, -6, 28),
    ('Rome', 12.5, 41.9, 14, -34, 28), ('Strassburg', 7.75, 48.58, 14, 10, 26),
    
]
SEAS = [('ATLANTIC  OCEAN', -10.5, 42.5, 54, 90), ('MEDITERRANEAN   SEA', 13.0, 36.9, 56, 0),
        ('BLACK  SEA', 34.0, 43.4, 48, 0), ('BAY of BISCAY', -6.0, 45.6, 34, 0),
        ('NORTH  SEA', 3.5, 54.0, 40, 0), ('ÆGEAN', 25.1, 37.6, 28, 70), ('ADRIATIC', 15.4, 43.0, 30, -40),
        ('Dardanelles', 24.6, 40.6, 24, 0)]

def labels(im):
    d = ImageDraw.Draw(im)
    for name, lo, la, dx, dy, sz in CITIES:
        x, y = proj(lo, la)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=INK, width=3)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=INK)
        f = ImageFont.truetype(F + ('IMFeENsc28P.ttf' if name.isupper() else 'IMFeENrm28P.ttf'), sz)
        d.text((x + dx, y + dy), name.title() if name.isupper() else name, font=f, fill=INK)
    for name, lo, la, sz, rot in SEAS:
        f = ImageFont.truetype(F + 'IMFeENit28P.ttf', sz)
        x, y = proj(lo, la)
        tw = d.textlength(name, font=f)
        t = Image.new('RGBA', (int(tw) + 20, sz + 30), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((10, 5), name, font=f, fill=(70, 70, 95, 230))
        t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(t, (int(x - t.width / 2), int(y - t.height / 2)), t)
    # cartouche
    cw, ch = 900, 250; cx, cy = W - cw - 70, 70
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=(236, 224, 196), outline=INK, width=4)
    d.rectangle([cx + 12, cy + 12, cx + cw - 12, cy + ch - 12], outline=INK, width=1)
    f1 = ImageFont.truetype(F + 'IMFeENsc28P.ttf', 58); f2 = ImageFont.truetype(F + 'IMFeENit28P.ttf', 38)
    def c(t, f, y):
        d.text((cx + cw / 2 - d.textlength(t, font=f) / 2, y), t, font=f, fill=INK)
    c('The Voyage of the', f2, cy + 28)
    c('Czarina Catherine', f1, cy + 74)
    c('London to Galatz  ·  October 1893', f2, cy + 160)
    return im

# --- routes -------------------------------------------------------------
SHIP = [(0.6, 51.47), (1.6, 51.05), (-1.5, 50.35), (-5.3, 49.1), (-9.6, 45.0), (-9.8, 42.9),
        (-10.0, 38.8), (-9.4, 36.85), (-5.6, 35.95), (-1.5, 36.6), (3.5, 37.6), (8.6, 38.3),
        (11.6, 37.6), (15.6, 36.6), (22.3, 35.8), (24.2, 37.0), (25.4, 38.8), (26.0, 39.85),
        (26.4, 40.15), (26.7, 40.4), (27.8, 40.75), (28.95, 40.95), (29.08, 41.2), (29.4, 41.6),
        (29.2, 42.6), (29.4, 43.6), (29.8, 44.5), (29.68, 45.15), (28.8, 45.18), (28.46, 45.27), (28.05, 45.43)]
TRAIN = [(-0.12, 51.51), (1.31, 51.13), (1.86, 50.95), (2.35, 48.86), (7.75, 48.58), (11.58, 48.14),
         (16.37, 48.21), (19.04, 47.5), (20.15, 46.25), (21.23, 45.75), (22.4, 44.7), (23.8, 44.32),
         (26.1, 44.43), (25.97, 43.9), (25.95, 43.85), (27.92, 43.21)]

def dense(pts, step=4):
    out = []
    P_ = [proj(*p) for p in pts]
    for (x0, y0), (x1, y1) in zip(P_, P_[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n): out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    out.append(P_[-1])
    # smooth
    a = np.array(out); k = 9
    if len(a) > k:
        sm = np.copy(a)
        for j in range(2): sm[:, j] = np.convolve(np.pad(a[:, j], k // 2, mode='edge'), np.ones(k) / k, 'valid')
        a = sm
    return [tuple(p) for p in a]

def frac_at(path, lonlat):
    """fraction along path closest to a place"""
    x, y = proj(*lonlat)
    d = [math.hypot(px - x, py - y) for px, py in path]
    return d.index(min(d)) / (len(path) - 1)

SHIP_D, TRAIN_D = dense(SHIP), dense(TRAIN)

def draw_route(im, path, frac, color, dash=None, width=7, head=None):
    d = ImageDraw.Draw(im)
    n = max(2, int(len(path) * frac))
    seg = path[:n]
    if dash:
        on, off = dash; acc = 0; cur = [seg[0]]
        for a, b in zip(seg, seg[1:]):
            acc += math.hypot(b[0] - a[0], b[1] - a[1])
            if (acc % (on + off)) < on: cur.append(b)
            else:
                if len(cur) > 1: d.line(cur, fill=color, width=width)
                cur = [b]
        if len(cur) > 1: d.line(cur, fill=color, width=width)
    else:
        d.line(seg, fill=color, width=width, joint='curve')
    return seg[-1]

def ship_icon(im, x, y, s=1.0):
    d = ImageDraw.Draw(im)
    k = 26 * s
    d.polygon([(x - k, y), (x + k, y), (x + k * .7, y + k * .45), (x - k * .7, y + k * .45)], fill=INK)
    for dx, h in ((-k * .45, 1.3), (0, 1.6), (k * .45, 1.2)):
        d.line([(x + dx, y), (x + dx, y - k * h)], fill=INK, width=3)
        d.polygon([(x + dx - k * .28, y - k * h * .9), (x + dx + k * .28, y - k * h * .9), (x + dx + k * .22, y - k * .25), (x + dx - k * .22, y - k * .25)], fill=(245, 238, 220), outline=INK)

def stamp(im, x, y, text, sub, color=(140, 30, 25)):
    f1 = ImageFont.truetype(F + 'OldStandard-Bold.ttf', 34); f2 = ImageFont.truetype(F + 'IMFeENit28P.ttf', 30)
    tmp = ImageDraw.Draw(im)
    w = max(tmp.textlength(text, font=f1), tmp.textlength(sub, font=f2)) + 44
    t = Image.new('RGBA', (int(w), 110), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    td.rounded_rectangle([3, 3, w - 4, 106], radius=14, outline=color + (215,), width=4)
    td.text((w / 2 - td.textlength(text, font=f1) / 2, 12), text, font=f1, fill=color + (225,))
    td.text((w / 2 - td.textlength(sub, font=f2) / 2, 58), sub, font=f2, fill=color + (215,))
    t = t.rotate(-4, expand=True, resample=Image.BICUBIC)
    im.paste(t, (int(x), int(y)), t)
