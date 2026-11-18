"""Sleepy Biographer Short (1080x1920) in the standing format (13 Nov 2026):
hook title + 'Full video: link in the description' at top, picture band with slow zoom, burned captions,
red 'SUBSCRIBE - TURN ON THE NOTIFICATION BELL' badge + channel name just below the captions,
spoken end line about the link and subscribing, end card text.
usage: python3 shorts.py spec.json out.mp4
spec: {"hook": "...", "text": "sentences...", "images": [paths], "voice": "bm_george", "speed": 0.74}
"""
import sys, json, re, subprocess, os
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from kokoro_onnx import Kokoro

spec = json.load(open(sys.argv[1])); OUT = sys.argv[2]
W, H, FPS, SR = 1080, 1920, 24, 24000
END_LINE = "The full story is waiting for you. The link is in the description. Subscribe, and tap the bell, for more calm biographies."
k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', spec['text']) if s.strip()]
segs, caps, t = [np.zeros(int(SR * 0.6), np.float32)], [], 0.6
for i, s in enumerate(sents + [END_LINE]):
    a, sr = k.create(s, voice=spec.get('voice', 'bm_george'), speed=spec.get('speed', 0.74), lang='en-gb')
    d = len(a) / SR
    caps.append((t, t + d, s, i == len(sents)))
    segs += [a, np.zeros(int(SR * 0.55), np.float32)]; t += d + 0.55
segs.append(np.zeros(int(SR * 1.2), np.float32)); total = t + 1.2
wav = OUT + '.wav'; sf.write(wav, np.concatenate(segs), SR)
end_start = caps[-1][0]

fb = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
fr = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
fsb = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F_HOOK = ImageFont.truetype(fb, 54); F_SUB = ImageFont.truetype(fr, 34); F_CAP = ImageFont.truetype(fb, 50); F_CAP2 = ImageFont.truetype(fb, 41)
F_BADGE = ImageFont.truetype(fsb, 30); F_CH = ImageFont.truetype(fr, 30); F_END = ImageFont.truetype(fb, 58)

imgs = [Image.open(p).convert('RGB') for p in spec['images']]
BAND_Y, BAND_H = 470, 620
def prep(im):
    r = W / im.width
    h = int(im.height * r)
    if h > BAND_H * 1.25:   # tall: crop around upper-middle
        big = im.resize((W, h), Image.LANCZOS); top = int((h - BAND_H * 1.15) * 0.3)
        big = big.crop((0, top, W, top + int(BAND_H * 1.15)))
    else:
        big = im.resize((W, h), Image.LANCZOS)
    a = np.asarray(ImageEnhance.Color(big).enhance(0.9)).astype(np.float32) * np.array([1, .95, .87]) * 0.95
    big = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    bg = im.resize((W, int(im.height * max(W / im.width, H / im.height))), Image.LANCZOS)
    t0 = (bg.height - H) // 2; bg = bg.crop((0, max(t0, 0), W, max(t0, 0) + H)).resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = Image.fromarray((np.asarray(bg).astype(np.float32) * 0.28).astype(np.uint8))
    return big, bg
preps = [prep(im) for im in imgs]

def wrap(dr, s, font, maxw):
    lines, cur = [], ''
    for w in s.split():
        tst = (cur + ' ' + w).strip()
        if dr.textlength(tst, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = tst
    lines.append(cur); return lines

def ctext(dr, y, s, font, fill, shadow=True):
    w = dr.textlength(s, font=font); x = (W - w) / 2
    if shadow: dr.text((x + 2, y + 2), s, font=font, fill=(0, 0, 0))
    dr.text((x, y), s, font=font, fill=fill)

n = int(total * FPS)
seg_len = end_start / len(preps)
proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                         '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                         '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(n):
    ts = f / FPS
    idx = min(int(ts / seg_len), len(preps) - 1) if ts < end_start else len(preps) - 1
    big, bg = preps[idx]
    local = (ts - idx * seg_len) / max(seg_len, 1) if ts < end_start else 1.0
    z = 1.0 + 0.06 * (local if idx % 2 == 0 else 1 - local)
    zw, zh = int(W / z), int(big.height / z)
    x0 = (W - zw) // 2; y0 = (big.height - zh) // 2
    band = big.crop((x0, y0, x0 + zw, y0 + zh)).resize((W, big.height), Image.BILINEAR)
    fr_im = bg.copy()
    bh = min(big.height, BAND_H)
    by = BAND_Y + (BAND_H - bh) // 2
    fr_im.paste(band.crop((0, (band.height - bh) // 2, W, (band.height - bh) // 2 + bh)), (0, by))
    # fade between pictures
    if ts < end_start:
        edge = min(ts - idx * seg_len, (idx + 1) * seg_len - ts)
        if idx > 0 and ts - idx * seg_len < 0.5 or (idx < len(preps) - 1 and (idx + 1) * seg_len - ts < 0.5):
            a = max(0.0, min(1.0, edge / 0.5))
            fr_im = Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), fr_im, 0.35 + 0.65 * a)
    dr = ImageDraw.Draw(fr_im)
    y = 150
    for ln in wrap(dr, spec['hook'], F_HOOK, W - 120):
        ctext(dr, y, ln, F_HOOK, (238, 196, 110)); y += 66
    ctext(dr, y + 6, 'Full video: link in the description', F_SUB, (236, 230, 218))
    cap_y = 1180
    if ts >= end_start:
        for i, (s, col) in enumerate((('Watch the full video', (250, 246, 236)), ('Link in the description', (238, 196, 110)), ('Subscribe and tap the bell', (250, 246, 236)))):
            ctext(dr, cap_y + i * 72, s, F_END if i < 2 else F_CAP, col)
        badge_y = cap_y + 250
    else:
        cur = [c for c in caps if c[0] - 0.05 <= ts < c[1] + 0.5 and not c[3]]
        fnt, lh = F_CAP, 64
        lines = wrap(dr, cur[0][2], fnt, W - 140) if cur else []
        if len(lines) > 4:
            fnt, lh = F_CAP2, 52; lines = wrap(dr, cur[0][2], fnt, W - 120)
        for i, ln in enumerate(lines[:5]): ctext(dr, cap_y + i * lh, ln, fnt, (250, 248, 240))
        badge_y = cap_y + 280
    btxt = 'SUBSCRIBE  •  TURN ON THE NOTIFICATION BELL'
    bw = dr.textlength(btxt, font=F_BADGE) + 48
    bx = (W - bw) / 2
    dr.rounded_rectangle((bx, badge_y, bx + bw, badge_y + 58), radius=6, fill=(200, 30, 36))
    dr.text((bx + 24, badge_y + 12), btxt, font=F_BADGE, fill=(255, 255, 255))
    ctext(dr, badge_y + 86, 'T H E   S L E E P Y   B I O G R A P H E R', F_CH, (224, 200, 150), shadow=False)
    if ts < 0.4: fr_im = Image.blend(Image.new('RGB', (W, H)), fr_im, ts / 0.4)
    proc.stdin.write(fr_im.tobytes())
proc.stdin.close(); proc.wait(); os.remove(wav)
print('short done', OUT, round(total, 1), 's')
