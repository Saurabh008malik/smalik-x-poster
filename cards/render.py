"""Render post cards from one data JSON.

Usage:
  python3 cards/render.py data.json out_basename
Creates:
  out_basename.png      1600x900  (X / Twitter card)
  out_basename-fb.jpg   1080x1350 (Facebook / Instagram portrait card)
Needs: pip install playwright && playwright install chromium (already present in Claude's workspace).
"""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
base = sys.argv[2]

jobs = [
    ("template.html", 1600, 900, base + ".png", "png"),
    ("template-portrait.html", 1080, 1350, base + "-fb.jpg", "jpeg"),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    for tpl, w, h, out, kind in jobs:
        html = (here / tpl).read_text().replace("<script>", "<script>window.DATA = " + json.dumps(data) + ";", 1)
        page = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        page.set_content(html, wait_until="networkidle")
        opts = {"path": out, "clip": {"x": 0, "y": 0, "width": w, "height": h}, "type": kind}
        if kind == "jpeg":
            opts["quality"] = 92
        page.screenshot(**opts)
        page.close()
        print("saved", out)
    b.close()
