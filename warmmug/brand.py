"""Warm Mug Radio - channel art: banner (2560x1440) and avatar (800x800).

Usage: python warmmug/brand.py out_dir
Outputs: banner.png, avatar.png
"""
import asyncio
import sys
from pathlib import Path

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700'
         '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')

# YouTube banner: 2560x1440 canvas, but only the middle 1546x423 is shown on every device.
BANNER = """<!doctype html><html><head><meta charset="utf-8">""" + FONTS + """
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:2560px;height:1440px;overflow:hidden;
       background:radial-gradient(130% 100% at 50% 42%, #3a2a1d 0%, #231812 45%, #140d0a 100%);
       font-family:'Inter',sans-serif;position:relative}
  /* warm lamp glow behind the text */
  .glow{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
        width:1900px;height:900px;border-radius:50%;
        background:radial-gradient(50% 50% at 50% 50%, rgba(255,176,79,.30), rgba(255,176,79,0) 70%);
        filter:blur(10px)}
  .safe{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
        width:1546px;height:423px;display:flex;align-items:center;
        justify-content:center;gap:60px}
  .mug{flex:0 0 auto}
  .txt{display:flex;flex-direction:column;gap:14px}
  h1{font-family:'Fraunces',serif;font-weight:700;font-size:112px;line-height:.95;
     color:#fff6e8;letter-spacing:-2px;text-shadow:0 4px 40px rgba(0,0,0,.5)}
  h1 em{font-style:normal;color:#ffb04f}
  p{font-size:33px;font-weight:500;color:#e8d5bd;letter-spacing:.3px}
  .row{display:flex;gap:14px;margin-top:10px}
  .chip{font-size:24px;font-weight:600;color:#1c120c;background:#ffb04f;
        padding:11px 22px;border-radius:999px;letter-spacing:.2px}
  .chip.ghost{background:transparent;color:#f0dcc2;border:2px solid rgba(240,220,194,.45)}
</style></head><body>
  <div class="glow"></div>
  <div class="safe">
    <svg class="mug" width="300" height="300" viewBox="0 0 300 300">
      <defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff3e0"/><stop offset="1" stop-color="#e8c79b"/></linearGradient></defs>
      <!-- saucer -->
      <ellipse cx="150" cy="247" rx="112" ry="20" fill="#120b07" opacity=".55"/>
      <!-- body -->
      <path d="M62 120 h150 v62 a75 75 0 0 1 -150 0 z" fill="url(#c)"/>
      <!-- handle -->
      <path d="M212 136 a44 44 0 0 1 0 74" fill="none" stroke="#f0dcc0" stroke-width="17" stroke-linecap="round"/>
      <!-- coffee surface -->
      <ellipse cx="137" cy="120" rx="75" ry="15" fill="#4a2a17"/>
      <ellipse cx="137" cy="118" rx="62" ry="11" fill="#6b3b1f"/>
      <!-- steam -->
      <g fill="none" stroke="#ffd9a8" stroke-width="7" stroke-linecap="round" stroke-opacity=".8">
        <path d="M112 86 C96 62 126 50 110 24"/>
        <path d="M150 80 C132 54 164 42 148 14"/>
        <path d="M188 88 C172 64 200 52 186 28"/>
      </g>
    </svg>
    <div class="txt">
      <h1>Warm Mug <em>Radio</em></h1>
      <p>Cozy jazz hop &amp; lofi to study, work and slow down.</p>
      <div class="row">
        <span class="chip">New mix weekly</span>
        <span class="chip ghost">Shorts 4&times; a week</span>
        <span class="chip ghost">Instrumental &middot; no ads mid-mix</span>
      </div>
    </div>
  </div>
</body></html>"""

AVATAR = """<!doctype html><html><head><meta charset="utf-8">""" + FONTS + """
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:800px;height:800px;overflow:hidden;
       background:radial-gradient(120% 100% at 50% 35%, #45321f 0%, #281a12 55%, #170f0a 100%);
       display:flex;align-items:center;justify-content:center;position:relative}
  .ring{position:absolute;width:720px;height:720px;border-radius:50%;
        border:10px solid rgba(255,176,79,.35)}
  .glow{position:absolute;width:620px;height:620px;border-radius:50%;
        background:radial-gradient(50% 50% at 50% 45%, rgba(255,176,79,.35), rgba(255,176,79,0) 70%)}
</style></head><body>
  <div class="glow"></div><div class="ring"></div>
  <svg width="470" height="470" viewBox="0 0 300 300">
    <defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff3e0"/><stop offset="1" stop-color="#e8c79b"/></linearGradient></defs>
    <path d="M62 132 h150 v58 a75 75 0 0 1 -150 0 z" fill="url(#c)"/>
    <path d="M212 148 a44 44 0 0 1 0 74" fill="none" stroke="#f0dcc0" stroke-width="17" stroke-linecap="round"/>
    <ellipse cx="137" cy="132" rx="75" ry="15" fill="#4a2a17"/>
    <ellipse cx="137" cy="130" rx="62" ry="11" fill="#6b3b1f"/>
    <g fill="none" stroke="#ffd9a8" stroke-width="8" stroke-linecap="round" stroke-opacity=".85">
      <path d="M112 96 C96 70 126 58 110 30"/>
      <path d="M150 90 C132 62 164 50 148 18"/>
      <path d="M188 98 C172 72 200 60 186 34"/>
    </g>
  </svg>
</body></html>"""


async def shoot(html, path, w, h):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        await pg.set_content(html)
        await pg.wait_for_timeout(1800)  # let Google Fonts load
        await pg.screenshot(path=str(path))
        await b.close()


async def main(out):
    out.mkdir(parents=True, exist_ok=True)
    await shoot(BANNER, out / "banner.png", 2560, 1440)
    await shoot(AVATAR, out / "avatar.png", 800, 800)
    print("wrote", out / "banner.png", "and", out / "avatar.png")


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1] if len(sys.argv) > 1 else "warmmug/brand")))
