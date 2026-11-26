"""Read-only Instagram health check: publishing quota, app usage headers, account basics. No posts, no tokens printed."""
import os, json, requests
G = "https://graph.facebook.com/v26.0"
accts = [("Cricket Ki Baat", "FB_PAGE_ID", "FB_PAGE_TOKEN"), ("Paycheck Truths", "MONEY_FB_PAGE_ID", "MONEY_FB_PAGE_TOKEN"),
         ("Credit Score Truths", "CREDIT_FB_PAGE_ID", "CREDIT_FB_PAGE_TOKEN"), ("Creator Adda", "ADDA_FB_PAGE_ID", "ADDA_FB_PAGE_TOKEN")]
for name, i, t in accts:
    pid, tok = os.environ.get(i), os.environ.get(t)
    print("==", name)
    if not pid or not tok:
        print("  secret missing"); continue
    r = requests.get(f"{G}/{pid}", params={"fields": "instagram_business_account", "access_token": tok}, timeout=30)
    hdr = {k: v for k, v in r.headers.items() if k.lower() in ("x-app-usage", "x-page-usage", "x-business-use-case-usage")}
    print("  page lookup", r.status_code, hdr)
    ig = (r.json().get("instagram_business_account") or {}).get("id") if r.ok else None
    if not ig:
        print("  no IG id:", r.text[:200]); continue
    for label, path, fields in (("account", ig, "username,media_count,followers_count"),
                                ("publishing limit", f"{ig}/content_publishing_limit", "quota_usage,config")):
        q = requests.get(f"{G}/{path}", params={"fields": fields, "access_token": tok}, timeout=30)
        h2 = {k: v for k, v in q.headers.items() if k.lower() in ("x-app-usage", "x-business-use-case-usage")}
        print(f"  {label}:", q.status_code, q.text[:400], h2)
