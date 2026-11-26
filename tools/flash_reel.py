"""Turn a cricket flash post's Facebook/Instagram image into an animated reel (27 Nov 2026).

Usage: python3 tools/flash_reel.py queue/DATE-flash-KEY.json /tmp/card.json
Reels reach people who don't follow the page yet; image posts mostly don't. X keeps its card image.
Never fails the run: on any problem the post stays an image post.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "design"))


def main(qpath, cardpath):
    q = pathlib.Path(qpath)
    d = json.loads(q.read_text(encoding="utf-8"))
    fb = d.get("facebook") or {}
    if not fb.get("caption") or "facebook" not in d.get("platforms", []):
        print("flash reel: no Facebook part, nothing to do"); return
    card = json.loads(pathlib.Path(cardpath).read_text(encoding="utf-8"))
    stats = card.get("stats") or []
    big = ""
    for s in stats:
        b = str(s.get("big") or "")
        if re.search(r"\d", b) and len(b) <= 7:
            big = b; break
    theme = {"#5B9BFF": "blue", "#FF5A5F": "red", "#3DDC84": "green", "#FFC64D": "gold"}.get(str(card.get("accent", "")).upper(), "saffron")
    reel = {"brand": "ckb", "kicker": card.get("tag") or "Cricket", "headline": card.get("headline") or "",
            "sub": card.get("result") or "", "source": card.get("source") or "", "big": big, "theme": theme}
    if not reel["headline"]:
        print("flash reel: no headline, keeping the image post"); return
    import engine
    out = q.with_name(q.stem + "-reel.mp4")
    music = ROOT / "money" / "music" / "uplift.mp3"
    engine.render_reel("ckb", reel, out, music if music.exists() else None)
    if not out.exists() or out.stat().st_size < 50_000:
        print("flash reel: output missing, keeping the image post"); return
    old = fb.pop("image", None)
    fb["video"] = out.name
    if old and (q.parent / old).exists():
        (q.parent / old).unlink()
    d["facebook"] = fb
    q.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("flash reel ok:", out.name)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:  # noqa: BLE001
        print("flash reel failed, keeping the image post:", e)
