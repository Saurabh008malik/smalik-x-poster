"""python3 xacc/cards/render.py ACCT data.json out.png  -> card for X.
Since 27 Nov 2026 the card uses the new poster design (design/engine.py, 4:5 portrait, which fills more
of the X mobile timeline). If that fails, the old 1600x900 card is made, so a post is never lost."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).parent
acct, data, outp = sys.argv[1], json.loads(pathlib.Path(sys.argv[2]).read_text()), sys.argv[3]
sys.path.insert(0, str(here.parent.parent / "design"))
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        import engine
        d = dict(data)
        d.setdefault("kicker", d.get("tag") or "")
        d["theme"] = d.get("theme") or ("red" if d.get("direction") == "down" else ("green" if acct == "wsp" else "blue"))
        size = engine.render_card(acct, d, outp, browser=b)
        b.close()
        print("saved", outp, "| new design | layout ok" if size >= 70 else f"| new design | WARNING: headline shrank to {size}px - shorten headline or sub")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print("new design failed, using the old card:", e)
    html = (here / f"{acct}.html").read_text().replace("<script>", "<script>window.DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)
    pg = b.new_page(viewport={"width": 1600, "height": 900})
    pg.set_content(html, wait_until="networkidle"); pg.wait_for_timeout(300)
    over = pg.evaluate("""()=>{const s=document.getElementById('sub'),st=document.getElementById('stats');if(!s||!st||!s.textContent)return false;return s.getBoundingClientRect().bottom>st.getBoundingClientRect().top-10}""")
    pg.screenshot(path=outp); b.close()
print("saved", outp, "| WARNING: text overlaps the stat boxes - shorten sub or headline" if over else "| layout ok")
