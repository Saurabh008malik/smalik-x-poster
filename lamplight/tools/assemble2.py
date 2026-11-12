"""Lamplight Scripture assembler (v2 visuals, 11 Nov 2026 rules from Saurabh):
every picture fills the whole 16:9 frame, slow zoom in/out on wide pictures, slow top-to-bottom pan on tall
pictures so nothing important is cut off, soft fades between pictures.

Usage:
  python3 assemble2.py <project_dir> audio
  python3 assemble2.py <project_dir> video
project_dir holds: audio/chNN.wav, img/*.jpg + img/sources.json, ch_imgs.json ({"1": [file, ...], ...}), meta.json
meta.json: {"channel": "LAMPLIGHT SCRIPTURE", "title": "...", "subtitle": "...", "out": "name.mp4", "cache": "lp1"}
"""
import sys, os, json, subprocess, math
import numpy as np, soundfile as sf
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, '/home/claude/lamplight/tools')
from fire import fire

BASE = sys.argv[1].rstrip('/')
IMG = BASE + '/img'
CLIPS = BASE + '/clips'
os.makedirs(CLIPS, exist_ok=True)
META = json.load(open(BASE + '/meta.json'))
CACHE = f"/tmp/{META.get('cache', 'lp')}_"
SR = 24000
FPS = 24
LEAD = 6.0
TAIL = 10.0
SLOT = 48.0          # seconds per picture, approx
W, H = 2400, 1350    # working frame (16:9), output 1920x1080
FADE = 1.3

def dur(path):
    i = sf.info(path); return i.frames / i.samplerate

def chap_durs():
    return {n: dur(f'{BASE}/audio/ch{n:02d}.wav') for n in range(1, 13)}

# ---------------- audio (same recipe as The Sleepy Biographer, quieter fire) ----------------
def build_audio():
    durs = chap_durs()
    total = LEAD + sum(durs.values()) + TAIL
    voice_path = BASE + '/voice_full.wav'
    with sf.SoundFile(voice_path, 'w', SR, 1, 'PCM_16') as vf:
        vf.write(np.zeros(int(LEAD * SR), np.float32))
        for n in range(1, 13):
            x, sr = sf.read(f'{BASE}/audio/ch{n:02d}.wav', dtype='float32'); assert sr == SR
            vf.write(x)
        vf.write(np.zeros(int(TAIL * SR), np.float32))
    fire_path = BASE + '/fire_full.wav'
    cf = int(4 * SR); chunk = 300
    with sf.SoundFile(fire_path, 'w', SR, 1, 'PCM_16') as ff:
        prev = None; written = 0; seed = 1; need = int(total * SR)
        while written < need:
            c = fire(chunk + 4, SR, seed=seed); seed += 1
            if prev is None:
                out = c[:-cf]; prev = c[-cf:]
            else:
                t = np.linspace(0, 1, cf, dtype=np.float32)
                mix = prev * np.cos(t * np.pi / 2) + c[:cf] * np.sin(t * np.pi / 2)
                out = np.concatenate([mix, c[cf:-cf]]); prev = c[-cf:]
            out = out[:need - written]; ff.write(out); written += len(out)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', voice_path, '-i', fire_path, '-filter_complex',
           f'[0:a]volume=0.9[v];[1:a]volume=0.045,afade=t=in:st=0:d=4,afade=t=out:st={total-6:.2f}:d=6[f];'
           '[v][f]amix=inputs=2:normalize=0,loudnorm=I=-20:TP=-2:LRA=7',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', BASE + '/audio_final.m4a']
    subprocess.run(cmd, check=True)
    json.dump({'durs': durs, 'total': total, 'lead': LEAD}, open(BASE + '/timeline.json', 'w'))
    print('audio done', round(total / 60, 1), 'min')

# ---------------- pictures ----------------
def grade(im):
    """Warm, slightly darkened lamplight grade, gentle vignette, full frame."""
    im = ImageEnhance.Color(im).enhance(0.85)
    a = np.asarray(im).astype(np.float32)
    a *= np.array([1.0, 0.94, 0.84], np.float32)
    a *= 0.86
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = np.clip(1.12 - 0.38 * d ** 2, 0.45, 1.0)
    a *= v[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def canvas(fn):
    """Returns (path, kind). kind 'wide' = 2400x1350 cover; 'tall' = 2400 x taller (for vertical pan)."""
    stem = os.path.splitext(os.path.basename(fn))[0]
    im = Image.open(f'{IMG}/{fn}').convert('RGB')
    ar = im.width / im.height
    if ar >= 1.45:
        kind = 'wide'; p = f'{CACHE}{stem}_wide.png'
        if not os.path.exists(p):
            r = max(W / im.width, H / im.height)
            big = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
            l = (big.width - W) // 2; t = int((big.height - H) * 0.42)   # bias slightly to the top (faces/horizons)
            grade(big.crop((l, t, l + W, t + H))).save(p)
    else:
        kind = 'tall'; p = f'{CACHE}{stem}_tall.png'
        if not os.path.exists(p):
            r = W / im.width
            hh = min(int(im.height * r), int(H * 2.3))      # cap very tall pictures
            big = im.resize((W, int(im.height * r)), Image.LANCZOS)
            t = (big.height - hh) // 2
            big = big.crop((0, t, W, t + hh))
            if hh <= H + 40:                                # near-square and short: just cover the frame
                r2 = H / big.height
                big = big.resize((int(big.width * r2) + 1, H), Image.LANCZOS)
                l = (big.width - W) // 2; big = big.crop((l, 0, l + W, H)); kind = 'wide'
                p = f'{CACHE}{stem}_wide.png'; grade(big).save(p)
            else:
                g = grade(big)
                pw = int(round(hh * 16 / 9))               # pad to 16:9: zoompan crops a 2400x1350 window and pans down
                pad = Image.new('RGB', (pw, hh), (8, 6, 5))
                pad.paste(g, ((pw - W) // 2, 0)); pad.save(p)
    return p, kind

def intro_canvas():
    p = f'{CACHE}intro.png'
    im = Image.new('RGB', (W, H), (12, 9, 7))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.55) / (H / 2)) ** 2)
    g = np.clip(1.0 - 0.55 * d, 0, 1)[..., None] * np.array([70, 44, 18], np.float32)
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) + g, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    fb = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
    fr = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    def ctext(y, s, f, sz, col):
        ft = ImageFont.truetype(f, sz); w = dr.textlength(s, font=ft); dr.text(((W - w) / 2, y), s, font=ft, fill=col)
    ctext(330, META.get('channel', 'LAMPLIGHT SCRIPTURE'), fr, 60, (214, 172, 104))
    t1 = META['title']
    sz = 140 if len(t1) < 22 else (110 if len(t1) < 30 else 86)
    ctext(470, t1, fb, sz, (244, 226, 188))
    ctext(700, META.get('subtitle', ''), fr, 66, (222, 198, 150))
    ctext(950, 'Bible stories for sleep  ·  AI-generated narration', fr, 44, (176, 146, 102))
    im.save(p); return p

def render_clip(job):
    k, canv, kind, frames, variant = job
    out = f'{CLIPS}/clip_{k:04d}.mp4'
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return k
    secs = frames / FPS
    N = int(round(secs * 12))
    if kind == 'wide':
        z = f"1.0+0.09*on/{N}" if variant % 2 == 0 else f"1.09-0.09*on/{N}"
        x = "(iw-iw/zoom)/2"; y = "(ih-ih/zoom)*0.45"
    else:
        # padded 16:9 canvas: zoom so the window is exactly the picture's width, then pan top->bottom or bottom->up
        zc = f"iw/{W}"
        z = zc; x = "(iw-iw/zoom)/2"
        ramp = f"clip((on-{int(FADE*12)})/{max(N-2*int(FADE*12),1)},0,1)"
        y = f"(ih-ih/zoom)*{ramp}" if variant % 2 == 0 else f"(ih-ih/zoom)*(1-{ramp})"
    vf = (f"zoompan=z='{z}':x='{x}':y='{y}':d={N+2}:s=1920x1080:fps=12,fps={FPS},tpad=stop_mode=clone:stop_duration=2,"
          f"fade=t=in:st=0:d={FADE},fade=t=out:st={secs - FADE:.3f}:d={FADE},format=yuv420p")
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', canv, '-vf', vf, '-frames:v', str(frames),
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-threads', '1', '-r', str(FPS), out + '.tmp.mp4']
    subprocess.run(cmd, check=True)
    os.rename(out + '.tmp.mp4', out)
    return k

def plan():
    tl = json.load(open(BASE + '/timeline.json'))
    durs = {int(k): v for k, v in tl['durs'].items()}
    ch_imgs = {int(k): v for k, v in json.load(open(BASE + '/ch_imgs.json')).items()}
    def frames_between(a, b): return int(round(b * FPS)) - int(round(a * FPS))
    jobs = [(intro_canvas(), 'wide', frames_between(0, LEAD), 0)]
    cum = LEAD
    for n in range(1, 13):
        D = durs[n] + (TAIL if n == 12 else 0)
        imgs = ch_imgs[n]
        slots = max(len(imgs), int(round(D / SLOT)))
        for s in range(slots):
            a = cum + D * s / slots; b = cum + D * (s + 1) / slots
            fn = imgs[s % len(imgs)]
            p, kind = canvas(fn)
            jobs.append((p, kind, frames_between(a, b), len(jobs)))
        cum += D
    return [(i, c, k, f, v) for i, (c, k, f, v) in enumerate(jobs)]

def build_video():
    jobs = plan()
    print('clips:', len(jobs), flush=True)
    with ProcessPoolExecutor(2) as ex:
        for k in ex.map(render_clip, jobs):
            if k % 10 == 0: print('clip', k, flush=True)
    with open(BASE + '/clips.txt', 'w') as f:
        for j in jobs: f.write(f"file '{CLIPS}/clip_{j[0]:04d}.mp4'\n")
    out = f"{BASE}/{META['out']}"
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', BASE + '/clips.txt',
                    '-i', BASE + '/audio_final.m4a', '-c', 'copy', '-movflags', '+faststart', '-shortest', out], check=True)
    print('video done', out)

if __name__ == '__main__':
    {'audio': build_audio, 'video': build_video}[sys.argv[2]]()
