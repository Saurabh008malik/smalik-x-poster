import sys, os, glob, json, subprocess, math, wave
import numpy as np, soundfile as sf
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, '/home/claude/franklin')
from fire import fire

BASE = '/home/claude/franklin'
IMG = BASE + '/img'
CLIPS = BASE + '/clips'
os.makedirs(CLIPS, exist_ok=True)
SR = 24000
FPS = 24
LEAD = 6.0      # seconds of fire-only intro (title card)
TAIL = 10.0     # seconds after the last word
SLOT = 52.0     # seconds per image, approx

CH_IMGS = {
 1: [2, 1, 38, 40, 63, 62],
 2: [26, 2, 68, 50, 61, 60],
 3: [3, 62, 50, 63, 40, 68],
 4: [4, 5, 42, 43, 34, 3],
 5: [6, 63, 60, 61, 69, 40],
 6: [58, 59, 28, 30, 42, 43, 70, 64],
 7: [8, 9, 10, 20, 4, 5],
 8: [17, 18, 19, 14, 15, 16, 85, 44, 84],
 9: [20, 21, 22, 41, 28, 42, 45],
 10: [84, 51, 77, 69, 6, 63, 45],
 11: [24, 25, 27, 38, 47, 55, 56, 79, 74, 75, 76, 73, 71, 81, 82, 78],
 12: [28, 31, 32, 33, 35, 36, 37, 72, 57, 65, 34],
}

def dur(path):
    i = sf.info(path)
    return i.frames / i.samplerate

def chap_durs():
    return {n: dur(f'{BASE}/audio/ch{n:02d}.wav') for n in range(1, 13)}

# ---------------- audio ----------------
def build_audio():
    durs = chap_durs()
    total = LEAD + sum(durs.values()) + TAIL
    voice_path = BASE + '/voice_full.wav'
    with sf.SoundFile(voice_path, 'w', SR, 1, 'PCM_16') as vf:
        vf.write(np.zeros(int(LEAD * SR), np.float32))
        for n in range(1, 13):
            x, sr = sf.read(f'{BASE}/audio/ch{n:02d}.wav', dtype='float32')
            assert sr == SR
            vf.write(x)
        vf.write(np.zeros(int(TAIL * SR), np.float32))
    # fire bed in 300 s chunks with 4 s crossfades
    fire_path = BASE + '/fire_full.wav'
    cf = int(4 * SR)
    chunk = 300
    with sf.SoundFile(fire_path, 'w', SR, 1, 'PCM_16') as ff:
        prev = None
        written = 0
        seed = 1
        need = int(total * SR)
        while written < need:
            c = fire(chunk + 4, SR, seed=seed); seed += 1
            if prev is None:
                out = c[:-cf]; prev = c[-cf:]
            else:
                t = np.linspace(0, 1, cf, dtype=np.float32)
                mix = prev * np.cos(t * np.pi / 2) + c[:cf] * np.sin(t * np.pi / 2)
                out = np.concatenate([mix, c[cf:-cf]]); prev = c[-cf:]
            out = out[:need - written]
            ff.write(out); written += len(out)
    # mix + loudness + fade out
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', voice_path, '-i', fire_path, '-filter_complex',
           f'[0:a]volume=0.9[v];[1:a]volume=0.05,afade=t=in:st=0:d=4,afade=t=out:st={total-6:.2f}:d=6[f];'
           '[v][f]amix=inputs=2:normalize=0,loudnorm=I=-20:TP=-2:LRA=7',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', BASE + '/audio_final.m4a']
    subprocess.run(cmd, check=True)
    json.dump({'durs': durs, 'total': total, 'lead': LEAD}, open(BASE + '/timeline.json', 'w'))
    print('audio done', total / 60, 'min')

# ---------------- video ----------------
_cache = {}
def find_img(idx):
    return glob.glob(f'{IMG}/fr_{idx:03d}_*')[0]

def canvas(idx):
    W, H = 2400, 1350
    p = f'/tmp/canvas_{idx:03d}.png'
    if os.path.exists(p):
        return p
    im = Image.open(find_img(idx)).convert('RGB')
    # background: cover + blur + dark
    r = max(W / im.width, H / im.height)
    bg = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    l, t = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(45))
    bg = ImageEnhance.Brightness(bg).enhance(0.28)
    # foreground fit
    fr = min((W - 260) / im.width, (H - 150) / im.height)
    fg = im.resize((int(im.width * fr), int(im.height * fr)), Image.LANCZOS)
    # warm grade
    fg = ImageEnhance.Color(fg).enhance(0.8)
    a = np.asarray(fg).astype(np.float32)
    a *= np.array([1.0, 0.93, 0.82], np.float32)
    a = a * 0.88
    fg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    sh = Image.new('RGBA', (fg.width + 80, fg.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((40, 40, 40 + fg.width, 40 + fg.height), fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    x, y = (W - fg.width) // 2, (H - fg.height) // 2
    bg.paste(sh, (x - 40, y - 40), sh)
    bg.paste(fg, (x, y))
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip(1.15 - 0.45 * d ** 2, 0.35, 1.0)
    out = np.asarray(bg).astype(np.float32) * v[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(p)
    return p

def intro_canvas():
    p = '/tmp/canvas_intro.png'
    W, H = 2400, 1350
    im = Image.new('RGB', (W, H), (14, 10, 8))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    g = np.clip(1.0 - 0.6 * d, 0, 1)[..., None] * np.array([48, 30, 14], np.float32)
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) + g, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    fb = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
    fr = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    def ctext(y, s, f, sz, col):
        ft = ImageFont.truetype(f, sz)
        w = dr.textlength(s, font=ft)
        dr.text(((W - w) / 2, y), s, font=ft, fill=col)
    ctext(380, 'THE SLEEPY BIOGRAPHER', fr, 62, (200, 160, 100))
    ctext(520, 'Benjamin Franklin', fb, 150, (240, 220, 180))
    ctext(720, 'The Printer Who Lit Up the World', fr, 70, (220, 195, 150))
    ctext(960, 'A calm biography for sleep  ·  AI-generated narration', fr, 46, (170, 140, 100))
    im.save(p)
    return p

def motion(variant, N, rep):
    # zoompan expressions; N = frames at 12 fps
    if variant == 0:   # slow zoom in
        z = f"1.0+0.12*on/{N}"; x = "(iw-iw/zoom)/2"; y = "(ih-ih/zoom)/2"
    elif variant == 1:  # pan right
        z = "1.14"; x = f"(iw-iw/zoom)*on/{N}"; y = "(ih-ih/zoom)/2"
    elif variant == 2:  # zoom out
        z = f"1.12-0.12*on/{N}"; x = "(iw-iw/zoom)/2"; y = "(ih-ih/zoom)/2"
    else:               # pan left
        z = "1.14"; x = f"(iw-iw/zoom)*(1-on/{N})"; y = "(ih-ih/zoom)/2"
    if rep:             # repeated image: closer detail view
        fx, fy = [(0.3, 0.3), (0.7, 0.35), (0.5, 0.7), (0.3, 0.7)][rep % 4]
        z = "1.45"; x = f"(iw-iw/zoom)*({fx}+0.08*on/{N})"; y = f"(ih-ih/zoom)*{fy}"
    return z, x, y

def render_clip(job):
    k, canv, length_frames, variant, rep = job
    out = f'{CLIPS}/clip_{k:04d}.mp4'
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return k
    secs = length_frames / FPS
    N = int(round(secs * 12))
    z, x, y = motion(variant, N, rep)
    fade = 1.5
    vf = (f"scale=2400:1350,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps=12,fps={FPS},"
          f"fade=t=in:st=0:d={fade},fade=t=out:st={secs - fade:.3f}:d={fade},format=yuv420p")
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', '12', '-i', canv,
           '-vf', vf, '-frames:v', str(length_frames), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24',
           '-threads', '1', '-r', str(FPS), out + '.tmp.mp4']
    subprocess.run(cmd, check=True)
    os.rename(out + '.tmp.mp4', out)
    return k

def plan():
    tl = json.load(open(BASE + '/timeline.json'))
    durs = {int(k): v for k, v in tl['durs'].items()}
    jobs = []
    # intro covers LEAD
    cum = 0.0
    def frames_between(a, b):
        return int(round(b * FPS)) - int(round(a * FPS))
    jobs.append((intro_canvas(), frames_between(0, LEAD), 0, 0))
    cum = LEAD
    used = {}
    for n in range(1, 13):
        D = durs[n] + (TAIL if n == 12 else 0)
        slots = max(1, int(round(D / SLOT)))
        imgs = CH_IMGS[n]
        start = cum
        for s in range(slots):
            a = start + D * s / slots; b = start + D * (s + 1) / slots
            idx = imgs[s % len(imgs)]
            rep = used.get(idx, 0); used[idx] = rep + 1
            jobs.append((canvas(idx), frames_between(a, b), (len(jobs)) % 4, rep))
        cum += D
    return [(i, c, f, v, r) for i, (c, f, v, r) in enumerate(jobs)]

def build_video():
    jobs = plan()
    print('clips:', len(jobs), flush=True)
    with ProcessPoolExecutor(2) as ex:
        for k in ex.map(render_clip, jobs):
            if k % 10 == 0:
                print('clip', k, flush=True)
    with open(BASE + '/clips.txt', 'w') as f:
        for j in jobs:
            f.write(f"file '{CLIPS}/clip_{j[0]:04d}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', BASE + '/clips.txt',
                    '-i', BASE + '/audio_final.m4a', '-c', 'copy', '-movflags', '+faststart', '-shortest',
                    BASE + '/franklin_video1.mp4'], check=True)
    print('video done')

if __name__ == '__main__':
    {'audio': build_audio, 'video': build_video}[sys.argv[1]]()
