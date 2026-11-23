"""Period documents for the Czarina Catherine voyage — Stoker's words, typeset."""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

W, H = 2912, 1638
F = '/home/claude/vm/fonts/'
INK = (40, 30, 24); RED = (150, 32, 26); BLUE = (34, 44, 92)
def font(n, s): return ImageFont.truetype(F + n, s)
RM, IT, SC = 'IMFeENrm28P.ttf', 'IMFeENit28P.ttf', 'IMFeENsc28P.ttf'
OS, OSB, OSI = 'OldStandard-Regular.ttf', 'OldStandard-Bold.ttf', 'OldStandard-Italic.ttf'
HAND = 'PetitFormalScript-Regular.ttf'; HAND2 = 'HomemadeApple-Regular.ttf'
rng = np.random.default_rng(11)

def desk(seed=0):
    r = np.random.default_rng(seed)
    g = ndimage.gaussian_filter(r.normal(0, 1, (H // 2, W // 2)), (0.8, 40))
    g = np.array(Image.fromarray(((g - g.min()) / np.ptp(g) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)) / 255.0
    base = np.array((52, 30, 18), np.float32)
    img = base[None, None, :] * (0.7 + 0.6 * g[..., None])
    yy, xx = np.mgrid[0:H, 0:W]
    light = np.exp(-(((xx - W * 0.42) / (W * 0.55)) ** 2 + ((yy - H * 0.35) / (H * 0.7)) ** 2))
    img = img * (0.45 + 0.9 * light[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def paper(w, h, tone=(236, 224, 196), seed=1, folds=(), age=1.0):
    r = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), np.float32) + tone
    n = ndimage.gaussian_filter(r.normal(0, 1, (h, w)), 1.0)[..., None] * 5
    blot = ndimage.gaussian_filter(r.normal(0, 1, (h // 6, w // 6)), 5)
    blot = np.array(Image.fromarray(((blot - blot.min()) / np.ptp(blot) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC))[..., None] / 255.0
    img = img + n - blot * 22 * age
    yy, xx = np.mgrid[0:h, 0:w]
    e = np.minimum(np.minimum(xx, w - xx), np.minimum(yy, h - yy)).astype(np.float32)
    img = img - (np.exp(-e / 28) * 55 * age)[..., None] * np.array([0.6, 0.8, 1.1])
    for k in range(int(30 * age)):  # foxing
        cx, cy, rr = r.integers(0, w), r.integers(0, h), r.uniform(2, 9)
        d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** .5
        img = img - (np.exp(-(d / rr) ** 2) * r.uniform(15, 40))[..., None] * np.array([0.5, 0.8, 1.2])
    for f in folds:  # ('h', frac) or ('v', frac)
        if f[0] == 'h':
            y = int(h * f[1]); img[y - 2:y + 2] *= 0.88; img[y + 2:y + 7] *= 1.03
        else:
            x = int(w * f[1]); img[:, x - 2:x + 2] *= 0.88; img[:, x + 2:x + 7] *= 1.03
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def place(bg, sheet, cx, cy, rot):
    sh = sheet.convert('RGBA').rotate(rot, expand=True, resample=Image.BICUBIC)
    shadow = Image.new('RGBA', sh.size, (0, 0, 0, 0))
    a = sh.split()[3].filter(ImageFilter.GaussianBlur(22))
    shadow.putalpha(a.point(lambda v: int(v * 0.6)))
    bg.paste((10, 6, 4), (int(cx - sh.width / 2 + 24), int(cy - sh.height / 2 + 30)), shadow)
    bg.paste(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)), sh)
    return bg

def center(d, text, f, y, x0, x1, fill=INK):
    d.text(((x0 + x1) / 2 - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)

def rule(d, x0, x1, y, w=2, fill=INK): d.line([(x0, y), (x1, y)], fill=fill, width=w)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = wd
        else: cur = t
    lines.append(cur); return lines

# ---------------------------------------------------------------- telegram
def telegram(date_line, handed_in, message, seed=3, received='VARNA'):
    w, h = 1500, 1020
    s = paper(w, h, tone=(232, 222, 190), seed=seed, folds=[('h', 0.5)], age=0.8)
    d = ImageDraw.Draw(s)
    rule(d, 60, w - 60, 60, 4); rule(d, 60, w - 60, 70, 1)
    center(d, 'TÉLÉGRAPHES  INTERNATIONAUX', font(OSB, 52), 92, 0, w)
    center(d, 'International Telegraph  ·  Received at  ' + received, font(IT, 38), 160, 0, w)
    rule(d, 60, w - 60, 222, 1); rule(d, 60, w - 60, 230, 3)
    lab = font(SC, 30); hand = font(HAND, 40)
    rows = [('Date', date_line), ('From', 'Rufus Smith, Lloyd’s, London'),
            ('To', 'Lord Godalming, care of H. B. M. Vice-Consul, Varna'), ('Handed in', handed_in)]
    y = 262
    for k, v in rows:
        d.text((90, y + 10), k, font=lab, fill=INK)
        d.text((330, y), v, font=hand, fill=BLUE)
        rule(d, 320, w - 90, y + 64, 1, (120, 100, 80)); y += 86
    d.text((90, y + 30), 'Message', font=lab, fill=INK)
    y += 30; mf = font(HAND, 54)
    for ln in wrap(d, message, mf, w - 420):
        d.text((330, y), ln, font=mf, fill=BLUE); rule(d, 320, w - 90, y + 80, 1, (120, 100, 80)); y += 100
    d.text((90, h - 110), 'No inquiry respecting this telegram can be attended to without its production.', font=font(IT, 26), fill=INK)
    rule(d, 60, w - 60, h - 60, 3)
    return s

# ---------------------------------------------------------------- Lloyd's list
def lloyds():
    w, h = 1250, 1420
    s = paper(w, h, tone=(234, 225, 200), seed=7, folds=[('v', 0.5)], age=1.0)
    d = ImageDraw.Draw(s)
    center(d, 'LLOYD’S  LIST', font(OSB, 96), 60, 0, w)
    center(d, 'and Shipping Gazette', font(IT, 40), 170, 0, w)
    rule(d, 50, w - 50, 232, 4); rule(d, 50, w - 50, 242, 1)
    center(d, 'LONDON, THURSDAY, OCTOBER 5, 1893.', font(OS, 34), 256, 0, w)
    rule(d, 50, w - 50, 306, 1)
    center(d, 'SAILED.', font(OSB, 44), 330, 0, w)
    center(d, 'Thames. — Oct. 4.', font(IT, 34), 392, 0, w)
    f = font(OS, 42); fb = font(OSB, 42)
    rows = [('Hesperus', 'Lisbon'), ('Margaret Ann', 'Leith'), ('Calypso', 'Bordeaux'),
            ('CZARINA CATHERINE', 'Varna, and thence up the Danube'), ('Ocean Queen', 'Oporto'),
            ('Thistle', 'Rotterdam'), ('Endeavour', 'Hamburg')]
    y = 460
    for nm, to in rows:
        star = nm.isupper()
        d.text((90, y), nm if star else nm, font=fb if star else f, fill=INK)
        x = 90 + d.textlength(nm, font=fb if star else f) + 2
        tx = (', from Doolittle’s Wharf, for ' if star else ', for ') + to
        for ln in wrap(d, tx, f, w - x - 80) if not star else [', from Doolittle’s Wharf,', 'for ' + to + '.']:
            d.text((x, y), ln, font=f, fill=INK); y += 58; x = 140
        if star:
            # red-pencil underline and margin mark (Van Helsing found her)
            d.line([(84, y - 4), (w - 120, y - 12)], fill=RED, width=5)
            d.line([(26, y - 96), (44, y - 70), (74, y - 140)], fill=RED, width=6, joint='curve')
        y += 22
    rule(d, 50, w - 50, y + 10, 1)
    center(d, 'ARRIVED.', font(OSB, 44), y + 30, 0, w)
    y += 96
    for ln in ['Gravesend. — Oct. 4. — Harmony, from Riga;', 'Pelican, from Malaga; Ariel, from Smyrna.']:
        d.text((90, y), ln, font=f, fill=INK); y += 58
    return s

# ---------------------------------------------------------------- owner's letter
def owners_letter(to_line, body):
    w, h = 1300, 1200
    s = paper(w, h, tone=(238, 230, 210), seed=21, folds=[('h', 0.34), ('h', 0.67)], age=0.7)
    d = ImageDraw.Draw(s)
    center(d, 'HAPGOOD  &  Co.', font(OSB, 74), 80, 0, w)
    center(d, 'Shipowners and Brokers', font(IT, 38), 172, 0, w)
    center(d, 'LONDON', font(SC, 34), 222, 0, w)
    rule(d, 120, w - 120, 278, 2)
    hand = font(HAND, 52)
    d.text((w - 540, 320), 'October 1893.', font=hand, fill=INK)
    d.text((120, 430), to_line, font=hand, fill=INK)
    y = 540
    for ln in wrap(d, body, hand, w - 260):
        d.text((150, y), ln, font=hand, fill=INK); y += 96
    d.text((w - 620, y + 60), 'For Hapgood & Co.', font=hand, fill=INK)
    d.text((w - 600, y + 150), 'Hapgood', font=font('PinyonScript-Regular.ttf', 110), fill=INK)
    return s

# ---------------------------------------------------------------- Orient Express ticket
def ticket():
    w, h = 1500, 760
    s = paper(w, h, tone=(214, 200, 160), seed=33, age=0.6)
    d = ImageDraw.Draw(s)
    d.rectangle([24, 24, w - 24, h - 24], outline=BLUE, width=6); d.rectangle([40, 40, w - 40, h - 40], outline=BLUE, width=2)
    center(d, 'COMPAGNIE INTERNATIONALE DES WAGONS-LITS', font(OSB, 44), 70, 0, w, BLUE)
    center(d, 'ET DES GRANDS EXPRESS EUROPÉENS', font(OS, 34), 128, 0, w, BLUE)
    center(d, 'ORIENT-EXPRESS', font('PlayfairDisplaySC-Bold.ttf', 96), 182, 0, w, RED)
    rule(d, 80, w - 80, 310, 2, BLUE)
    f = font(OS, 40); hand = font(HAND, 46)
    for i, (k, v) in enumerate([('De', 'Paris'), ('À', 'Varna'), ('Date', '12 Octobre 1893'), ('Places', 'Cinq — Lit-salon')]):
        y = 350 + i * 82
        d.text((120, y + 8), k, font=f, fill=BLUE); d.text((400, y), v, font=hand, fill=INK)
        rule(d, 390, w - 420, y + 66, 1, BLUE)
    # punched hole and stamp
    d.ellipse([w - 330, 380, w - 280, 430], fill=(40, 25, 15))
    t = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    td.ellipse([10, 10, 290, 290], outline=RED + (200,), width=6); td.ellipse([40, 40, 260, 260], outline=RED + (200,), width=2)
    center(td, 'PARIS', font(OSB, 44), 88, 0, 300, RED + (210,)); center(td, '12 OCT 93', font(OS, 36), 148, 0, 300, RED + (210,))
    t = t.rotate(-14, resample=Image.BICUBIC); s.paste(t, (w - 400, 380), t)
    return s

def frame(sheet, rot=-2.0, seed=0, scale=0.92):
    bg = desk(seed)
    k = min(W * scale / sheet.width, H * scale / sheet.height)
    sh = sheet.resize((int(sheet.width * k), int(sheet.height * k)), Image.LANCZOS)
    return place(bg, sh, W / 2, H / 2, rot)
