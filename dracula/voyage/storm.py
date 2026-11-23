"""The Czarina's storm (XXV cue 68), animated from the four V8 Doré stills.
Each still: pitch and roll, sea heave, slanting rain, its own painted bolt flaring;
every cut lands on a lightning flash. usage: python3 storm2.py <out.mp4> <still0> .. <still3>
"""
import sys, subprocess, math
import numpy as np, cv2

out, stills = sys.argv[1], sys.argv[2:]
FPS, W, H = 24, 1456, 816
TOTAL = 465                                   # = the old czarina-v8-storm.mp4 (19.375 s)
lens = [TOTAL // len(stills)] * len(stills); lens[-1] += TOTAL - sum(lens)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(11)

def noise(seed, scale=3):
    r = np.random.default_rng(seed); acc = np.zeros((H, W), np.float32); amp = 1
    for o in range(4):
        s = int(scale * 2 ** o); acc += amp * cv2.resize(r.random((max(2, H * s // W), s)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC); amp *= .5
    return (acc - acc.min()) / (acc.max() - acc.min())

class Rain:
    def __init__(s, n, ln, ang, spd, a, seed):
        r = np.random.default_rng(seed)
        s.p = r.random((n, 2)) * [W, H]; s.sp = spd * (.7 + .6 * r.random(n)); s.ln = ln * (.6 + .8 * r.random(n))
        s.dx, s.dy = math.sin(math.radians(ang)), math.cos(math.radians(ang)); s.a = a
    def draw(s, f):
        L = np.zeros((H, W), np.float32)
        for (x0, y0), sp, ln in zip(s.p, s.sp, s.ln):
            y = (y0 + sp * f) % (H + 60) - 60; x = (x0 + sp * f * s.dx / s.dy) % W
            cv2.line(L, (int(x), int(y)), (int(x + s.dx * ln), int(y + s.dy * ln)), 1.0, 1, cv2.LINE_AA)
        return cv2.GaussianBlur(L, (3, 3), 0) * s.a

def flash_env(n, strikes):
    e = np.zeros(n, np.float32)
    for f0, st in strikes:
        for k, v in enumerate([1, .3, .85, .45, .28, .16, .09, .05, .02]):
            if 0 <= f0 + k < n: e[f0 + k] = max(e[f0 + k], st * v)
    return e

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)

for si, (path, n) in enumerate(zip(stills, lens)):
    img = cv2.resize(cv2.imread(path), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    gray = img.mean(2)
    # the painted bolt: brightest strokes in the sky
    bolt = ((gray > np.percentile(gray[: H // 2], 99.3)) & (yy < H * .55)).astype(np.float32)
    bolt = cv2.dilate(bolt, np.ones((3, 3))); bolt = cv2.GaussianBlur(bolt, (0, 0), 5) * 1.6
    sea = np.clip((yy - H * .33) / (H * .67), 0, 1) ** 1.1 * (.55 + .45 * noise(si + 20))
    rain = Rain(700, 30, -14, 44, .17, si)
    rain2 = Rain(350, 14, -14, 26, .10, si + 50)
    # a flash at the cut (frame 0) and one or two inside the shot
    env = flash_env(n, [(0, 1.0), (int(n * (.45 + .1 * si % 2)), .65), (n - 9, .4)])
    phase = si * 1.7; sgn = -1 if si % 2 else 1
    z0, z1 = 1.07, 1.13
    for f in range(n):
        t = f / FPS; u = f / (n - 1)
        # sea heave: a rolling swell plus a cross chop
        dy = (9 * np.sin(2 * math.pi * (xx / 420 - t * .5) + phase) + 4 * np.sin(2 * math.pi * (xx / 170 + t * .9)) ) * sea
        dx = 4 * np.sin(2 * math.pi * (yy / 260 + t * .35)) * sea
        fr = cv2.remap(img, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # the ship pitches: camera rolls with the sea
        ang = sgn * 1.8 * math.sin(2 * math.pi * .27 * t + phase)
        z = z0 + (z1 - z0) * (u * u * (3 - 2 * u))
        M = cv2.getRotationMatrix2D((W * .5, H * .55), ang, z)
        M[1, 2] += 10 * math.sin(2 * math.pi * .27 * t + phase + 1.2)
        fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        b = cv2.warpAffine(bolt, M, (W, H))
        e = env[f]
        fr = fr * (1 + 1.2 * e) + .12 * e
        fr += (b * (.15 + 1.4 * e))[..., None] * np.array([1, .98, .94])
        fr += ((rain.draw(f) + rain2.draw(f)) * (1 + 2.2 * e))[..., None] * np.array([.9, .92, .95])
        ff.stdin.write((np.clip(fr, 0, 1) * 255).astype(np.uint8).tobytes())
    print('shot', si, n, 'frames')

ff.stdin.close(); ff.wait(); print('wrote', out)
