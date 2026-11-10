"""Creator Adda Reel v2: voice-over (Microsoft neural voice via edge-tts), kinetic captions,
scene cuts with whoosh/pop sounds and ducked royalty-free music. 1080x1920, 30 fps.

Input (the item's "reel2" object):
  {"music": "uplift|focus|calm", "promo": false, "scene": "myth|mic|edit|thumbnail|celebrate|think",
   "hook":  {"say": "<Hindi in Devanagari, English words in Latin>", "show": "<Roman Hinglish caption, *word* = yellow>",
             "headline": "Big text with <em>red</em> words", "sticker": "RUKO ✋"},
   "steps": [{"say": "...", "show": "...", "title": "Big text with <em>red</em>", "icon": "😃",
              "kicker": "optional chip", "n": true, "note": "optional small line", "theme": "yellow|white|dark|red"}],
   "end":   {"say": "...", "show": "...", "title": "optional, e.g. Aise tips <span>roz</span> chahiye?"}}
"""
import json
import os
import pathlib
import re
import subprocess
import tempfile
import wave

import numpy as np

HERE = pathlib.Path(__file__).parent
MUSIC = HERE.parent / "money" / "music"
FPS = 30
SR = 44100
VOICE = os.environ.get("ADDA_VOICE", "hi-IN-SwaraNeural")
RATE = os.environ.get("ADDA_VOICE_RATE", "+8%")
LEAD, GAP, END_HOLD = 0.15, 0.22, 1.3
THEMES = ["yellow", "white", "dark", "yellow", "white"]


def _dur(path):
    """duration in seconds using ffmpeg only (no ffprobe on the runner)"""
    err = subprocess.run(["ffmpeg", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", err)
    if m:
        h, mi, se = m[-1]
        return int(h) * 3600 + int(mi) * 60 + float(se)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def speak(text, out_mp3):
    """Microsoft neural voice. ADDA_FAKE_TTS=1 makes silent audio of a plausible length (offline tests)."""
    if os.environ.get("ADDA_FAKE_TTS"):
        secs = max(1.2, len(text) * 0.062)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"sine=frequency=220:duration={secs:.2f}",
                        "-af", "volume=0.05", str(out_mp3)], check=True)
        return
    import sys as _sys
    for attempt in range(3):  # separate process: Playwright already owns this thread's event loop
        r = subprocess.run([_sys.executable, "-m", "edge_tts", "--voice", VOICE, f"--rate={RATE}", "--text", text,
                            "--write-media", str(out_mp3)], capture_output=True, text=True)
        if r.returncode == 0 and _dur(out_mp3) > 0.3:
            return
        print("tts retry", attempt, r.stderr[-300:])
    raise RuntimeError("voice-over failed")


def _chunks(show, n=3):
    """split caption into chunks of up to n words; *a few words* -> yellow highlight (may span words)"""
    toks, em = [], False
    for w in show.split():
        start = w.startswith("*"); w2 = w.lstrip("*")
        if start: em = True
        end = w2.rstrip(".,!?;:").endswith("*") or w2.endswith("*")
        clean = w2.replace("*", "")
        toks.append((clean, em))
        if end: em = False
    out = []
    for i in range(0, len(toks), n):
        part = toks[i:i + n]
        html = " ".join(f"<em>{w}</em>" if e else w for w, e in part)
        out.append((html, sum(len(w) for w, _ in part) + 1))
    return out


def _sfx():
    rng = np.random.default_rng(7)
    n = int(.32 * SR); t = np.arange(n) / SR
    from numpy.fft import rfft, irfft
    noise = rng.standard_normal(n)
    f = np.fft.rfftfreq(n, 1 / SR); spec = rfft(noise); spec[(f < 400) | (f > 5000)] = 0
    whoosh = irfft(spec, n) * np.sin(np.pi * t / t[-1]) ** 2
    whoosh = whoosh / (np.abs(whoosh).max() + 1e-9) * .35
    m = int(.08 * SR); x = np.arange(m) / SR
    pop = np.sin(2 * np.pi * (500 * x + 4000 * x * x)) * np.minimum(x / .002, 1) * np.exp(-x / .03) * .45
    return whoosh, pop


def _write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype("<i2").tobytes())


def build_timeline(spec, tmp):
    parts = [("hook", spec["hook"])] + [("step", s) for s in spec.get("steps", [])[:5]] + [("end", spec.get("end") or {})]
    segs, caps, voices = [], [], []
    t = 0.0
    step_no = 0
    for i, (kind, p) in enumerate(parts):
        say = (p.get("say") or "").strip()
        dur_a = 0.0
        if say:
            mp3 = tmp / f"v{i}.mp3"
            speak(say, mp3)
            dur_a = _dur(mp3)
            voices.append((mp3, t + LEAD))
        d = LEAD + dur_a + (END_HOLD if kind == "end" else GAP)
        s = {"kind": kind, "t0": round(t, 3), "t1": round(t + d, 3)}
        if kind == "hook":
            s.update(headline=p.get("headline", ""), sticker=p.get("sticker", ""), art=bool(spec.get("_art")))
        elif kind == "step":
            step_no += 1
            s.update(title=p.get("title", ""), icon=p.get("icon", ""), kicker=p.get("kicker", ""), note=p.get("note", ""),
                     theme=p.get("theme") or THEMES[(step_no - 1) % len(THEMES)],
                     n=(step_no if p.get("n", True) else 0))
        else:
            s.update(title=p.get("title", ""), promo=bool(spec.get("promo")))
        segs.append(s)
        if say and p.get("show"):
            ch = _chunks(p["show"]); tot = sum(w for _, w in ch)
            c0 = t + LEAD
            for html, w in ch:
                c1 = c0 + dur_a * w / tot
                caps.append({"t0": round(c0, 3), "t1": round(c1 + (0.25 if (html, w) == ch[-1] else 0), 3), "html": html})
                c0 = c1
        t += d
    return segs, caps, voices, round(t, 3)


def mix_audio(segs, voices, total, music_name, tmp, out_wav):
    whoosh, pop = _sfx()
    n = int((total + 0.5) * SR)
    fx = np.zeros(n)
    def add(a, at):
        i = int(at * SR); j = min(n, i + len(a))
        if 0 <= i < n: fx[i:j] += a[:j - i]
    for s in segs[1:]:
        add(whoosh, s["t0"] - 0.12)
    for s in segs:
        if s["kind"] == "step":
            add(pop, s["t0"] + 0.15)
        if s["kind"] == "hook" and s.get("sticker"):
            add(pop, s["t0"] + 0.5)
    _write_wav(tmp / "fx.wav", fx)
    track = MUSIC / f"{music_name or 'uplift'}.mp3"
    if not track.exists():
        track = MUSIC / "uplift.mp3"
    inputs = ["-i", str(track), "-i", str(tmp / "fx.wav")]
    for mp3, _ in voices:
        inputs += ["-i", str(mp3)]
    vs = []
    for k, (_, at) in enumerate(voices):
        ms = int(at * 1000)
        vs.append(f"[{k + 2}:a]aresample={SR},aformat=channel_layouts=mono,adelay={ms}:all=1,apad[v{k}]")
    vmix = "".join(f"[v{k}]" for k in range(len(voices)))
    graph = ";".join(vs + [
        f"{vmix}amix=inputs={len(voices)}:normalize=0,atrim=0:{total:.2f},volume=1.35,asplit=2[vo][sc]",
        f"[0:a]aloop=loop=-1:size=2e9,atrim=0:{total:.2f},aresample={SR},aformat=channel_layouts=mono,volume=0.30[mu]",
        "[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck]",
        f"[1:a]aresample={SR}[fx]",
        f"[vo][duck][fx]amix=inputs=3:normalize=0,afade=t=out:st={max(0, total - 0.8):.2f}:d=0.8,alimiter=limit=0.95[out]",
    ])
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-ac", "2", "-ar", str(SR), str(out_wav)], check=True)


def render(browser, spec, page_html, out_mp4):
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        segs, caps, voices, total = build_timeline(spec, tmp)
        data = {"segs": segs, "caps": caps, "total": total, "scene": spec.get("scene")}
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(page_html(data), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        frames = tmp / "f"; frames.mkdir()
        for f in range(int(total * FPS)):
            page.evaluate(f"setT({f / FPS})")
            page.screenshot(path=str(frames / f"f{f:05d}.jpg"), type="jpeg", quality=90)
        page.close()
        mix_audio(segs, voices, total, spec.get("music"), tmp, tmp / "mix.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(frames / "f%05d.jpg"),
                        "-i", str(tmp / "mix.wav"), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                        str(out_mp4)], check=True)
    return total


if __name__ == "__main__":  # quick test: python3 adda/reel2.py sample.json out.mp4
    import sys
    sys.path.insert(0, str(HERE))
    from build import page_html as _ph
    from playwright.sync_api import sync_playwright
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with sync_playwright() as p:
        b = p.chromium.launch()
        art = HERE / "art" / f"host-{spec.get('scene')}.jpg"
        spec["_art"] = art.exists()
        print("OK", render(b, spec, lambda d: _ph("template-reel2.html", {**d, "scene": spec.get("scene")}), sys.argv[2]))
        b.close()
