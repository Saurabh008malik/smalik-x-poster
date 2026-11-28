"""Poster-style thumbnails (27 Nov 2026 upgrade): one focal public-domain portrait, bold modern serif, 3-5 words, strong contrast."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1280, 720
FD = '/home/claude/fonts/'
def F(n, s):
    f = ImageFont.truetype(FD + n, s)
    try:
        if 'Crimson' in n: f.set_variation_by_axes([600])
    except Exception: pass
    return f

def portrait_layer(path, box_w, crop_top=0.0, zoom=1.0, focus_x=0.5):
    im = Image.open(path).convert('RGB')
    r = max(H * zoom / im.height, box_w / im.width)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    t = int((im.height - H) * crop_top); l = int(max(0, (im.width - box_w) * focus_x)); t = min(t, im.height - H)
    im = im.crop((l, t, l + box_w, t + H))
    im = ImageEnhance.Contrast(im).enhance(1.08); im = ImageEnhance.Color(im).enhance(1.05)
    return im

def base(path, box_w, **kw):
    bg = Image.new('RGB', (W, H), (14, 10, 9))
    a = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 300) / 700) ** 2 + ((yy - 470) / 520) ** 2)
    a += np.clip(1 - d, 0, 1)[..., None] * np.array([86, 50, 22], np.float32)
    bg = Image.fromarray(np.clip(a + 12, 0, 255).astype(np.uint8))
    p = portrait_layer(path, box_w, **kw)
    m = np.ones((H, box_w), np.float32)
    ramp = np.clip(np.arange(box_w) / 230.0, 0, 1)
    m *= ramp[None, :] ** 1.5
    mask = Image.fromarray((m * 255).astype(np.uint8))
    bg.paste(p, (W - box_w, 0), mask)
    return bg

def shadow_text(im, xy, s, f, fill, blur=8, off=4):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + off, xy[1] + off), s, font=f, fill=(0, 0, 0, 230))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).text(xy, s, font=f, fill=fill)

def moon(d, x, y, r, col):
    d.ellipse((x - r, y - r, x + r, y + r), fill=col); d.ellipse((x - r + r * 0.55, y - r - r * 0.15, x + r + r * 0.55, y + r - r * 0.15), fill=(14, 10, 9))


def make(portrait, out, l1, l2, sub, sz1=150, sz2=150, box=660, **kw):
    im = base(portrait, box, **kw)
    d = ImageDraw.Draw(im)
    gold = (232, 190, 110); cream = (250, 240, 218)
    moon(d, 70, 78, 16, gold)
    d.text((100, 62), 'LAMPLIGHT SCRIPTURE', font=F('CrimsonPro.ttf', 30), fill=gold)
    shadow_text(im, (56, 140), l1, F('Gloock-Regular.ttf', sz1), cream)
    shadow_text(im, (56, 140 + sz1 + 10), l2, F('Gloock-Regular.ttf', sz2), cream)
    d = ImageDraw.Draw(im); y = 140 + sz1 + sz2 + 46
    d.rectangle((60, y, 300, y + 4), fill=gold)
    shadow_text(im, (58, y + 22), sub, F('CrimsonPro-Italic.ttf', 48), (240, 214, 168), blur=5, off=2)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((56, 610, 556, 668), radius=8, fill=(120, 74, 30))
    d.text((80, 616), 'BIBLE STORIES FOR SLEEP', font=F('CrimsonPro.ttf', 38), fill=cream)
    im.save(out, quality=92)
if __name__ == '__main__':
    make('/home/claude/lamp7/img/a_as_016.jpg', '/home/claude/lamp7/thumbnail.jpg', 'The First', 'Christmas', 'The Nativity, told slowly', sz1=128, sz2=128, box=700, crop_top=0.2, zoom=1.05, focus_x=0.62)
    make('/home/claude/lamp7/img/a_ng_030.jpg', '/home/claude/lamp7/thumbnail_b.jpg', 'Silent', 'Night', 'The first Christmas, told slowly', sz1=150, sz2=150, box=640, crop_top=0.55, zoom=1.0, focus_x=0.5)
