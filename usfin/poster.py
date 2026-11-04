"""Publishes due posts for the usfin pages (Credit Score Truths, Closing Costs, Fine Print Facts).

Run: python usfin/poster.py                 -> post due items for every page that has its secrets set
     python usfin/poster.py check [slug]    -> test Page token(s), write status/<slug>_token.txt
     python usfin/poster.py delete slug id  -> delete a Facebook post/reel
Secrets (env) per page: <PREFIX>_FB_PAGE_ID, <PREFIX>_FB_PAGE_TOKEN  (CREDIT, CLOSING, FINEPRINT)
Reuses money/poster.py (Facebook + Instagram + first comments); only the folders and secrets differ.
"""
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "money"))
import poster as mp  # noqa: E402  (money/poster.py)

PAGES = json.loads((HERE / "pages.json").read_text())


def use(slug):
    cfg = PAGES[slug]
    pid, tok = os.environ.get(f"{cfg['env']}_FB_PAGE_ID", ""), os.environ.get(f"{cfg['env']}_FB_PAGE_TOKEN", "")
    if not pid or not tok:
        print(f"[{cfg['name']}] secrets not set yet - skipped.")
        return False
    os.environ["MONEY_FB_PAGE_ID"], os.environ["MONEY_FB_PAGE_TOKEN"] = pid, tok
    base = HERE / slug
    mp.ROOT, mp.QUEUE, mp.POSTED, mp.FAILED = base, base / "queue", base / "posted", base / "failed"
    return True


def check(slug):
    import requests
    cfg = PAGES[slug]
    page_id, token = mp.page_token()
    r = requests.get(f"{mp.GRAPH}/{page_id}", params={"fields": "id,name,instagram_business_account{id,username}",
                                                      "access_token": token}, timeout=30)
    print(f"[{cfg['name']}] Page:", r.status_code, r.text[:200])
    raw = os.environ["MONEY_FB_PAGE_TOKEN"]
    d = requests.get(f"{mp.GRAPH}/debug_token", params={"input_token": raw, "access_token": raw}, timeout=30).json().get("data", {})
    status = HERE.parent / "status"
    status.mkdir(exist_ok=True)
    (status / f"{slug}_token.txt").write_text(
        f"page call: {r.status_code} {r.text[:300]}\ntype: {d.get('type')}\nexpires_at: {d.get('expires_at')}\n"
        f"data_access_expires_at: {d.get('data_access_expires_at')}\nscopes: {d.get('scopes')}\n")
    return r.ok


def main():
    args = sys.argv[1:]
    ok = True
    if args and args[0] == "check":
        for slug in (args[1:2] or PAGES):
            if use(slug):
                ok &= check(slug)
    elif args and args[0] == "delete":
        if use(args[1]):
            sys.argv = ["poster.py", "delete", args[2]]
            mp.main()
    else:
        for slug in PAGES:
            if not use(slug):
                continue
            sys.argv = ["poster.py"]
            try:
                mp.main()
            except SystemExit as e:  # one page failing must not stop the others
                ok &= (e.code in (0, None))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
