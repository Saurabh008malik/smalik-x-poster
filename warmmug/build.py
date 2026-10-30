"""Warm Mug Radio - builds the next YouTube mix from tracks waiting in warmmug/inbox.json.

Output (in warmmug/out/): video.mp4, thumbnail.jpg, meta.json (title, description, tags, tracks).
Exit code 0 = built, 3 = not enough new music yet (nothing to post).

Usage: python warmmug/build.py [--target-min 60] [--min-min 12]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
WORK = HERE / "work"
XFADE = 4.0  # seconds of crossfade between tracks

DESCRIPTION = """{hook}

☕ Warm Mug Radio - cozy jazz hop and lofi for slow mornings, focused afternoons and quiet nights.
New playlists every Tuesday and Saturday. Grab a warm drink, press play, and take your time.

🎧 Perfect for: studying • working • reading • relaxing • sleeping

Tracklist
{tracklist}

🔔 Subscribe so your next calm hour is always ready.

Music created with AI tools and curated by hand for Warm Mug Radio.

#lofi #jazzhop #studymusic #chillbeats #lofivibes
"""

BASE_TAGS = ["lofi", "lofi music", "lofi vibes", "jazz hop", "chill beats", "study music",
             "relaxing music", "lofi hip hop", "cozy music", "cafe music", "focus music", "warm mug radio"]


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(f"command failed: {' '.join(cmd[:4])} ...")
    return r.stdout


def duration(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())


def ts(sec):
    sec = int(sec)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def load(name, default):
    p = HERE / name
    return json.loads(p.read_text()) if p.exists() else default


def next_title(published):
    used = {p["title"] for p in published}
    for line in (HERE / "titles.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and line.strip() not in used:
            return line.strip()
    return f"Cozy Jazz Hop Lofi Mix No. {len(published) + 1} | Warm Mug Radio ☕"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-min", type=float, default=60)
    ap.add_argument("--min-min", type=float, default=12)
    a = ap.parse_args()

    inbox = load("inbox.json", [])
    published = load("published.json", [])
    used = {u for p in published for u in p.get("track_urls", [])}
    waiting = [t for t in inbox if t["url"] not in used]
    print(f"{len(waiting)} new tracks waiting")

    WORK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    chosen, total = [], 0.0
    for i, t in enumerate(waiting):
        src = WORK / f"src_{i}"
        wav = WORK / f"t_{i}.wav"
        if not wav.exists():
            if Path(t["url"]).exists():  # local file (used for tests)
                src = Path(t["url"])
            else:
                r = requests.get(t["url"], timeout=180)
                r.raise_for_status()
                src.write_bytes(r.content)
            # same format for every track so they join cleanly
            sh(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ar", "44100", "-ac", "2", str(wav)])
        d = duration(wav)
        chosen.append({**t, "file": str(wav), "dur": d})
        total += d - (XFADE if len(chosen) > 1 else 0)
        if total >= a.target_min * 60:
            break

    if total < a.min_min * 60:
        msg = f"Only {total/60:.1f} min of new music waiting (need {a.min_min:.0f}). Nothing posted."
        print(msg)
        (OUT / "skip.txt").write_text(msg)
        sys.exit(3)

    # 1) audio: crossfade chain + gentle fade in/out + loudness for YouTube (-14 LUFS)
    ins, filt, prev = [], [], "0:a"
    for c in chosen:
        ins += ["-i", c["file"]]
    for i in range(1, len(chosen)):
        lab = f"x{i}"
        filt.append(f"[{prev}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[{lab}]")
        prev = lab
    end = total - 5
    filt.append(f"[{prev}]afade=t=in:d=2,afade=t=out:st={end:.2f}:d=5,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    mix = WORK / "mix.m4a"
    sh(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", str(mix)])

    # 2) art
    title = next_title(published)
    sys.path.insert(0, str(HERE))
    import art
    theme = art.render(title, OUT)

    # 3) video: still background, 2 fps keeps the render small and fast
    video = OUT / "video.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", "2", "-i", str(OUT / "background.png"),
        "-i", str(mix), "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-r", "2",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(video)])

    # 4) chapters + description
    lines, start = [], 0.0
    for i, c in enumerate(chosen):
        lines.append(f"{ts(start)} {c['name']}")
        start += c["dur"] - XFADE
    hook = title.split("|")[0].strip() + "."
    mood_tags = {"rain": ["rainy day lofi", "rain lofi"], "autumn": ["autumn lofi", "fall lofi"],
                 "winter": ["winter lofi", "christmas lofi"], "night": ["sleep music", "late night lofi"],
                 "morning": ["morning coffee music", "chillhop"], "ocean": ["ocean sounds", "sleep music"]}[theme]
    meta = {
        "title": title[:100],
        "description": DESCRIPTION.format(hook=hook, tracklist="\n".join(lines)),
        "tags": BASE_TAGS + mood_tags,
        "theme": theme,
        "minutes": round(total / 60, 1),
        "track_urls": [c["url"] for c in chosen],
        "tracks": [c["name"] for c in chosen],
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Built '{title}' - {meta['minutes']} min, {len(chosen)} tracks, theme {theme}")


if __name__ == "__main__":
    main()
