# US finance pages — daily batch (instructions for Claude, runs inside GitHub Actions)

You write ONE DAY of posts (8 posts + 1 Reel = 9 items) for ONE Facebook Page + Instagram account. Which page is given at the end of this prompt as PAGE_SLUG (credit | closing | fineprint). Read `usfin/pages.json` and use that page's `name`, `handle`, `niche`, `topics`, `kickers` — every item must stay inside that page's niche (English, US audience; UK readers welcome). The Page is run by Saurabh Malik, who is not American, so every fact must be verified and the voice must feel like a relatable US person talking about real-life money.

TARGET_DATE (US Eastern) is given at the end of this prompt. The workflow publishes the posts at 8 slots through that US day.

Folders for this page: `usfin/<PAGE_SLUG>/posted`, `usfin/<PAGE_SLUG>/queue`. Status files: `status/perf-<PAGE_SLUG>.md` and `status/trends-money.md`.


## Learn from what worked (do this first)
If `status/perf-<PAGE_SLUG>.md` exists, read it. It ranks this page's recent posts and reels by engagement. If this page has no data yet, also read `status/perf-money.md` (our sister page Paycheck Truths) — the same patterns usually work.
- Repeat the PATTERNS of the top performers: hook style, format (card / reel / text), topic type, length and theme. Never copy their text or repeat their topic.
- Avoid the patterns of the weakest ones.

Then read `status/trends-money.md` (formats and hooks getting the MOST views right now in the money niche on Instagram Reels / TikTok).
- RULE: about two thirds of today's items (and ALWAYS the reel) must use one of these winning patterns — from perf or from the trends file. Name the pattern in the item's "sources" list as `pattern: <name>`.
- The remaining items may test something new, so we keep learning.
- Copy the PATTERN only. Never copy another creator's words; every fact must come from your fresh research.

## 1. Avoid repeats
List the newest files in `usfin/<PAGE_SLUG>/posted/` and `usfin/<PAGE_SLUG>/queue/` (.json). Never reuse a topic or angle already used in the last ~5 days.

## 2. Research (fresh, never from memory — and NEVER limit yourself to a few sites)
Go wide. Run many WebSearch queries and WebFetch pages across news (AP, Reuters, CNBC, Bloomberg, WSJ, NYT, Washington Post, USA Today, Yahoo Finance, MarketWatch, NPR, Axios, Business Insider, Fortune, Forbes, local US news), official data and regulators (CFPB, FTC, Fed, NY Fed, BLS, Census, FHFA, Freddie Mac, Treasury, IRS, SSA, state AGs), consumer sites (NerdWallet, Bankrate, Investopedia, Kiplinger, LendingTree, Credit Karma, Experian, Consumer Reports, The Penny Hoarder), and what people are talking about (X/Twitter, Reddit — r/personalfinance, r/povertyfinance, r/RealEstate, r/FirstTimeHomeBuyer, r/CreditCards, r/Frugal — Google Trends, TikTok/Instagram/Facebook viral money posts, comment sections of big stories).
Page topics to lean on: the `topics` field for this page in `usfin/pages.json`.
Pick the biggest, most talked-about stories — not the first result. Verify every number against at least one reliable source (ideally the original data). If you can't verify a number, don't use it. Original wording only.

## 3. The 9 items (in this order)
1. **News card** — a verified story in this page's niche from the last ~48h, explained simply. Card `source` = "Source: <outlet>".
2. **Relatable frustration** card ("Can someone explain why…", "Unpopular opinion: …").
3. **Mindset / motivation** card — short punchy truth in the niche.
4. **Practical tip** card — a general, useful habit or checklist item.
5. **True or False?** card — a myth/question that invites comments.
6. **Text-only post** — a relatable question or confession with no image (set `"card": null`).
7. **News card #2** — a different verified story.
8. **Comparison or "what it really costs" card** (e.g. "Pay now vs pay later", "$100 vs $1,000").
9. **REEL** — short animated text video (9:16). Set `"reel": true` and give it a `card`. Strong hook and a REVEAL: the headline appears word by word, then the `sub` line at the end (e.g. a myth-buster: headline "Checking your own credit score does <em>NOT</em> lower it." + sub "It's a soft inquiry. No impact on your score."). Headline max ~55 characters, sub max ~60 characters. Caption: 2–3 short lines + question. Published around noon New York time. The reel music is royalty-free and picked by theme automatically (optional `"music": "calm|focus|uplift"`).

## 4. Rules
- ORIGINAL wording. Never copy another page's post; no screenshots of tweets.
- Non-partisan. No attacking parties, politicians, companies or groups. Talk about prices, rules and habits.
- NO investment, legal, tax or medical advice: never tell people to buy/sell a stock/crypto, never "guaranteed" anything. General education only, and say "check your own situation / a professional" where it matters. Never promise credit repair or guaranteed score gains.
- No links anywhere. Max 1–2 hashtags, only if natural. Emojis: a few, tasteful.
- Never mention "Pradeep Raj".

## 5. Write `/tmp/posts.json`
A JSON list of 9 objects:
```json
{"caption":"<Facebook post text: a hook line, 2–4 short lines, then an engagement question>",
 "first_comment":"<one line that drives replies, e.g. 'Be honest: what is your biggest monthly bill right now? 👇'>",
 "instagram_first_comment":"<a different one-liner for Instagram; mention the page handle>",
 "card":{"kicker":"CREDIT MYTH","headline":"Closing old cards can <em>hurt</em> your score.","sub":"optional one line","theme":"green|gold|red|blue","source":"optional, e.g. Source: CFPB"},
 "sources":["<url>","<url>"]}
```
- `headline`: max ~70 characters, punchy, wrap key words in `<em></em>`. `kicker`: 1–3 words — pick from this page's `kickers`.
- `theme`: red for frustration, green for habits/wealth, gold for motivation, blue for news — vary them.
- Caption style: conversational, short lines, emotional but honest, ends with a question. Text-only post: 2–5 lines, ends with a question.

Card posts and the reel are also published to Instagram (the page's handle) automatically; text-only posts stay Facebook-only.

## 6. Build
Run: `python3 usfin/build.py <PAGE_SLUG> /tmp/posts.json TARGET_DATE usfin/<PAGE_SLUG>/queue`
It renders each card (1080x1350) and writes `usfin/<PAGE_SLUG>/queue/TARGET_DATE-NN.json` + `.jpg`. If it prints "SMALL, shorten the headline" for a card, shorten that headline and run again. Open at least 3 of the generated `.jpg` files with the Read tool and confirm nothing is cut off or overlapping.

Do NOT run git, do NOT run usfin/poster.py, do NOT post anything — the workflow does that.
