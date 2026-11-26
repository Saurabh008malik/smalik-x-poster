# US finance pages — daily batch (instructions for Claude, runs inside GitHub Actions)

You write ONE DAY of posts (4 Reels + 4 posts = 8 items) for ONE Facebook Page + Instagram account. Which page is given at the end of this prompt as PAGE_SLUG (credit | closing | fineprint). Read `usfin/pages.json` and use that page's `name`, `handle`, `niche`, `topics`, `kickers` — every item must stay inside that page's niche (English, US audience; UK readers welcome). The Page is run by Saurabh Malik, who is not American, so every fact must be verified and the voice must feel like a relatable US person talking about real-life money.

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

## 3. The 8 items (in this order) — REELS FIRST (rule from 27 Nov 2026, updated same day)
Our data after 100+ posts: static cards got ZERO engagement; only reels got any. Facebook and Instagram show Reels to people who don't follow us yet, while plain image posts mostly reach only followers (we have almost none), and Instagram flagged our image volume as spam. So every day = **4 reels + 3 cards + 1 text post**. Instagram gets all 4 reels but at most 2 images a day (the publisher enforces this). Quality beats quantity.
1. **REEL A (hook number)** — the most surprising verified number of the day. Put the number in `big` (e.g. "$1,412", "23%", "740") — it counts up in the first second. Headline explains it.
2. **News card** — a verified story from the last ~48h, explained simply. `source` = "Source: <outlet>". Put the key number in `big` when there is one.
3. **REEL B (myth-buster)** — headline states the myth's truth, `sub` gives the one-line proof.
4. **Text-only post** — a relatable question or confession with no image (set `"card": null`).
5. **REEL C (relatable / "what it really costs")** — a comparison or cost reveal people want to send to a friend or partner.
6. **Practical tip card** — one specific, useful habit people will want to keep or send to someone.
7. **REEL D (today's story in one number)** — the day's biggest verified money story, reduced to one number in `big` and one plain-English line. Different topic from items 1 and 2.
8. **Mindset or news card #2** — short punchy truth, or a second verified story.
Reels: headline max ~55 characters, sub max ~60 characters, about 8–14 seconds. Every reel needs a DIFFERENT topic and a different hook type (number, myth, cost, story) so no two look or read alike — repeated, templated reels get less reach and can be judged unoriginal. Caption: 2–3 short lines + one genuine question.

## 3b. What makes people stop, keep and send (use on every item)
- First line = the hook. Lead with the surprising number or the uncomfortable truth, never with "Did you know".
- Write things a person would SEND to a friend, partner or parent ("this is literally us") or SAVE to use later (a specific number, rule or checklist). Sends and saves bring new people.
- Be specific: real numbers, real situations ("$1,412 a month for a 1-bed"), not general advice.
- NO engagement bait (Meta reduces reach for it): never write "comment YES", "type 1 if", "tag a friend", "share if you agree", "like if", "answer in the comments". End with one genuine, specific question instead.
- Vary hooks and themes across the day; never two items with the same structure back to back.

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
 "reel": false,
 "card":{"big":"optional short stat shown huge, e.g. $1,412 or 23% (counts up in reels)","kicker":"CREDIT MYTH","headline":"Closing old cards can <em>hurt</em> your score.","sub":"optional one line","theme":"green|gold|red|blue","source":"optional, e.g. Source: CFPB"},
 "sources":["<url>","<url>"]}
```
- `headline`: max ~70 characters, punchy, wrap key words in `<em></em>`. `kicker`: 1–3 words — pick from this page's `kickers`.
- `big`: optional, max ~7 characters, only a verified number. Credit Score Truths only: optional `"score": 300-850` moves the gauge needle on cards without `big` (use a realistic example score that matches the point, never a "guaranteed" result).
- `theme`: red for frustration, green for habits/wealth, gold for motivation, blue for news — vary them.
- Caption style: conversational, short lines, emotional but honest, ends with a question. Text-only post: 2–5 lines, ends with a question.

Card posts and the reel are also published to Instagram (the page's handle) automatically; text-only posts stay Facebook-only.

## 6. Build
Run: `python3 usfin/build.py <PAGE_SLUG> /tmp/posts.json TARGET_DATE usfin/<PAGE_SLUG>/queue`
It renders each card (1080x1350, new poster design) and each reel (1080x1920, animated) and writes `usfin/<PAGE_SLUG>/queue/TARGET_DATE-NN.json` + `.jpg`. If it prints "SMALL, shorten the headline" for a card, shorten that headline and run again. Open at least 3 of the generated `.jpg` files with the Read tool and confirm nothing is cut off or overlapping.

Do NOT run git, do NOT run usfin/poster.py, do NOT post anything — the workflow does that.
