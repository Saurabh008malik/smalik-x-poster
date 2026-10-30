"""Warm Mug Radio - draws the video background (1920x1080) and thumbnail (1280x720).

The scene is a cozy window at night/morning with a steaming mug on the sill.
The mood (rain, autumn, winter, night, morning...) is picked from the video title.

Usage: python warmmug/art.py "<video title>" out_dir
"""
import random
import sys
from pathlib import Path

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700'
         '&family=Inter:wght@500;600;700&display=swap" rel="stylesheet">')

# sky top, sky bottom, wall, glow colour, accent
THEMES = {
    "rain":    dict(sky=("#1b2433", "#3a4a5e"), wall="#24170f", glow="#ffb35c", accent="#9fc3e6", fx="rain"),
    "autumn":  dict(sky=("#2b1b2e", "#c46a3a"), wall="#2a170d", glow="#ffb04f", accent="#e8894a", fx="leaves"),
    "winter":  dict(sky=("#141d33", "#3d4d73"), wall="#20160f", glow="#ffc074", accent="#dfe9ff", fx="snow"),
    "night":   dict(sky=("#0d1226", "#2c2f5c"), wall="#1b120c", glow="#ffb86b", accent="#f5e6b8", fx="stars"),
    "morning": dict(sky=("#f2b88b", "#fbe3c4"), wall="#3a2416", glow="#ffd08a", accent="#ffffff", fx="sun"),
    "ocean":   dict(sky=("#0f2236", "#2f6f86"), wall="#1c140e", glow="#ffbe78", accent="#bfe7ef", fx="waves"),
}

KEYWORDS = [
    ("rain", "rain"), ("café", "rain"), ("cafe", "rain"),
    ("autumn", "autumn"), ("leaves", "autumn"), ("leaf", "autumn"), ("🍂", "autumn"), ("🍁", "autumn"),
    ("snow", "winter"), ("winter", "winter"), ("❄", "winter"), ("fire", "winter"),
    ("ocean", "ocean"), ("wave", "ocean"), ("🌊", "ocean"),
    ("coffee", "morning"), ("morning", "morning"), ("sunday", "morning"), ("☕", "morning"),
    ("sleep", "night"), ("midnight", "night"), ("night", "night"), ("study", "night"), ("page", "night"),
]


def pick_theme(title):
    t = title.lower()
    for word, theme in KEYWORDS:
        if word in t:
            return theme
    return "night"


def fx_layer(fx, rnd, accent):
    out = []
    if fx == "rain":
        for _ in range(140):
            x, y, l = rnd.uniform(0, 900), rnd.uniform(-40, 700), rnd.uniform(18, 46)
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x-6:.0f}" y2="{y+l:.0f}" stroke="{accent}" '
                       f'stroke-opacity="{rnd.uniform(.15,.45):.2f}" stroke-width="2" stroke-linecap="round"/>')
        for _ in range(26):  # drops on the glass
            out.append(f'<circle cx="{rnd.uniform(0,900):.0f}" cy="{rnd.uniform(0,700):.0f}" r="{rnd.uniform(2,6):.1f}" '
                       f'fill="{accent}" fill-opacity=".22"/>')
    elif fx == "snow":
        for _ in range(160):
            out.append(f'<circle cx="{rnd.uniform(0,900):.0f}" cy="{rnd.uniform(0,700):.0f}" r="{rnd.uniform(1.5,5):.1f}" '
                       f'fill="{accent}" fill-opacity="{rnd.uniform(.4,.9):.2f}"/>')
    elif fx == "leaves":
        cols = ["#e8894a", "#d4572e", "#f2b544", "#b8452a"]
        for _ in range(34):
            x, y, r = rnd.uniform(0, 900), rnd.uniform(0, 700), rnd.uniform(0, 360)
            out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="11" ry="5" fill="{rnd.choice(cols)}" '
                       f'transform="rotate({r:.0f} {x:.0f} {y:.0f})" opacity=".85"/>')
    elif fx in ("stars", "ocean"):
        for _ in range(90 if fx == "stars" else 40):
            out.append(f'<circle cx="{rnd.uniform(0,900):.0f}" cy="{rnd.uniform(0,420):.0f}" r="{rnd.uniform(.8,2.4):.1f}" '
                       f'fill="{accent}" fill-opacity="{rnd.uniform(.3,.9):.2f}"/>')
        out.append(f'<circle cx="690" cy="150" r="56" fill="{accent}" fill-opacity=".9"/>'
                   f'<circle cx="712" cy="138" r="52" fill="url(#sky)"/>')  # crescent moon
        if fx == "ocean":
            for i in range(7):
                y = 470 + i * 34
                out.append(f'<path d="M0 {y} Q 75 {y-14} 150 {y} T 300 {y} T 450 {y} T 600 {y} T 750 {y} T 900 {y}" '
                           f'fill="none" stroke="{accent}" stroke-opacity="{.15 + i*.06:.2f}" stroke-width="3"/>')
    elif fx == "sun":
        out.append('<circle cx="450" cy="560" r="150" fill="#ffd9a0" fill-opacity=".85"/>')
        for i in range(3):
            out.append(f'<path d="M0 {600+i*40} Q 225 {560+i*40} 450 {600+i*40} T 900 {600+i*40} V 700 H 0 Z" '
                       f'fill="#c98b6b" fill-opacity="{.35+i*.2:.2f}"/>')
    # distant city/hill silhouette for depth (not for morning/ocean which have their own)
    if fx in ("rain", "night", "snow", "leaves"):
        rnd2 = random.Random(7)
        x, pts = 0, []
        while x < 900:
            w, h = rnd2.uniform(40, 90), rnd2.uniform(80, 230)
            pts.append(f'<rect x="{x:.0f}" y="{700-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#000" fill-opacity=".35"/>')
            for _ in range(int(h // 40)):
                if rnd2.random() < .45:
                    pts.append(f'<rect x="{x+rnd2.uniform(6,w-14):.0f}" y="{700-h+rnd2.uniform(10,h-20):.0f}" width="7" height="9" '
                               f'fill="#ffcf7a" fill-opacity=".55"/>')
            x += w + 4
        out = pts + out
    return "\n".join(out)


def scene_svg(theme_name, seed=1):
    th = THEMES[theme_name]
    rnd = random.Random(seed)
    s1, s2 = th["sky"]
    glow, wall = th["glow"], th["wall"]
    fx = fx_layer(th["fx"], rnd, th["accent"])
    return f'''
<svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
 <defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{s1}"/><stop offset="1" stop-color="{s2}"/></linearGradient>
  <radialGradient id="lamp" cx=".22" cy=".42" r=".55"><stop offset="0" stop-color="{glow}" stop-opacity=".55"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a4a2a"/><stop offset="1" stop-color="#4a2a17"/></linearGradient>
  <linearGradient id="mug" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9d8c2"/><stop offset=".6" stop-color="#d9bfa0"/><stop offset="1" stop-color="#b8977a"/></linearGradient>
  <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
  <clipPath id="win"><rect x="0" y="0" width="900" height="700" rx="10"/></clipPath>
 </defs>
 <rect width="1920" height="1080" fill="{wall}"/>
 <rect width="1920" height="1080" fill="url(#lamp)"/>
 <!-- window -->
 <g transform="translate(860,120)">
  <rect x="-26" y="-26" width="952" height="752" rx="18" fill="#3b2415"/>
  <g clip-path="url(#win)"><rect width="900" height="700" fill="url(#sky)"/>{fx}</g>
  <rect x="440" y="0" width="20" height="700" fill="#3b2415"/><rect x="0" y="340" width="900" height="20" fill="#3b2415"/>
  <rect x="0" y="0" width="900" height="700" rx="10" fill="none" stroke="#2a180d" stroke-width="6"/>
 </g>
 <!-- curtain -->
 <path d="M760 70 C 800 300, 740 600, 800 900 L 690 900 C 650 600, 700 300, 660 70 Z" fill="#8c3b2a" opacity=".9"/>
 <path d="M720 70 C 750 300, 705 600, 745 900" stroke="#6e2c1f" stroke-width="10" fill="none" opacity=".7"/>
 <!-- sill -->
 <rect x="600" y="840" width="1320" height="44" rx="6" fill="url(#wood)"/>
 <rect x="600" y="884" width="1320" height="196" fill="#1a100a" opacity=".55"/>
 <!-- lamp -->
 <g transform="translate(400,330)">
  <circle cx="60" cy="40" r="210" fill="{glow}" opacity=".18" filter="url(#soft)"/>
  <path d="M-20 0 L140 0 L105 -110 L15 -110 Z" fill="#e9b26d"/>
  <rect x="54" y="0" width="12" height="505" fill="#3a2516"/><ellipse cx="60" cy="510" rx="60" ry="12" fill="#3a2516"/>
 </g>
 <!-- books -->
 <g transform="translate(1530,742)">
  <rect width="250" height="34" rx="4" fill="#5b7a6a"/><rect x="14" y="34" width="230" height="32" rx="4" fill="#c9a36a"/>
  <rect x="-6" y="66" width="262" height="32" rx="4" fill="#8c3b2a"/>
 </g>
 <!-- plant -->
 <g transform="translate(1810,700)">
  <path d="M0 140 L70 140 L60 60 L10 60 Z" fill="#b5653f"/>
  <path d="M35 60 C 0 10, -30 0, -40 -40 M35 60 C 40 0, 30 -40, 50 -80 M35 60 C 70 20, 100 0, 110 -30" stroke="#6f9b6a" stroke-width="10" fill="none" stroke-linecap="round"/>
 </g>
 <!-- mug -->
 <g transform="translate(1060,650)">
  <path d="M60 -30 C 30 -80, 90 -110, 60 -170" stroke="#fff" stroke-opacity=".35" stroke-width="10" fill="none" stroke-linecap="round" filter="url(#soft)"/>
  <path d="M120 -30 C 90 -90, 150 -120, 115 -190" stroke="#fff" stroke-opacity=".28" stroke-width="10" fill="none" stroke-linecap="round" filter="url(#soft)"/>
  <rect x="0" y="0" width="190" height="190" rx="26" fill="url(#mug)"/>
  <path d="M190 45 C 270 45, 270 150, 190 150" stroke="#d2b496" stroke-width="22" fill="none"/>
  <ellipse cx="95" cy="8" rx="88" ry="14" fill="#5a3320"/>
  <path d="M60 95 C 60 75, 95 75, 95 95 C 95 75, 130 75, 130 95 C 130 120, 95 135, 95 145 C 95 135, 60 120, 60 95 Z" fill="#c4553f" opacity=".85"/>
 </g>
 <!-- record player -->
 <g transform="translate(110,860)">
  <rect width="420" height="120" rx="14" fill="#5a3a24"/><rect x="10" y="-8" width="400" height="18" rx="6" fill="#3a2516"/>
  <ellipse cx="150" cy="-14" rx="125" ry="18" fill="#141414"/><ellipse cx="150" cy="-14" rx="32" ry="6" fill="{glow}"/>
 </g>
 <rect width="1920" height="1080" fill="url(#lamp)" opacity=".35"/>
</svg>'''


def html_page(inner, w, h):
    return f'''<!doctype html><html><head><meta charset="utf-8">{FONTS}
<style>html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#000}}
.wrap{{position:relative;width:{w}px;height:{h}px}}
.brand{{position:absolute;font-family:Inter,sans-serif;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#f6e7d2}}
.title{{position:absolute;font-family:Fraunces,Georgia,serif;font-weight:700;color:#fff6ea;line-height:1.02;
  text-shadow:0 6px 30px rgba(0,0,0,.55)}}
.chip{{position:absolute;font-family:Inter,sans-serif;font-weight:700;color:#2a170d;background:#f3c27a;border-radius:999px}}
</style></head><body><div class="wrap">{inner}</div></body></html>'''


def short_title(title):
    """First part of the title (before the |) for the thumbnail, cleaned of emoji."""
    main = title.split("|")[0].strip()
    return "".join(ch for ch in main if ord(ch) < 0x2190).strip()


def render(title, out_dir, seed=None):
    from playwright.sync_api import sync_playwright
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    theme = pick_theme(title)
    seed = seed if seed is not None else abs(hash(title)) % 10000
    svg = scene_svg(theme, seed)
    tag = title.split("|")[1].strip() if "|" in title else "Cozy Jazz Hop Lofi"
    tag = "".join(ch for ch in tag if ord(ch) < 0x2190).strip()

    bg = html_page(f'{svg}<div class="brand" style="left:70px;top:58px;font-size:26px">☕ Warm Mug Radio</div>', 1920, 1080)
    thumb = html_page(
        f'<div style="position:absolute;left:0;top:0;transform:scale(.6667);transform-origin:0 0">{svg}</div>'
        f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(15,8,4,.82) 0%,rgba(15,8,4,.45) 48%,rgba(0,0,0,0) 70%)"></div>'
        f'<div class="brand" style="left:56px;top:48px;font-size:22px">☕ Warm Mug Radio</div>'
        f'<div class="title" style="left:56px;top:150px;width:640px;font-size:68px">{short_title(title)}</div>'
        f'<div class="chip" style="left:56px;bottom:56px;padding:12px 26px;font-size:26px">{tag}</div>', 1280, 720)

    with sync_playwright() as p:
        b = p.chromium.launch()
        for html, w, h, name in ((bg, 1920, 1080, "background.png"), (thumb, 1280, 720, "thumbnail.png")):
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.set_content(html, wait_until="networkidle", timeout=30000)
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(out / name))
            pg.close()
        b.close()
    # YouTube thumbnails must be under 2 MB - save a JPG copy
    from PIL import Image
    Image.open(out / "thumbnail.png").convert("RGB").save(out / "thumbnail.jpg", quality=90)
    return theme


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2]))
