"""The hunters' train, London to Varna (XXV cue 62): the period chart from map.py, the
train line growing stage by stage with a locomotive at its head, cut with the journey's
paintings. Dates from the text only: Charing Cross on the morning of the 12th, Paris the
same night, the Orient Express night and day, Varna about five o'clock on the 15th.
usage (from dracula/voyage, needs map.py's fonts and Natural Earth files):
    python3 train.py <art-dir> <out.mp4>
"""
import sys, os, math, subprocess, tempfile
from PIL import Image, ImageDraw
import map as M

art, out = sys.argv[1], sys.argv[2]
FPS, OW, OH = 24, 1456, 816
TRAIN_C = (30, 40, 70)
tmp = tempfile.mkdtemp()

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def loco(im, x, y, ang, s=1.0):
    """a small engine drawn side-on, turned along the line"""
    k = 22 * s
    t = Image.new('RGBA', (int(k * 5), int(k * 3)), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    ox, oy = k * .6, k * .8
    d.rectangle([ox, oy + k * .5, ox + k * 2.6, oy + k * 1.3], fill=M.INK)              # boiler
    d.rectangle([ox + k * 2.6, oy, ox + k * 3.6, oy + k * 1.3], fill=M.INK)             # cab
    d.rectangle([ox + k * .4, oy + k * .05, ox + k * .8, oy + k * .5], fill=M.INK)      # chimney
    for cx in (ox + k * .5, ox + k * 1.5, ox + k * 2.9):
        d.ellipse([cx - k * .32, oy + k * 1.2, cx + k * .32, oy + k * 1.84], fill=M.PAPER, outline=M.INK, width=3)
    for j, r in enumerate((.28, .38, .5)):                                              # smoke
        cx, cy = ox + k * (.4 - j * .5), oy - k * (.2 + j * .3)
        d.ellipse([cx - k * r, cy - k * r, cx + k * r, cy + k * r], fill=(120, 110, 96, 150))
    t = t.rotate(-math.degrees(ang) + 180 if abs(ang) > math.pi / 2 else -math.degrees(ang), expand=True, resample=Image.BICUBIC)
    im.paste(t, (int(x - t.width / 2), int(y - t.height / 2 - k * .4)), t)

STAMPS = [((-0.12, 51.51), 'CHARING CROSS', 'morning of the 12th', -110, 70),
          ((2.35, 48.86), 'PARIS', 'the same night', -150, 20),
          ((16.37, 48.21), 'VIENNA', 'the Orient Express', -60, -130),
          ((19.04, 47.5), 'BUDA-PESTH', 'night and day', 20, 20),
          ((27.92, 43.21), 'VARNA', 'the 15th · five o’clock', -300, 50)]
SF = {s[1]: M.frac_at(M.TRAIN_D, s[0]) for s in STAMPS}

BASE = M.base(); M.labels(BASE)

def map_stage(path, dur, f0, f1, box0, box1, reach=0.8):
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS; e = ease(t / dur); f = f0 + (f1 - f0) * ease(t / (dur * reach))
        im = BASE.copy()
        hx, hy = M.draw_route(im, M.TRAIN_D, max(f, .003), TRAIN_C, width=8)
        for ll, txt, sub, dx, dy in STAMPS:
            if f >= SF[txt] - .004:
                x, y = M.proj(*ll); M.stamp(im, x + dx, y + dy, txt, sub, TRAIN_C)
        n = int(len(M.TRAIN_D) * max(f, .003)) - 1
        a = M.TRAIN_D[max(0, n - 12)]; b = M.TRAIN_D[max(1, n)]
        cx = box0[0] + (box1[0] - box0[0]) * e; cy = box0[1] + (box1[1] - box0[1]) * e; w = box0[2] + (box1[2] - box0[2]) * e; h = w * OH / OW
        cx = min(max(cx, w / 2), M.W - w / 2); cy = min(max(cy, h / 2), M.H - h / 2)
        p.stdin.write(im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((OW, OH), Image.LANCZOS).convert('RGB').tobytes())
    p.stdin.close(); p.wait()

def still(path, img, dur, z0=1.0, z1=1.08):
    n = int(dur * FPS)
    vf = (f"scale=2912:1632,zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={OW}x{OH}:fps={FPS},"
          f"fade=t=in:st=0:d=0.5,format=yuv420p")
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-loop', '1', '-i', os.path.join(art, img), '-vf', vf, '-frames:v', str(n),
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', path], check=True)

def place(ll): return M.proj(*ll)
L, PA, VI, BU, VA = place((-0.12, 51.51)), place((2.35, 48.86)), place((16.37, 48.21)), place((19.04, 47.5)), place((27.92, 43.21))
f = lambda ll: M.frac_at(M.TRAIN_D, ll)
PLAN = [
    ('map', 6, 0.0, f((-0.12, 51.51)) + .004, (L[0] + 60, L[1] + 60, 760), (L[0] + 80, L[1] + 70, 700)),
    ('still', 'ch25-charingcross-1.jpg', 4),
    ('still', 'ch25-channel-0.jpg', 3),
    ('still', 'ch25-oe1-1.jpg', 5),                       # Calais, the boat train
    ('map', 5, f((-0.12, 51.51)) + .004, f((2.35, 48.86)) + .004, (L[0] + 80, L[1] + 70, 700), (PA[0], PA[1] - 80, 820)),
    ('still', 'ch25-oe2-3.jpg', 5),                       # Paris, Gare de l'Est, the same night
    ('still', 'ch25-doc-orient-ticket.jpg', 3),
    ('still', 'ch25-oe2-1.jpg', 3),
    ('map', 6, f((2.35, 48.86)) + .004, f((16.37, 48.21)) + .004, (PA[0], PA[1] - 80, 820), (VI[0] - 150, VI[1], 1100)),
    ('still', 'ch25-oe3-0.jpg', 5),                       # the Alps
    ('still', 'ch25-oe3-3.jpg', 3),
    ('still', 'ch25-oe4-2.jpg', 4),                       # Vienna at dusk
    ('still', 'ch25-oe6-3.jpg', 4),                       # the dining car, night and day
    ('map', 5, f((16.37, 48.21)) + .004, f((19.04, 47.5)) + .004, (VI[0] - 150, VI[1], 1100), (BU[0] - 100, BU[1], 1150)),
    ('still', 'ch25-oe5-0.jpg', 5),                       # the Danube at Buda-Pesth
    ('still', 'ch25-oe5-2.jpg', 3),
    ('still', 'ch25-orient-0.jpg', 3),
    ('map', 7, f((19.04, 47.5)) + .004, 1.0, (BU[0] - 100, BU[1], 1150), (VA[0] - 250, VA[1] - 120, 1150)),
    ('still', 'ch25-oe7-0.jpg', 5),                       # Varna, about five o'clock
    ('still', 'ch25-harbour-0.jpg', 4, 1.0, 1.05),
]
parts = []
for k, step in enumerate(PLAN):
    pth = os.path.join(tmp, f'{k:02d}.mp4'); parts.append(pth)
    if step[0] == 'map': map_stage(pth, *step[1:])
    else: still(pth, *step[1:])
    print('part', k, step[0], step[1] if step[0] == 'still' else step[1])
lst = os.path.join(tmp, 'list.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-crf', '22', '-preset', 'slow',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('wrote', out)
