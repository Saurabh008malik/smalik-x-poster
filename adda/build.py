"""Build Creator Adda's posts for one day (Hinglish, India).

Usage: python3 adda/build.py posts.json DATE(IST, YYYY-MM-DD) adda/queue
posts.json = list of 3 items in order: post, reel, post
  {"caption","first_comment","instagram_first_comment","card":{...},"reel":true?,"sources":[...]}
Writes OUT_DIR/<date>-NN.json (+ .jpg card or .mp4 reel) with publish_at (UTC) at the IST slots below.
"""
import base64
import sys
import datetime as dt
import json
import pathlib
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import reel2  # noqa: E402

HERE = pathlib.Path(__file__).parent
IST = ZoneInfo("Asia/Kolkata")
# (hour, minute) IST for item 1, 2, 3 ... the reel goes to REEL_SLOT
POST_SLOTS = [(17, 30), (21, 30), (16, 30)]  # cards: 5:30 PM, 9:30 PM IST (hourly publisher runs at :35 from 4:35 PM)
REEL_SLOTS = [(19, 30), (22, 30)]  # reels: 7:30 PM, 10:30 PM IST
FPS = 24
MUSIC = HERE.parent / "money" / "music"


def _fonts_css():
    css = []
    for fam, weight, f in [("Bricolage", 600, "bricolage-600"), ("Bricolage", 800, "bricolage-800"),
                           ("Mukta", 500, "mukta-500"), ("Mukta", 700, "mukta-700")]:
        b64 = base64.b64encode((HERE / "fonts" / f"{f}.woff2").read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(css)


def page_html(template, data):
    host = "data:image/jpeg;base64," + base64.b64encode((HERE / "brand" / "host.jpg").read_bytes()).decode()
    html = (HERE / "cards" / template).read_text()
    html = html.replace("/*FONTS*/", _fonts_css()).replace("HOST_SRC", host)
    data = dict(data)
    art = HERE / "art" / f"host-{data.get('scene')}.jpg" if data.get("scene") else None
    if art and art.exists():
        html = html.replace("ART_SRC", "data:image/jpeg;base64," + base64.b64encode(art.read_bytes()).decode())
        data["__art"] = True
    return html.replace("<script>", "<script>window.DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)


def render_card(browser, data, out):
    page = browser.new_page(viewport={"width": 1080, "height": 1350})
    page.set_content(page_html("template.html", data), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    size, minimum = page.evaluate("[window.__fit, window.__min]")
    page.screenshot(path=str(out), type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
    page.close()
    return size, minimum


def render_reel(browser, data, out):
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.set_content(page_html("template-reel.html", data), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    dur = page.evaluate("window.__duration")
    with tempfile.TemporaryDirectory() as tmp:
        for f in range(int(dur * FPS)):
            page.evaluate(f"setT({f / FPS})")
            page.screenshot(path=f"{tmp}/f{f:04d}.jpg", type="jpeg", quality=88)
        page.close()
        track = MUSIC / f"{data.get('music') or 'uplift'}.mp3"
        if not track.exists():
            track = MUSIC / "uplift.mp3"
        fade = f"afade=t=in:d=0.4,afade=t=out:st={max(0.0, dur - 1.6):.2f}:d=1.6,volume=0.9"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.jpg",
                        "-stream_loop", "-1", "-i", str(track), "-t", f"{dur:.2f}", "-af", fade,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", str(FPS),
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    return dur


def main(posts_file, date, outdir):
    posts = json.loads(pathlib.Path(posts_file).read_text())
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    day = dt.date.fromisoformat(date)
    with sync_playwright() as p:
        b = p.chromium.launch()
        n_post = n_reel = 0
        for i, post in enumerate(posts[:5]):
            name = f"{date}-{i + 1:02d}"
            item = {"caption": post["caption"], "first_comment": post.get("first_comment", ""),
                    "sources": post.get("sources", [])}
            if post.get("instagram_first_comment"):
                item["instagram"] = {"first_comment": post["instagram_first_comment"]}
            if post.get("reel2"):
                spec = dict(post["reel2"])
                spec["_art"] = (HERE / "art" / f"host-{spec.get('scene')}.jpg").exists()
                dur = reel2.render(b, spec, lambda d, sc=spec.get("scene"): page_html("template-reel2.html", {**d, "scene": sc}),
                                   out / f"{name}.mp4")
                item["video"] = f"{name}.mp4"
                hh, mm = REEL_SLOTS[n_reel % len(REEL_SLOTS)]; n_reel += 1
                print(f"{name}: voice reel ok ({dur:.1f}s)")
            elif post.get("reel"):
                dur = render_reel(b, post["card"], out / f"{name}.mp4")
                item["video"] = f"{name}.mp4"
                hh, mm = REEL_SLOTS[n_reel % len(REEL_SLOTS)]; n_reel += 1
                print(f"{name}: reel ok ({dur:.1f}s)")
            else:
                size, minimum = render_card(b, post["card"], out / f"{name}.jpg")
                item["image"] = f"{name}.jpg"
                hh, mm = POST_SLOTS[n_post % len(POST_SLOTS)]
                n_post += 1
                warn = "  <-- SMALL, shorten the headline or points" if size < minimum else ""
                print(f"{name}: card ok (headline font {size}px){warn}")
            when = dt.datetime.combine(day, dt.time(hh, mm), tzinfo=IST)
            item["publish_at"] = when.astimezone(dt.timezone.utc).isoformat()
            (out / f"{name}.json").write_text(json.dumps(item, ensure_ascii=False, indent=2))
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:4])
