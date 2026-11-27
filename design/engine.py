"""Shared poster + animated-reel engine (Nov 2026 redesign).

Posters: design/poster.html (1080x1350), one distinct skin per page.
Reels:   design/reel.html (1080x1920), HyperFrames method: one paused GSAP timeline,
         seeked frame by frame, so every render is identical.

Used by money/, usfin/, adda/ and cards/ with a fallback to the old templates, so a
problem here can never stop a post.

  render_card(brand, data, out_jpg)          -> headline font size (int)
  render_reel(brand, data, out_mp4, music)   -> duration seconds
brand: paycheck | credit | closing | fineprint | adda | ckb | x (X cards: Saurabh Malik @Smalik_wc)
"""
import base64
import json
import pathlib
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FPS = 24
FONTS = {
    "Brico": "BricolageGrotesque-Bold.ttf", "BricoR": "BricolageGrotesque-Regular.ttf",
    "Mono": "DMMono-Regular.ttf", "Outfit": "Outfit-Bold.ttf", "OutfitR": "Outfit-Regular.ttf",
    "Serif": "InstrumentSerif-Regular.ttf", "SerifI": "InstrumentSerif-Italic.ttf",
    "Anton": "Anton-Regular.ttf", "Shoulders": "BigShoulders-Bold.ttf",
}
BRANDS = {
    "paycheck": {"name": "Paycheck Truths", "handle": "@paychecktruths", "cta": "Follow for daily money truths"},
    "credit": {"name": "Credit Score Truths", "handle": "@creditscoretruths", "cta": "Follow for daily credit truths"},
    "closing": {"name": "Closing Costs", "handle": "@closingcosts", "cta": "Follow for daily home-buying truths"},
    "fineprint": {"name": "Fine Print Facts", "handle": "@fineprintfacts", "cta": "Follow so you never miss the fine print"},
    "adda": {"name": "Creator Adda", "handle": "@real_creator_adda", "cta": "Follow karo, roz ek creator tip"},
    "ckb": {"name": "Cricket Ki Baat", "handle": "@realcricketkibaat", "cta": "Follow karo, roz ki cricket"},
    # X cards: Saurabh's own account (same stadium look as ckb, but his own name + handle, never Cricket Ki Baat)
    "x": {"name": "Saurabh Malik", "handle": "@Smalik_wc", "cta": "Follow for daily cricket updates"},
    "wsp": {"name": "Wall St Pulse", "handle": "@WallStPulseHQ", "cta": "Follow for the market in 30 seconds"},
    "inf": {"name": "The Inference", "handle": "@TheInferenceHQ", "cta": "Follow for AI news without the hype"},
}
_cache = {}


def _font_css():
    if "css" not in _cache:
        parts = []
        for fam, f in FONTS.items():
            b = base64.b64encode((HERE / "fonts" / f).read_bytes()).decode()
            parts.append(f'@font-face{{font-family:"{fam}";src:url(data:font/ttf;base64,{b}) format("truetype")}}')
        _cache["css"] = "\n".join(parts)
    return _cache["css"]


def _page(tpl, brand, data):
    cfg = dict(BRANDS.get(brand, BRANDS["credit"]))
    cfg["key"] = brand
    html = (HERE / tpl).read_text()
    html = html.replace("/*FONTS*/", _font_css())
    html = html.replace("/*GSAP*/", (HERE / "vendor" / "gsap.min.js").read_text())
    html = html.replace("/*DATA*/", "window.DATA=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
                        + ";window.BRAND=" + json.dumps(cfg, ensure_ascii=False) + ";" + _host(brand))
    return html


def _host(brand):
    p = ROOT / "adda" / "brand" / "host.jpg"
    if brand != "adda" or not p.exists():
        return ""
    return "window.HOST='data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() + "';"


def render_card(brand, data, out, browser=None):
    def go(b):
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(_page("poster.html", brand, data), wait_until="load")
        page.evaluate("document.fonts.ready")
        page.wait_for_function("window.__ready === true", timeout=15000)
        size = page.evaluate("window.__fit")
        kind = "png" if str(out).endswith(".png") else "jpeg"
        opts = {"path": str(out), "type": kind, "clip": {"x": 0, "y": 0, "width": 1080, "height": 1350}}
        if kind == "jpeg":
            opts["quality"] = 93
        page.screenshot(**opts)
        page.close()
        return size
    if browser is not None:
        return go(browser)
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            return go(b)
        finally:
            b.close()


def render_reel(brand, data, out, music=None, browser=None):
    with tempfile.TemporaryDirectory() as tmp:
        if browser is not None:
            dur = _frames(browser, brand, data, tmp)
        else:
            with sync_playwright() as p:
                b = p.chromium.launch()
                try:
                    dur = _frames(b, brand, data, tmp)
                finally:
                    b.close()
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.jpg"]
        if music and pathlib.Path(music).exists():
            fade = f"afade=t=in:d=0.3,afade=t=out:st={max(0.0, dur - 1.4):.2f}:d=1.4,volume=0.9"
            cmd += ["-stream_loop", "-1", "-i", str(music), "-t", f"{dur:.2f}", "-af", fade, "-c:a", "aac", "-b:a", "128k"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", str(FPS), "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)
    print(f"reel ok (new design): {out} ({dur:.1f}s)")
    return dur


def _frames(b, brand, data, tmp):
    page = b.new_page(viewport={"width": 1080, "height": 1920})
    page.set_content(_page("reel.html", brand, data), wait_until="load")
    page.evaluate("document.fonts.ready")
    page.wait_for_function("window.__ready === true", timeout=15000)
    dur = float(page.evaluate("window.__duration"))
    for f in range(int(dur * FPS)):
        page.evaluate(f"window.setT({f / FPS})")
        page.screenshot(path=f"{tmp}/f{f:04d}.jpg", type="jpeg", quality=88)
    page.close()
    return dur


def short_overlay(channel, hook, in_mp4, out_mp4):
    """27 Nov 2026: give an already-rendered long-video Short the new animated top (channel chip, hook words
    popping in, 'link in the description' pill). The new panel covers the old title area; the rest of the
    Short is unchanged. Raises on any problem so the caller can upload the original file instead."""
    html = (HERE / "short_top.html").read_text()
    html = html.replace("/*FONTS*/", _font_css()).replace("/*GSAP*/", (HERE / "vendor" / "gsap.min.js").read_text())
    html = html.replace("/*DATA*/", "window.DATA=" + json.dumps({"channel": channel, "hook": hook}, ensure_ascii=False).replace("</", "<\\/") + ";")
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch()
        try:
            page = b.new_page(viewport={"width": 1080, "height": 1920})
            page.set_content(html, wait_until="load")
            page.wait_for_function("window.__ready === true", timeout=15000)
            dur = float(page.evaluate("window.__duration"))
            n = int(dur * FPS) + 1
            for f in range(n):
                page.evaluate(f"window.setT({f / FPS})")
                page.screenshot(path=f"{tmp}/o{f:04d}.png", omit_background=True)
        finally:
            b.close()
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(in_mp4), "-framerate", str(FPS), "-i", f"{tmp}/o%04d.png",
               "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=repeat:format=auto[v]", "-map", "[v]", "-map", "0:a?",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy",
               "-movflags", "+faststart", str(out_mp4)]
        subprocess.run(cmd, check=True)
    return out_mp4
