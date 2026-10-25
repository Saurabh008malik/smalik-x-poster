"""Generate original royalty-free background tracks (no samples, no third-party audio).
Output: money/music/<name>.mp3 (needs numpy + ffmpeg). Because we synthesise everything ourselves,
there is no copyright / royalty issue."""
import pathlib, subprocess, wave
import numpy as np

SR = 44100
OUT = pathlib.Path(__file__).parent
rng = np.random.default_rng(7)


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, d, s, r):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, max(na, 1))
    e[na:na + nd] = np.linspace(1, s, max(nd, 1))[: max(0, n - na)] if na < n else e[na:na + nd]
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tone(m, dur, kind="pad", amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    if kind == "pad":
        w = sum(np.sin(2 * np.pi * f * (1 + dt) * t) for dt in (-0.003, 0, 0.003)) / 3
        w += 0.25 * np.sin(2 * np.pi * 2 * f * t)
        return amp * w * env(n, 0.5, 0.4, 0.7, 0.6)
    if kind == "pluck":
        w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        return amp * w * np.exp(-t * 5.5) * env(n, 0.005, 0.0, 1.0, 0.05)
    if kind == "bass":
        w = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
        return amp * w * env(n, 0.02, 0.2, 0.8, 0.15)


def kick(amp=1.0):
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 28)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


def hat(amp=1.0):
    n = int(0.06 * SR); x = rng.standard_normal(n)
    x = np.diff(x, prepend=0)  # crude high-pass
    return amp * x * np.exp(-np.arange(n) / SR * 90)


def place(buf, snd, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(snd)); buf[i:j] += snd[: j - i]


def make(name, bpm, chords, bass_roots, arp_pattern, hats=True, kick_beats=(0, 2), bars=12, pad_amp=0.20, arp_amp=0.16):
    beat = 60.0 / bpm; bar = 4 * beat; total = bars * bar + 2.0
    buf = np.zeros(int(total * SR))
    for b in range(bars):
        ch = chords[b % len(chords)]; root = bass_roots[b % len(chords)]; t0 = b * bar
        for m in ch: place(buf, tone(m, bar + 0.6, "pad", pad_amp), t0)
        place(buf, tone(root, bar, "bass", 0.32), t0)
        for k, step in enumerate(arp_pattern):  # 8th-note arpeggio
            if step is None: continue
            place(buf, tone(ch[step % 3] + 12 * (step // 3), beat, "pluck", arp_amp), t0 + k * beat / 2)
        for kb in kick_beats: place(buf, kick(0.55), t0 + kb * beat)
        if hats:
            for h in range(8): place(buf, hat(0.10 if h % 2 else 0.06), t0 + h * beat / 2)
    # echo
    d = int(beat * 0.75 * SR)
    for rep, g in ((1, 0.32), (2, 0.16)): buf[d * rep:] += g * buf[: len(buf) - d * rep]
    # soft limit + fades
    buf = np.tanh(buf * 1.1); buf /= max(1e-9, np.abs(buf).max()); buf *= 0.7
    fade = int(1.5 * SR); buf[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR)); buf[-fade:] *= np.linspace(1, 0, fade)
    wav = OUT / f"{name}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "2", "-b:a", "128k", str(OUT / f"{name}.mp3")], check=True)
    wav.unlink(); print("made", name)


# Am F C G - calm lo-fi
make("calm", 84, [[57, 60, 64], [53, 57, 60], [52, 55, 60], [55, 59, 62]], [45, 41, 48, 43], [0, 1, 2, 1, 0, 1, 2, None])
# C G Am F - bright uplift
make("uplift", 100, [[52, 55, 60], [55, 59, 62], [57, 60, 64], [53, 57, 60]], [48, 43, 45, 41], [0, 2, 1, 2, 0, 2, 1, 2], kick_beats=(0, 1, 2, 3))
# Dm Bb F C - focused / serious
make("focus", 92, [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]], [38, 34, 41, 36], [0, None, 1, 2, 0, None, 2, 1], hats=False)
