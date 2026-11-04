"""Warm Mug Radio - builds the next YouTube Short (about 40 s, vertical) from a track in inbox.json.

Each track gives as many different 40 s excerpts as fit in it (about 3-4 for a 3-minute track), so 6 new tracks a month = about 20 Shorts.
Output in warmmug/out_short/: video.mp4 + meta.json. Exit 3 = nothing new to cut.
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "out_short"
WORK = HERE / "work"
# first comment posted by the channel on every Short - one is picked by the day of the year
SHORT_COMMENTS = [
    '☕ Full version of "{name}" is on the channel - long mixes every week.',
    "☕ Want the hour-long version? It's on the channel. Headphones on 🎧",
    '☕ This is a clip from "{name}". The full cozy mix is on the channel.',
    "☕ Full mixes live on the channel - perfect for studying or winding down.",
]

LEN = 40          # seconds per Short
SLOTS = [10, 55, 100, 145, 190, 235, 280, 325, 370]  # excerpt start points; only those that fit inside a track are used

HOOKS = [
    ("POV: it's raining and you have nowhere to be", "rain"),
    ("Autumn evenings hit different with this", "autumn"),
    ("Coffee first. Everything else later.", "morning"),
    ("For the ones who study after midnight", "night"),
    ("Rainy window, warm mug, no notifications", "rain"),
    ("Falling leaves and soft piano", "autumn"),
    ("Sunday morning, no plans, just this", "morning"),
    ("Put this on and finish that one task", "night"),
    ("Close the laptop. Breathe. Press play.", "rain"),
    ("When the house is finally quiet", "night"),
    ("This is your sign to slow down today", "morning"),
    ("Snow outside, music inside", "winter"),
    ("Cozy café beats for your focus", "rain"),
    ("The calm you needed after a long day", "night"),
    ("Soft beats for slow mornings", "morning"),
    ("Let the leaves fall, you're doing fine", "autumn"),
    ("Your study desk, but cozier", "night"),
    ("Tea steam and a quiet playlist", "morning"),
    ("For the walk home in the rain", "rain"),
    ("Deep work starts with the right song", "night"),
    ("Windows fogged up, mind finally calm", "winter"),
    ("A slow song for a fast week", "morning"),
    ("Your late night study playlist", "night"),
    ("Warm drink, cold night, soft jazz", "winter"),
]


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit("command failed")
    return r.stdout


def main():
    inbox = json.loads((HERE / "inbox.json").read_text())
    log_p = HERE / "shorts.json"
    log = json.loads(log_p.read_text()) if log_p.exists() else []
    used = {}
    for e in log:
        used.setdefault(e["track_url"], []).append(e["start"])

    pick, src, dur = None, None, None
    WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    cache = {}
    for slot in SLOTS:                      # first pass uses slot 1 of every track, then slot 2...
        for t in inbox:
            if any(abs(slot - u) < LEN for u in used.get(t["url"], [])):
                continue                    # overlaps a clip already posted from this track
            if t["url"] not in cache:       # download each track once to learn how long it is
                f = WORK / f"short_src_{len(cache)}"
                if Path(t["url"]).exists():
                    f = Path(t["url"])
                else:
                    r = requests.get(t["url"], timeout=180); r.raise_for_status(); f.write_bytes(r.content)
                cache[t["url"]] = (f, float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                "-of", "csv=p=0", str(f)]).strip()))
            f, d = cache[t["url"]]
            if slot + LEN + 2 > d:          # this excerpt would run past the end of the track
                continue
            pick, src, dur = (t, slot), f, d
            break
        if pick:
            break
    if not pick:
        (OUT / "skip.txt").write_text("No new music left to cut into Shorts - waiting for next month's tracks.")
        print("nothing new"); sys.exit(3)

    t, start = pick

    hook, theme = HOOKS[len(log) % len(HOOKS)]
    sys.path.insert(0, str(HERE))
    import art
    frame = art.render_short(hook, theme, OUT, seed=len(log) + 3)

    audio = WORK / "short.m4a"
    sh(["ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(LEN), "-i", str(src),
        "-af", f"afade=t=in:d=1.5,afade=t=out:st={LEN-2.5}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "44100", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(audio)])
    # gentle slow zoom so the Short isn't a frozen picture
    frames = LEN * 30
    sh(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(frame), "-i", str(audio),
        "-filter_complex", f"[0:v]scale=2160:3840,zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':"
                           f"y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30,format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "copy", "-t", str(LEN), "-movflags", "+faststart", str(OUT / "video.mp4")])

    meta = {
        "title": f"{hook} ☕ #lofi #shorts"[:100],
        "description": (f"{hook}.\n\n🎧 \"{t['name']}\" by Warm Mug Radio - cozy jazz hop & lofi for studying, "
                        "working and relaxing. Full mixes every week on the channel.\n\n"
                        "Music created with AI tools and curated by hand.\n\n#lofi #jazzhop #studymusic #chillbeats #shorts"),
        "tags": ["lofi", "lofi shorts", "jazz hop", "study music", "chill beats", "cozy music", "warm mug radio"],
        "minutes": round(LEN / 60, 1),
        "track_url": t["url"], "track": t["name"], "start": pick[1], "hook": hook,
        "comment": SHORT_COMMENTS[int(dt.date.today().strftime("%j")) % len(SHORT_COMMENTS)].format(name=t["name"]),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Built Short: {meta['title']} ({t['name']} from {start}s)")


if __name__ == "__main__":
    main()
