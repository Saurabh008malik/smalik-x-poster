"""Profile pictures (1080x1080, centred for circle crops) and Facebook covers (1640x624) for the usfin pages.

Usage: python3 usfin/brand.py   -> usfin/<slug>/brand/<slug>-profile.png and -cover.png
"""
import json
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PAGES = json.loads((HERE / "pages.json").read_text())

STYLE = {
    "credit": dict(accent="#4C8DFF", rgb="76,141,255", tag="Real credit talk. Scores, debt and cards - explained.",
                   title=("Credit Score", "Truths"),
                   icon='<path d="M16 82 A44 44 0 1 1 104 82" fill="none" stroke="{a}" stroke-width="9" stroke-linecap="round"/>'
                        '<path d="M60 70 L84 40" stroke="#F5F7FB" stroke-width="9" stroke-linecap="round"/>'
                        '<circle cx="60" cy="70" r="9" fill="#F5F7FB"/>'
                        '<path d="M26 92 H94" stroke="{a}" stroke-width="7" stroke-linecap="round" opacity=".55"/>'),
    "closing": dict(accent="#FFC23D", rgb="255,194,61", tag="Buying a home? Know every dollar before you sign.",
                    title=("Closing", "Costs"),
                    icon='<path d="M14 58 L60 18 L106 58" fill="none" stroke="{a}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                         '<path d="M26 54 V100 H94 V54" fill="none" stroke="#F5F7FB" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                         '<text x="60" y="88" text-anchor="middle" font-family="Inter,sans-serif" font-weight="900" font-size="42" fill="{a}">$</text>'),
    "fineprint": dict(accent="#FF7A45", rgb="255,122,69", tag="The fine print they hope you skip - in plain English.",
                      title=("Fine Print", "Facts"),
                      icon='<circle cx="52" cy="52" r="30" fill="none" stroke="{a}" stroke-width="9"/>'
                           '<path d="M75 75 L102 102" stroke="#F5F7FB" stroke-width="11" stroke-linecap="round"/>'
                           '<path d="M38 46 H66 M38 58 H58" stroke="#F5F7FB" stroke-width="6" stroke-linecap="round"/>'),
}

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Inter","Noto Color Emoji",sans-serif;background:#070B14;color:#F5F7FB}
.profile{width:1080px;height:1080px;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(700px 700px at 70% 20%,rgba(%RGB%,.30),transparent 60%),linear-gradient(160deg,#0E1830,#070B14)}
.profile svg{width:620px;height:620px}
.cover{width:1640px;height:624px;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(900px 600px at 85% 0%,rgba(%RGB%,.28),transparent 60%),radial-gradient(700px 500px at 0% 100%,rgba(76,141,255,.14),transparent 60%),linear-gradient(160deg,#0E1830,#070B14)}
.cover::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:64px 64px}
.inner{position:relative;display:flex;align-items:center;gap:44px;top:-120px}
.inner svg{width:190px;height:190px}
.t1{font-size:108px;font-weight:900;letter-spacing:-.04em;line-height:1}
.t1 em{font-style:normal;color:%ACC%}
.t2{margin-top:16px;font-size:36px;font-weight:600;color:#B9C3DA;letter-spacing:-.01em}"""


def page_html(slug):
    st = STYLE[slug]
    svg = '<svg viewBox="0 0 120 120">' + st["icon"].replace("{a}", st["accent"]) + "</svg>"
    css = CSS.replace("%RGB%", st["rgb"]).replace("%ACC%", st["accent"])
    a, b = st["title"]
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
            f'<div class="profile" id="profile">{svg}</div>'
            f'<div class="cover" id="cover"><div class="inner">{svg}<div><div class="t1">{a} <em>{b}</em></div>'
            f'<div class="t2">{st["tag"]}</div></div></div></div></body></html>')


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        for slug in PAGES:
            out = HERE / slug / "brand"
            out.mkdir(parents=True, exist_ok=True)
            page = b.new_page(viewport={"width": 1700, "height": 1100}, device_scale_factor=1)
            page.set_content(page_html(slug), wait_until="networkidle")
            page.locator("#profile").screenshot(path=str(out / f"{slug}-profile.png"))
            page.locator("#cover").screenshot(path=str(out / f"{slug}-cover.png"))
            page.close()
            print("wrote", out)
        b.close()


if __name__ == "__main__":
    main()
