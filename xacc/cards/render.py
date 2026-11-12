"""python3 xacc/cards/render.py ACCT data.json out.png  -> 1600x900 card for X (16:9)."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).parent
acct, data, outp = sys.argv[1], json.loads(pathlib.Path(sys.argv[2]).read_text()), sys.argv[3]
html = (here / f"{acct}.html").read_text().replace("<script>", "<script>window.DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 900})
    pg.set_content(html, wait_until="networkidle"); pg.wait_for_timeout(300)
    over = pg.evaluate("""()=>{const s=document.getElementById('sub'),st=document.getElementById('stats');if(!s||!st||!s.textContent)return false;return s.getBoundingClientRect().bottom>st.getBoundingClientRect().top-10}""")
    pg.screenshot(path=outp); b.close()
print("saved", outp, "| WARNING: text overlaps the stat boxes - shorten sub or headline" if over else "| layout ok")
