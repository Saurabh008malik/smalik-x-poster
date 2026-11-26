"""Render post cards from one data JSON.

Usage:
  python3 cards/render.py data.json out_basename
Creates:
  out_basename.png      X / Twitter card
  out_basename-fb.jpg   1080x1350 (Facebook / Instagram portrait card)
Since 27 Nov 2026 both use the new poster design (design/engine.py, 4:5 portrait, which also
takes more of the X mobile timeline). If the new design fails for any reason, the old templates
(1600x900 X card, 1080x1350 portrait) are used, so a post is never lost.
Needs: pip install playwright && playwright install chromium (already present in Claude's workspace).
"""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
base = sys.argv[2]
sys.path.insert(0, str(here.parent / "design"))
try:
    import engine as design
except Exception as e:  # noqa: BLE001
    design = None
    print("new design unavailable, using old templates:", e)

jobs = [
    ("template.html", 1600, 900, base + ".png", "png"),
    ("template-portrait.html", 1080, 1350, base + "-fb.jpg", "jpeg"),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    for tpl, w, h, out, kind in jobs:
        if design is not None:
            try:
                design.render_card("ckb", data, out, browser=b)
                print("saved", out, "(new design)")
                continue
            except Exception as e:  # noqa: BLE001
                print(f"new design failed for {out} ({e}); using old template")
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
