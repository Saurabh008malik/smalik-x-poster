"""Download public-domain assets (text files + Wikimedia Commons images) inside GitHub Actions.
config: {"urls": {"name.ext": "https://..."}, "commons": [{"q": "search", "n": 40, "tag": "genesis"}], "min_width": 900, "thumb": 1600}
Writes research/assets/<name>/ (files, img/*.jpg, sources.json).
"""
import json, sys, pathlib, re, time, requests

cfg = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "LamplightResearch/1.0 (contact: saurabh6041@gmail.com)"}
for name, url in cfg.get("urls", {}).items():
    try:
        r = requests.get(url, headers=H, timeout=120); r.raise_for_status()
        (out / name).write_bytes(r.content); print("OK url", name, len(r.content))
    except Exception as e:
        print("ERR url", name, e)

OK_LIC = re.compile(r"public domain|cc0|pd-|no restrictions|pd ", re.I)
img = out / "img"; img.mkdir(exist_ok=True); sources = []
seen = set()
def get(url, **kw):
    for i in range(6):
        r = requests.get(url, headers=H, timeout=120, **kw)
        if r.status_code == 429:
            time.sleep(8 * (i + 1)); continue
        r.raise_for_status(); return r
    raise RuntimeError("429 after retries")

for job in cfg.get("commons", []):
    q, n, tag = job.get("q"), job.get("n", 40), job.get("tag", "x")
    cat = job.get("category")
    try:
        api = "https://commons.wikimedia.org/w/api.php"
        pages = {}
        cont = {}
        while len(pages) < n * 3:
            if cat:
                params = {"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": "Category:" + cat, "gcmtype": "file", "gcmlimit": 50,
                          "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": cfg.get("thumb", 1400), **cont}
            else:
                params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 50,
                          "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": cfg.get("thumb", 1400), **cont}
            j = get(api, params=params).json()
            pages.update(j.get("query", {}).get("pages", {}))
            if "continue" in j: cont = j["continue"]
            else: break
            time.sleep(1.5)
    except Exception as e:
        print("ERR commons", cat or q, e); continue
    got = 0
    # prefer larger, skip obvious duplicates/derivatives
    items = sorted(pages.values(), key=lambda p: -((p.get("imageinfo") or [{}])[0].get("width") or 0))
    for p in items:
        if got >= n: break
        ii = (p.get("imageinfo") or [{}])[0]; em = ii.get("extmetadata", {})
        lic = (em.get("LicenseShortName", {}).get("value", "") + " " + em.get("License", {}).get("value", "") + " " + em.get("Copyrighted", {}).get("value", ""))
        if not (OK_LIC.search(lic) or em.get("Copyrighted", {}).get("value", "").lower() == "false"): continue
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff"): continue
        if (ii.get("width") or 0) < cfg.get("min_width", 900): continue
        title = p["title"]
        if title in seen: continue
        seen.add(title)
        turl = ii.get("thumburl") or ii.get("url")
        fn = f"{tag}_{len(sources):03d}.jpg"
        try:
            d = get(turl)
            (img / fn).write_bytes(d.content)
        except Exception as e:
            print("ERR img", title, e); continue
        sources.append({"file": fn, "title": title, "page": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                        "license": em.get("LicenseShortName", {}).get("value", ""), "artist": re.sub("<[^>]+>", "", em.get("Artist", {}).get("value", ""))[:120],
                        "query": cat or q, "width": ii.get("width"), "height": ii.get("height")})
        got += 1; time.sleep(1.2)
    print("OK commons", cat or q, got)
json.dump(sources, open(out / "sources.json", "w"), indent=1)
print("images:", len(sources))
