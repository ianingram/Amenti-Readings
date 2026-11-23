"""The Count's lairs — the hunters' plan drawn on Whitbread's New Plan of London (1853,
Library of Congress G&M, free to use). Dracula XXII cues 63–64.
usage: python3 lairs.py <map.png> <fonts-dir> <out.mp4>
Timeline (seconds from cue 63, spoken estimate): Carfax first (cue 63, 'destroy the
Count's lair close at hand'), the route to Piccadilly at 38–46 ('after our visit to
Carfax … the house in Piccadilly'), Godalming and Quincey's branches at 47–53, then the
whole plan held to 72 s ('To this plan I strenuously objected')."""
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

src, fdir, out = sys.argv[1:4]
FPS, DUR, OW, OH = 24, 72.0, 1456, 816
M = Image.open(src).convert('RGB')
MW, MH = M.size
RED, BLUE, PAPER = (150, 28, 22), (28, 44, 92), (244, 234, 210)
F = lambda n, s: ImageFont.truetype(f'{fdir}/{n}', s)
rng = np.random.default_rng(3)

PICC, FENCH, MILE, BERM = (1370, 1580), (2710, 1385), (2950, 1170), (2955, 1820)
CARFAX = (3745, 1445)
ROUTE = [CARFAX, (3700, 1400), (3550, 1348), (3250, 1360), (3000, 1395), FENCH, (2500, 1370), (2250, 1390),
         (2000, 1430), (1800, 1490), (1730, 1520), (1600, 1480), (1460, 1535), PICC]
TO_MILE = [PICC, (1650, 1420), (2050, 1300), (2500, 1230), MILE]
TO_BERM = [PICC, (1700, 1660), (2100, 1760), (2500, 1810), BERM]

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def dense(pts, step=6):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n): out.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    out.append(pts[-1])
    # smooth (Chaikin-ish moving average) and a hand tremor
    a = np.array(out)
    for _ in range(6): a[1:-1] = (a[:-2] + 2 * a[1:-1] + a[2:]) / 4
    a += rng.normal(0, 0.9, a.shape)
    return a

R_ROUTE, R_MILE, R_BERM = dense(ROUTE), dense(TO_MILE), dense(TO_BERM)

def draw_path(d, a, frac, col, w, dash=None):
    n = int(len(a) * max(0, min(1, frac)))
    if n < 2: return None
    seg = a[:n]
    if dash:
        on, off = dash; L = 0; acc = []
        for i in range(1, n):
            L += math.hypot(*(seg[i] - seg[i - 1]))
            if (L % (on + off)) < on: d.line([tuple(seg[i - 1]), tuple(seg[i])], fill=col, width=w)
    else:
        d.line([tuple(p) for p in seg], fill=col, width=w, joint='curve')
    return tuple(seg[-1])

def mark(d, p, col, r=22, w=6):
    x, y = p
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=w)
    d.line([x - r * .6, y - r * .6, x + r * .6, y + r * .6], fill=col, width=w)
    d.line([x - r * .6, y + r * .6, x + r * .6, y - r * .6], fill=col, width=w)

def label(base, p, lines, col, dx, dy, alpha=1.0):
    if alpha <= 0: return
    fonts = [F('fell-sc.ttf', 52), F('fell-i.ttf', 40)]
    m = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    sizes = [m.textbbox((0, 0), t, font=fonts[min(i, 1)]) for i, t in enumerate(lines)]
    w = max(b[2] - b[0] for b in sizes) + 40; h = sum(b[3] - b[1] + 14 for b in sizes) + 26
    tile = Image.new('RGBA', (w + 1, h + 1), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
    d.rounded_rectangle([0, 0, w, h], 10, fill=PAPER + (int(225 * alpha),), outline=col + (int(255 * alpha),), width=3)
    yy = 14
    for i, t in enumerate(lines):
        d.text((20, yy), t, font=fonts[min(i, 1)], fill=col + (int(255 * alpha),)); yy += sizes[i][3] - sizes[i][1] + 14
    x, y = int(p[0] + dx), int(p[1] + dy)
    if dx < 0: x -= w
    base.alpha_composite(tile, dest=(x, y))

def arrow(d, a, col, w):
    if len(a) < 2: return
    (x0, y0), (x1, y1) = a[-2], a[-1]
    ang = math.atan2(y1 - y0, x1 - x0); L = 46
    for s in (-1, 1):
        d.line([x1, y1, x1 - L * math.cos(ang + s * .45), y1 - L * math.sin(ang + s * .45)], fill=col, width=w)

# camera keyframes: (t, cx, cy, w)
CAM = [(0, 2550, 1480, 2500), (6, 2550, 1480, 2450), (15, 3330, 1430, 1250), (33, 3300, 1420, 1150), (38.4, 3300, 1420, 1200),
       (46, 1750, 1500, 1350), (47.2, 1750, 1500, 1350), (53, 2530, 1560, 2600), (72, 2530, 1560, 2540)]
def cam(t):
    for (t0, *a), (t1, *b) in zip(CAM, CAM[1:]):
        if t <= t1:
            e = ease((t - t0) / max(1e-6, t1 - t0)); return [a[i] + (b[i] - a[i]) * e for i in range(3)]
    return CAM[-1][1:]

def fade(t, t0, d=0.8): return max(0, min(1, (t - t0) / d))

ff = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
base = M.convert('RGBA')
import os
ONLY = [float(x) for x in os.environ.get('ONLY','').split(',') if x]
N = int(DUR * FPS)
for i in (range(N) if not ONLY else [int(x*FPS) for x in ONLY]):
    t = i / FPS
    im = base.copy(); d = ImageDraw.Draw(im)
    # 1 · Carfax first (cue 63): the arrow east to Purfleet
    if t >= 12:
        a = dense([(3330, 1500), (3560, 1470), CARFAX])
        draw_path(d, a, ease((t - 12) / 3), RED, 9)
        if t >= 15: arrow(d, a, RED, 9); mark(d, (3500, 1475), RED, 26, 7)
    # 2 · the route to Piccadilly (38.4–46)
    if t >= 38.4:
        draw_path(d, R_ROUTE, (t - 38.4) / 7.4, RED, 8)
    if t >= 46: mark(d, PICC, RED, 30, 8)
    # 3 · Godalming and Quincey's branches (47.2–53)
    if t >= 47.6:
        draw_path(d, R_MILE, (t - 47.6) / 3.6, BLUE, 7, dash=(26, 14))
        if t >= 51.2: mark(d, MILE, BLUE, 26, 7)
    if t >= 49.2:
        draw_path(d, R_BERM, (t - 49.2) / 3.8, BLUE, 7, dash=(26, 14))
        if t >= 53: mark(d, BERM, BLUE, 26, 7)
    label(im, (3500, 1475), ['Carfax, Purfleet', '29 boxes · first'], RED, -40, 50, fade(t, 15.5))
    label(im, PICC, ['347 Piccadilly', '9 boxes · all of us'], RED, 40, 40, fade(t, 46.3))
    label(im, MILE, ['Mile End New Town', 'Chicksand St · 6 boxes'], BLUE, 40, -170, fade(t, 51.5))
    label(im, BERM, ['Bermondsey', 'Jamaica Lane · 6 boxes'], BLUE, 40, 30, fade(t, 53.3))
    if t >= 55:
        label(im, (1290, 2020), ['The Count’s Lairs', '3 October · fifty boxes of earth', 'Godalming & Quincey east — the rest at Piccadilly'], RED, 0, 0, fade(t, 55, 1.2))
    cx, cy, w = cam(t); h = w * OH / OW
    cx = min(max(cx, w / 2), MW - w / 2); cy = min(max(cy, h / 2), MH - h / 2)
    fr = im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((OW, OH), Image.LANCZOS).convert('RGB')
    if t < 1.2:  # fade up from black
        fr = Image.blend(Image.new('RGB', fr.size), fr, t / 1.2)
    if ONLY: fr.save(f'prev-{t:.1f}.jpg', quality=80)
    else: ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print('wrote', out)
