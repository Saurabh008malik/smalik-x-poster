"""Calm animated segments for The Sleepy Biographer (27 Nov 2026 upgrade): title, chapter cards, quote cards, journey maps.
Pure Python (Pillow + numpy) piped to ffmpeg; slow eases, drifting dust motes, light film grain, no flashes.
"""
import subprocess, math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1920, 1080, 24
FD = '/home/claude/fonts/'
GLOOCK = FD + 'Gloock-Regular.ttf'
CRIM = FD + 'CrimsonPro.ttf'
CRIMI = FD + 'CrimsonPro-Italic.ttf'
GOLD = (222, 184, 112); CREAM = (244, 232, 206); DIM = (186, 160, 120)

def ease(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)

def font(path, size):
    f = ImageFont.truetype(path, size)
    try:
        if 'Crimson' in path: f.set_variation_by_axes([420])
    except Exception: pass
    return f

def spaced(s, n=1):
    return (' ' * n).join(s)

def bg_from_image(path, dim=0.30, blur=18, scale=1.12):
    im = Image.open(path).convert('RGB')
    BW, BH = int(W * scale), int(H * scale)
    r = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    l, t = (im.width - BW) // 2, int((im.height - BH) * 0.35)
    im = im.crop((l, t, l + BW, t + BH)).filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Color(im).enhance(0.7)
    a = np.asarray(im).astype(np.float32) * np.array([1.0, 0.92, 0.80]) * dim
    return a

def bg_plain(scale=1.12, warm=(64, 40, 20)):
    BW, BH = int(W * scale), int(H * scale)
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    d = np.sqrt(((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH * 0.55) / (BH / 2)) ** 2)
    g = np.clip(1.0 - 0.6 * d, 0, 1)[..., None] * np.array(warm, np.float32)
    return g + np.array([12, 9, 7], np.float32)

_vig = None
def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = np.clip(1.1 - 0.42 * d ** 2, 0.4, 1.0)[..., None]
    return _vig

class Dust:
    def __init__(self, n=46, seed=3):
        rnd = random.Random(seed)
        self.p = [[rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.2, 3.4), rnd.uniform(-6, 6), rnd.uniform(-9, -2),
                   rnd.uniform(0, 6.28), rnd.uniform(0.25, 0.7)] for _ in range(n)]
    def layer(self, t):
        im = Image.new('L', (W // 2, H // 2), 0); d = ImageDraw.Draw(im)
        for x, y, r, vx, vy, ph, a in self.p:
            px = ((x + vx * t + 14 * math.sin(t * 0.3 + ph)) % W) / 2; py = ((y + vy * t) % H) / 2
            al = a * (0.6 + 0.4 * math.sin(t * 0.8 + ph))
            d.ellipse((px - r, py - r, px + r, py + r), fill=int(255 * al))
        im = im.filter(ImageFilter.GaussianBlur(1.6)).resize((W, H), Image.BILINEAR)
        return np.asarray(im).astype(np.float32)[..., None] / 255.0

class Writer:
    def __init__(self, out, secs):
        self.n = int(round(secs * FPS)); self.secs = secs
        self.p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                   '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21',
                                   '-pix_fmt', 'yuv420p', '-threads', '2', out + '.tmp.mp4'], stdin=subprocess.PIPE)
        self.out = out
    def put(self, a):
        self.p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
    def close(self):
        self.p.stdin.close(); self.p.wait(); os.rename(self.out + '.tmp.mp4', self.out)

def text_layer(items):
    """items: list of (text, fontpath, size, color, y_center, x_center or None, tracking)"""
    layers = []
    for s, fp, sz, col, yc, xc, *rest in items:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); f = font(fp, sz)
        w = d.textlength(s, font=f); bb = d.textbbox((0, 0), s, font=f)
        x = (W - w) / 2 if xc is None else xc - w / 2
        y = yc - (bb[1] + bb[3]) / 2
        # soft glow shadow
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x, y + 3), s, font=f, fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6)); L = Image.alpha_composite(sh, L)
        ImageDraw.Draw(L).text((x, y), s, font=f, fill=col + (255,))
        layers.append(np.asarray(L).astype(np.float32) / 255.0)
    return layers

def comp(base, layer, alpha, dy=0):
    rgb, a = layer[..., :3] * 255.0, layer[..., 3:4] * alpha
    if dy:
        rgb = np.roll(rgb, int(dy), axis=0); a = np.roll(a, int(dy), axis=0)
    return base * (1 - a) + rgb * a

def finish(frame, t, dust, grain_rng):
    f = frame * vignette()
    if dust is not None:
        f = f + dust.layer(t) * np.array([255, 226, 180], np.float32) * 0.55
    f = f + grain_rng.normal(0, 3.2, (H // 4, W // 4, 1)).repeat(4, 0).repeat(4, 1)
    return f

def drift_bg(bg, t, secs, zoom_from=1.0, zoom_to=1.06):
    BH, BW = bg.shape[:2]
    z = zoom_from + (zoom_to - zoom_from) * (t / secs)
    cw, ch = int(BW / (BW / W) / z * (BW / W)), None
    # crop window of size W*s x H*s from oversized bg then resize to W x H
    s = (BW / W) / z
    cw, ch = int(W * s), int(H * s)
    x0, y0 = (BW - cw) // 2, (BH - ch) // 2
    crop = bg[y0:y0 + ch, x0:x0 + cw]
    if crop.shape[1] == W and crop.shape[0] == H: return crop
    im = Image.fromarray(np.clip(crop, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return np.asarray(im).astype(np.float32)

def card(out, secs, bg, items, timings, rule=None, fade_in=1.2, fade_out=1.2, seed=1):
    """timings: list of (start, dur_in) per item; rule: (y, max_halfwidth, start, dur) gold line drawing out from centre."""
    if os.path.exists(out): return out
    wr = Writer(out, secs); layers = text_layer(items); dust = Dust(seed=seed); rng = np.random.default_rng(seed)
    for i in range(wr.n):
        t = i / FPS
        f = drift_bg(bg, t, secs)
        for L, (st, du) in zip(layers, timings):
            e = ease((t - st) / du); f = comp(f, L, e, dy=(1 - e) * 14)
        if rule:
            ry, hw, st, du = rule; e = ease((t - st) / du); w = int(hw * e)
            if w > 2:
                f[ry - 1:ry + 1, W // 2 - w:W // 2 + w] = f[ry - 1:ry + 1, W // 2 - w:W // 2 + w] * 0.2 + np.array(GOLD, np.float32) * 0.8
        f = finish(f, t, dust, rng)
        g = min(ease(t / fade_in), ease((secs - t) / fade_out))
        wr.put(f * g)
    wr.close(); return out

NUM = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']

def chapter_card(out, n, title, bg_img, secs=7.0):
    bg = bg_from_image(bg_img, dim=0.26, blur=14)
    sz = 92 if len(title) < 34 else (76 if len(title) < 46 else 62)
    items = [(spaced('CHAPTER ' + NUM[n].upper(), 1), CRIM, 38, GOLD, 430, None),
             (title, GLOOCK, sz, CREAM, 540, None)]
    return card(out, secs, bg, items, [(0.6, 1.6), (1.4, 1.8)], rule=(625, 230, 2.0, 2.2), seed=n)

def quote_card(out, quote_lines, attribution, bg_img=None, secs=12.0):
    bg = bg_from_image(bg_img, dim=0.22, blur=20) if bg_img else bg_plain()
    n = len(quote_lines); y0 = 540 - (n - 1) * 46 - 40
    items = [(l, CRIMI, 66, CREAM, y0 + i * 92, None) for i, l in enumerate(quote_lines)]
    items.append((attribution, CRIM, 34, DIM, y0 + n * 92 + 50, None))
    tim = [(0.8 + 0.5 * i, 2.0) for i in range(n)] + [(1.0 + 0.5 * n + 0.6, 2.0)]
    return card(out, secs, bg, items, tim, rule=(y0 + n * 92 - 8, 120, 1.0 + 0.5 * n, 1.6), fade_in=1.5, fade_out=1.5, seed=7)

def title_card(out, channel, title, subtitle, foot, bg_img, secs=24.0):
    bg = bg_from_image(bg_img, dim=0.34, blur=10, scale=1.16)
    items = [(spaced(channel, 1), CRIM, 40, GOLD, 330, None), (title, GLOOCK, 150, CREAM, 490, None),
             (subtitle, CRIMI, 70, (232, 206, 160), 640, None), (foot, CRIM, 34, DIM, 900, None)]
    return card(out, secs, bg, items, [(1.0, 2.0), (2.2, 2.6), (3.6, 2.4), (5.2, 2.0)], rule=(715, 260, 4.2, 2.6),
                fade_in=2.0, fade_out=2.5, seed=11)

# ---------------- journey map ----------------
def journey_map(out, title, caption, stops, bbox, rivers=(), dashed_tail=None, secs=20.0, label_side=None):
    """stops: [(name, lon, lat)], drawn in order; bbox (lon0, lon1, lat0, lat1); rivers: [[(lon,lat),...]]"""
    if os.path.exists(out): return out
    lon0, lon1, lat0, lat1 = bbox
    mx, my, mw, mh = 170, 210, W - 340, H - 380
    kx = math.cos(math.radians((lat0 + lat1) / 2))
    sx = mw / ((lon1 - lon0) * kx); sy = mh / (lat1 - lat0); s = min(sx, sy)
    ox = mx + (mw - (lon1 - lon0) * kx * s) / 2; oy = my + (mh - (lat1 - lat0) * s) / 2
    P = lambda lon, lat: (ox + (lon - lon0) * kx * s, oy + (lat1 - lat) * s)
    # parchment base
    rng = np.random.default_rng(5)
    base = bg_plain(scale=1.0, warm=(70, 50, 28)) + rng.normal(0, 4, (H, W, 1))
    bim = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(bim)
    d.rectangle((mx - 30, my - 30, mx + mw + 30, my + mh + 30), outline=(120, 92, 56), width=2)
    d.rectangle((mx - 40, my - 40, mx + mw + 40, my + mh + 40), outline=(90, 68, 40), width=1)
    if rivers:
        rl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rl)
        for r in rivers: rd.line([P(*q) for q in r], fill=(78, 92, 98, 255), width=4, joint='curve')
        mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).rectangle((mx - 28, my - 28, mx + mw + 28, my + mh + 28), fill=255)
        rl.putalpha(Image.fromarray(np.minimum(np.asarray(rl.getchannel('A')), np.asarray(mask))))
        bim = Image.alpha_composite(bim.convert('RGBA'), rl).convert('RGB'); d = ImageDraw.Draw(bim)
    fsm = font(CRIMI, 30); fnm = font(CRIM, 36); ftt = font(GLOOCK, 64); fcap = font(CRIM, 30)
    tw = d.textlength(title, font=ftt); d.text(((W - tw) / 2, 70), title, font=ftt, fill=CREAM)
    cw = d.textlength(caption, font=fcap); d.text(((W - cw) / 2, H - 120), caption, font=fcap, fill=DIM)
    base = np.asarray(bim).astype(np.float32)
    pts = [P(lon, lat) for _, lon, lat in stops]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(seg)
    draw_t0, draw_t1 = 2.0, secs - 4.0
    wr = Writer(out, secs); dust = Dust(n=30, seed=9)
    # per-stop reveal times
    acc = [0.0]
    for sg in seg: acc.append(acc[-1] + sg)
    reveal = [draw_t0 + (draw_t1 - draw_t0) * a / tot for a in acc]
    for i in range(wr.n):
        t = i / FPS
        im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
        prog = ease((t - draw_t0) / (draw_t1 - draw_t0)) * tot
        # path so far
        path = [pts[0]]; rem = prog; head = pts[0]
        for k, sg in enumerate(seg):
            if rem >= sg: path.append(pts[k + 1]); rem -= sg; head = pts[k + 1]
            else:
                f = rem / sg if sg else 0; head = (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)
                path.append(head); break
        if len(path) > 1: d.line(path, fill=GOLD + (235,), width=5, joint='curve')
        if dashed_tail and t > draw_t1:
            a = P(*dashed_tail[0]); b = P(*dashed_tail[1]); e = ease((t - draw_t1) / 1.5)
            for j in range(12):
                f0, f1 = j / 12, (j + 0.5) / 12
                if f0 > e: break
                d.line((a[0] + (b[0] - a[0]) * f0, a[1] + (b[1] - a[1]) * f0, a[0] + (b[0] - a[0]) * min(f1, e), a[1] + (b[1] - a[1]) * min(f1, e)), fill=DIM + (200,), width=3)
            bx, by = b; al = int(220 * e)
            d.ellipse((bx - 7, by - 7, bx + 7, by + 7), outline=DIM + (al,), width=2)
            nm = dashed_tail[2]; d.text((bx + 14, by - 22), nm, font=fsm, fill=DIM + (al,))
        for k, (nm, lon, lat) in enumerate(stops):
            al = ease((t - reveal[k] + 0.3) / 0.9)
            if al <= 0: continue
            x, y = pts[k]; big = k in (0, len(stops) - 1)
            r = 10 if big else 7
            d.ellipse((x - r, y - r, x + r, y + r), fill=CREAM + (int(255 * al),), outline=GOLD + (int(255 * al),), width=2)
            side = (label_side or {}).get(nm, 'r')
            f = fnm if big else fsm; tw = d.textlength(nm, font=f)
            tx = x + 16 if side == 'r' else (x - 16 - tw if side == 'l' else x - tw / 2)
            ty = y - 22 if side in 'rl' else (y + 14 if side == 'b' else y - 52)
            d.text((tx, ty), nm, font=f, fill=CREAM + (int(255 * al),))
        if prog > 0 and t < draw_t1 + 0.5:
            hx, hy = head; d.ellipse((hx - 12, hy - 12, hx + 12, hy + 12), fill=(255, 226, 160, 90))
        fr = np.asarray(im).astype(np.float32)
        fr = finish(fr, t, dust, rng)
        g = min(ease(t / 1.2), ease((secs - t) / 1.4))
        wr.put(fr * g)
    wr.close(); return out
