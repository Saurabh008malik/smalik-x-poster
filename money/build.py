"""Build the day's money-page posts.

Usage: python3 money/build.py posts.json TARGET_ET_DATE OUT_DIR
posts.json = list of {"caption","first_comment","card": {...} or null,"sources":[...]}
Writes OUT_DIR/<date>-NN.json (+ .jpg card) with a publish_at (UTC) in 8 US-daytime slots.
"""
import datetime as dt
import json
import pathlib
import sys
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import reel as reel_mod  # noqa: E402

HERE = pathlib.Path(__file__).parent
SLOTS_ET = [7, 9, 11, 13, 15, 17, 19, 21]
REEL_SLOT_ET = 12


def main(posts_file, date, outdir):
    posts = json.loads(pathlib.Path(posts_file).read_text())
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = (HERE / "cards" / "template.html").read_text()
    et = ZoneInfo("America/New_York")
    day = dt.date.fromisoformat(date)
    with sync_playwright() as p:
        b = p.chromium.launch()
        n_std = 0
        for i, post in enumerate(posts[: len(SLOTS_ET) + 1]):
            name = f"{date}-{i + 1:02d}"
            item = {"caption": post["caption"], "first_comment": post.get("first_comment", ""),
                    "sources": post.get("sources", [])}
            if post.get("instagram_first_comment"):
                item["instagram"] = {"first_comment": post["instagram_first_comment"]}
            if post.get("reel") and post.get("card"):
                reel_mod.render(post["card"], out / f"{name}.mp4")
                item["video"] = f"{name}.mp4"
                slot = REEL_SLOT_ET
            elif post.get("card"):
                html = tpl.replace("<script>", "<script>window.DATA = " + json.dumps(post["card"]) + ";", 1)
                page = b.new_page(viewport={"width": 1080, "height": 1350})
                page.set_content(html, wait_until="networkidle")
                size = page.evaluate("window.__fit")
                page.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=92,
                                clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
                page.close()
                item["image"] = f"{name}.jpg"
                print(f"{name}: card ok (headline font {size}px){'  <-- SMALL, shorten the headline' if size < 80 else ''}")
            else:
                print(f"{name}: text-only post")
            if not post.get("reel"):
                slot = SLOTS_ET[n_std % len(SLOTS_ET)]
                n_std += 1
            when = dt.datetime.combine(day, dt.time(slot, 0), tzinfo=et)
            item["publish_at"] = when.astimezone(dt.timezone.utc).isoformat()
            (out / f"{name}.json").write_text(json.dumps(item, ensure_ascii=False, indent=2))
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:4])
