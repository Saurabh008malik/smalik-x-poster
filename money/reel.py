"""Render an animated 1080x1920 Reel (mp4, silent AAC track) from a card JSON.

Usage: python3 money/reel.py card.json out.mp4
"""
import json
import pathlib
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
FPS = 24
MUSIC = HERE / "music"
BY_THEME = {"green": "calm", "gold": "uplift", "red": "focus", "blue": "focus"}


def render(card, out):
    tpl = (HERE / "cards" / "template-reel.html").read_text()
    html = tpl.replace("<script>", "<script>window.DATA = " + json.dumps(card) + ";", 1)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(html, wait_until="networkidle")
        dur = page.evaluate("window.__duration")
        n = int(dur * FPS)
        for f in range(n):
            page.evaluate(f"setT({f / FPS})")
            page.screenshot(path=f"{tmp}/f{f:04d}.jpg", type="jpeg", quality=88)
        b.close()
        track = MUSIC / f"{card.get('music') or BY_THEME.get(card.get('theme'), 'calm')}.mp3"
        if not track.exists():
            track = MUSIC / "calm.mp3"
        fade = f"afade=t=in:d=0.4,afade=t=out:st={max(0.0, dur - 1.6):.2f}:d=1.6,volume=0.9"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.jpg",
                        "-i", str(track), "-t", f"{dur:.2f}", "-af", fade,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", str(FPS),
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    print(f"reel ok: {out} ({dur:.1f}s)")


if __name__ == "__main__":
    render(json.loads(pathlib.Path(sys.argv[1]).read_text()), sys.argv[2])
