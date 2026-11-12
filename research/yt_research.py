"""Collect public YouTube numbers for niche research with yt-dlp (no API key).
Usage: python3 research/yt_research.py config.json out.json
config: {"channels": ["@handle", ...], "searches": ["query", ...], "per_channel": 40, "per_search": 40}
"""
import json, subprocess, sys, time, datetime as dt

cfg = json.load(open(sys.argv[1])); out = {"generated": dt.datetime.utcnow().isoformat() + "Z", "channels": {}, "searches": {}}

def ytdlp(url, n):
    cmd = ["yt-dlp", "--flat-playlist", "--dump-single-json", "--playlist-end", str(n), "--no-warnings", "--extractor-args", "youtubetab:approximate_date", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        if r.returncode != 0:
            return {"error": r.stderr[-600:]}
        return json.loads(r.stdout)
    except Exception as e:
        return {"error": str(e)}

def slim(e):
    return {"id": e.get("id"), "title": e.get("title"), "views": e.get("view_count"), "duration_s": e.get("duration"),
            "uploaded": e.get("upload_date") or e.get("timestamp"), "channel": e.get("channel") or e.get("uploader"),
            "channel_id": e.get("channel_id"), "subs": e.get("channel_follower_count")}

for h in cfg.get("channels", []):
    url = f"https://www.youtube.com/{h}/videos"
    d = ytdlp(url, cfg.get("per_channel", 40))
    if "error" in d:
        out["channels"][h] = d; print("ERR", h, d["error"][:200]); continue
    vids = [slim(e) for e in d.get("entries", []) if e]
    out["channels"][h] = {"title": d.get("title") or d.get("channel"), "subs": d.get("channel_follower_count"),
                          "channel_id": d.get("channel_id"), "description": (d.get("description") or "")[:300], "videos": vids}
    print("OK", h, d.get("channel_follower_count"), len(vids)); time.sleep(2)

for q in cfg.get("searches", []):
    d = ytdlp(f"ytsearch{cfg.get('per_search', 40)}:{q}", cfg.get("per_search", 40))
    if "error" in d:
        out["searches"][q] = d; print("ERR", q, d["error"][:200]); continue
    out["searches"][q] = [slim(e) for e in d.get("entries", []) if e]
    print("OK search", q, len(out["searches"][q])); time.sleep(2)

json.dump(out, open(sys.argv[2], "w"), indent=1)
