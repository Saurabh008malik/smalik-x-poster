"""Build one day of posts for a usfin page.

Usage: python3 usfin/build.py <slug> posts.json TARGET_ET_DATE OUT_DIR
Same format and 8 + 1 reel slots as money/build.py; cards are branded with the page name.
"""
import datetime as dt
import json
import pathlib
import sys
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reel as reel_mod  # noqa: E402

SLOTS_ET = [7, 9, 11, 13, 15, 17, 19, 21]
REEL_SLOT_ET = 12


def main(slug, posts_file, date, outdir):
    page_cfg = json.loads((HERE / "pages.json").read_text())[slug]
    posts = json.loads(pathlib.Path(posts_file).read_text())
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = ((HERE.parent / "money" / "cards" / "template.html").read_text()
           .replace("Paycheck Truths", page_cfg["name"]).replace("Follow for daily money truths", page_cfg["cta"]))
    et = ZoneInfo("America/New_York")
    day = dt.date.fromisoformat(date)
    with sync_playwright() as p:
        b = p.chromium.launch()
        n_std = 0
        reels = []
        for i, post in enumerate(posts[: len(SLOTS_ET) + 1]):
            name = f"{date}-{i + 1:02d}"
            item = {"caption": post["caption"], "first_comment": post.get("first_comment", ""),
                    "sources": post.get("sources", [])}
            if post.get("instagram_first_comment"):
                item["instagram"] = {"first_comment": post["instagram_first_comment"]}
            if post.get("card"):
                item["card"] = post["card"]
            if post.get("reel") and post.get("card"):
                reels.append((post["card"], out / f"{name}.mp4"))  # rendered after this browser closes
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
    for card, mp4 in reels:
        reel_mod.render(page_cfg["name"], card, mp4)


if __name__ == "__main__":
    main(*sys.argv[1:5])
