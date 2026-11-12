"""Lamplight Scripture thumbnail (1280x720).
python3 thumb.py <art.jpg> <out.jpg> "<BIG TITLE>" "<subtitle>" [focus_x 0..1]
Dark warm background, artwork filling the right ~58% with a soft blend, big serif title on the left, channel strap.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

art, out, title, sub = sys.argv[1:5]
fx = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
W, H = 1280, 720
bg = Image.new('RGB', (W, H), (16, 11, 8))
# warm glow bottom-left (lamp)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W * 0.22) / (W * 0.6)) ** 2 + ((yy - H * 0.75) / (H * 0.7)) ** 2)
g = np.clip(1.0 - d, 0, 1)[..., None] ** 1.6 * np.array([110, 66, 22], np.float32)
bg = Image.fromarray(np.clip(np.asarray(bg).astype(np.float32) + g, 0, 255).astype(np.uint8))

im = Image.open(art).convert('RGB')
aw = int(W * 0.60); ah = H
r = max(aw / im.width, ah / im.height)
im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
l = int((im.width - aw) * fx); t = (im.height - ah) // 2
im = im.crop((l, t, l + aw, t + ah))
im = ImageEnhance.Color(im).enhance(0.9)
a = np.asarray(im).astype(np.float32) * np.array([1.0, 0.95, 0.86], np.float32) * 0.95
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
# soft left edge mask
mask = np.ones((ah, aw), np.float32)
ramp = np.linspace(0, 1, int(aw * 0.32))
mask[:, :len(ramp)] = ramp ** 1.4
mask = Image.fromarray((mask * 255).astype(np.uint8))
bg.paste(im, (W - aw, 0), mask)
# vignette
v = np.clip(1.1 - 0.35 * np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 2, 0.5, 1)
bg = Image.fromarray(np.clip(np.asarray(bg).astype(np.float32) * v[..., None], 0, 255).astype(np.uint8))

dr = ImageDraw.Draw(bg)
fb = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
fr = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def shadow_text(x, y, s, font, fill):
    for dx, dy in ((3, 3), (2, 2)):
        dr.text((x + dx, y + dy), s, font=font, fill=(0, 0, 0))
    dr.text((x, y), s, font=font, fill=fill)
# strap
f1 = ImageFont.truetype(fr, 30)
shadow_text(56, 64, 'LAMPLIGHT SCRIPTURE', f1, (222, 182, 112))
# title (wrap on words, big)
words = title.split()
lines, cur = [], ''
fsize = 118 if max(len(w) for w in words) <= 8 else 96
f2 = ImageFont.truetype(fb, fsize)
for w in words:
    test = (cur + ' ' + w).strip()
    if dr.textlength(test, font=f2) > W * 0.52 and cur:
        lines.append(cur); cur = w
    else:
        cur = test
lines.append(cur)
y = 130
for ln in lines:
    shadow_text(52, y, ln, f2, (248, 234, 200)); y += int(fsize * 1.08)
f3 = ImageFont.truetype(fr, 46)
shadow_text(56, y + 14, sub, f3, (228, 206, 160))
f4 = ImageFont.truetype(fb, 34)
pill = 'BIBLE STORIES FOR SLEEP'
pw = dr.textlength(pill, font=f4) + 44
py = H - 112
dr.rounded_rectangle((52, py, 52 + pw, py + 60), radius=14, fill=(92, 56, 18))
dr.text((74, py + 11), pill, font=f4, fill=(255, 240, 210))
bg.save(out, quality=92)
print('saved', out)
