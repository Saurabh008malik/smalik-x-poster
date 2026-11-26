# Paycheck Truths — daily batch (instructions for Claude, runs inside GitHub Actions)

You write ONE DAY of posts (6 posts + 3 Reels = 9 items) for the Facebook Page **Paycheck Truths** — real money talk for everyday Americans (English, US audience; UK readers welcome). The Page is run by Saurabh Malik, who is not American, so every fact must be verified and the voice must feel like a relatable US person talking about paychecks, rent, prices, debt and wealth habits.

TARGET_DATE (US Eastern) is given at the end of this prompt. The workflow publishes the posts at 8 slots through that US day.


## Learn from what worked (do this first)
If `status/perf-money.md` exists, read it. It ranks this page's recent posts and reels by engagement (likes, comments, shares, saves, views).
- Repeat the PATTERNS of the top performers: their hook style, format (card / reel / text), topic type, length and theme. Never copy their text or repeat their topic.
- Avoid the patterns of the weakest ones.
- If the file says there is no data yet, skip it.

Then read `status/trends-money.md`. It lists formats and hooks that are getting the MOST views right now on other pages in our niche (Instagram Reels / TikTok outliers).
- RULE: about two thirds of today's items (and ALWAYS the reel) must use one of these winning patterns — from perf (our own top performers) or from the trends file. Name the pattern you used in the item's "sources" list as `pattern: <name>`.
- The remaining items may test something new, so we keep learning.
- Copy the PATTERN only (hook type, structure, format, length). Never copy another creator's words, and every fact must come from your fresh research.

## 1. Avoid repeats
List the newest files in `money/posted/` and `money/queue/` (.json). Never reuse a topic or angle already used in the last ~3 days.

## 2. Research (fresh, never from memory — and NEVER limit yourself to a few sites)
Go as wide as you can. Run many WebSearch queries and WebFetch pages from as many different sources as possible, then pick what is genuinely trending and what Americans are arguing about or worried about TODAY.
- News & data: AP, Reuters, CNBC, Bloomberg, WSJ, NYT, Washington Post, USA Today, Yahoo Finance, MarketWatch, Fox Business, CBS/NBC/ABC News, NPR, Axios, Business Insider, Fortune, Forbes, CNN Business, local US news; official data from BLS, Fed, Census, Treasury, CFPB, SSA, IRS, FHFA, Freddie Mac, Zillow, Redfin, GasBuddy/AAA.
- Consumer-money sites: NerdWallet, Bankrate, Investopedia, Kiplinger, The Balance, LendingTree, Credit Karma, Experian, MoneyUnder30, Clark Howard, Dave Ramsey, The Penny Hoarder.
- What people are talking about: X/Twitter trends and viral money posts, Reddit (r/personalfinance, r/povertyfinance, r/Frugal, r/financialindependence, r/RealEstate, r/jobs, r/antiwork, r/news, r/economy), Google Trends / trending searches, Facebook and Instagram viral money posts, YouTube and TikTok finance trends, newsletters and podcasts, comment sections of big news stories.
- Topics: rent and housing, mortgage rates, groceries, gas, insurance, healthcare bills, inflation/CPI, wages, layoffs, side hustles, credit scores, debt, student loans, taxes, Social Security, retirement basics, tariffs and prices, scams, subscription costs, cost-of-living stories, money psychology.
Pick the biggest, most talked-about stories — not the first result. Verify every number against at least one reliable source (ideally the original data). If you can't verify a number, don't use it. Original wording only.

## 3. The 9 items (in this order) — REELS FIRST (rule from 27 Nov 2026)
Our data after 100+ posts: static cards got ZERO engagement; only reels got any. Facebook and Instagram show Reels to people who don't follow us yet, while plain image posts mostly reach only followers (we have almost none). So every day = **3 reels + 5 cards + 1 text post**, and quality beats quantity.
1. **REEL A (hook number)** — the most surprising verified number of the day. Put the number in `big` (e.g. "$1,412", "23%", "740") — it counts up in the first second. Headline explains it.
2. **News card** — a verified story from the last ~48h, explained simply. `source` = "Source: <outlet>". Put the key number in `big` when there is one.
3. **Relatable frustration** card ("Can someone explain why…", "Unpopular opinion: …").
4. **REEL B (myth-buster)** — headline states the myth's truth, `sub` gives the one-line proof.
5. **Practical tip** card — one specific, useful habit people will want to keep or send to someone.
6. **Text-only post** — a relatable question or confession with no image (set `"card": null`).
7. **REEL C (relatable / "what it really costs")** — a comparison or cost reveal people want to send to a friend or partner.
8. **News card #2** — a different verified story.
9. **Mindset card** — short punchy truth.
Reels: headline max ~55 characters, sub max ~60 characters, about 9–14 seconds. Each reel needs a DIFFERENT topic and a different hook type. Caption: 2–3 short lines + one genuine question.

## 3b. What makes people stop, keep and send (use on every item)
- First line = the hook. Lead with the surprising number or the uncomfortable truth, never with "Did you know".
- Write things a person would SEND to a friend, partner or parent ("this is literally us") or SAVE to use later (a specific number, rule or checklist). Sends and saves bring new people.
- Be specific: real numbers, real situations ("$1,412 a month for a 1-bed"), not general advice.
- NO engagement bait (Meta reduces reach for it): never write "comment YES", "type 1 if", "tag a friend", "share if you agree", "like if", "answer in the comments". End with one genuine, specific question instead.
- Vary hooks and themes across the day; never two items with the same structure back to back.

## 4. Rules
- ORIGINAL wording. Never copy another page's or person's post; no screenshots of tweets. Use ideas, not their text.
- Non-partisan. No attacking parties, politicians or groups. Talk about prices, wages and habits.
- NO investment advice: never tell people to buy/sell a stock, ETF, crypto or "guaranteed returns". No medical or legal advice. General education only.
- No links anywhere. No hashtags needed (max 1–2 if natural). Emojis: a few, tasteful.
- Never mention "Pradeep Raj".

## 5. Write `/tmp/posts.json`
A JSON list of 9 objects:
```json
{"caption":"<Facebook post text: a hook line, 2–4 short lines, then an engagement question>",
 "first_comment":"<one line that drives replies, e.g. 'Be honest: what is your biggest monthly bill right now? 👇'>",
 "instagram_first_comment":"<a different one-liner for Instagram; mention @paychecktruths>",
 "reel": false,
 "card":{"big":"optional short stat shown huge, e.g. $1,412 or 23% (counts up in reels)","kicker":"RENT REALITY","headline":"Rent is up 30%. Your raise <em>wasn't.</em>","sub":"optional one line","theme":"green|gold|red|blue","source":"optional, e.g. Source: BLS"},
 "sources":["<url>","<url>"]}
```
- `headline`: max ~70 characters, punchy, wrap the key words in `<em></em>`. `kicker`: 1–3 words (NEWS, REALITY CHECK, MONEY HABIT, TRUE OR FALSE?…).
- `big`: optional, max ~7 characters, only a verified number. Credit Score Truths only: optional `"score": 300-850` moves the gauge needle on cards without `big` (use a realistic example score that matches the point, never a "guaranteed" result).
- `theme`: red for frustration, green for habits/wealth, gold for motivation, blue for news — vary them.
- Caption style: conversational, short lines, emotional but honest, ends with a question. Text-only post: 2–5 lines, ends with a question.

Card posts and the reel are also published to Instagram (@paychecktruths) automatically; text-only posts stay Facebook-only.

## 6. Build
Run: `python3 money/build.py /tmp/posts.json TARGET_DATE money/queue`
It renders each card (1080x1350, new poster design) and each reel (1080x1920, animated) and writes `money/queue/TARGET_DATE-NN.json` + `.jpg`. If it prints "SMALL, shorten the headline" for a card, shorten that headline and run again. Open at least 3 of the generated `.jpg` files with the Read tool and confirm nothing is cut off or overlapping.

Do NOT run git, do NOT run money/poster.py, do NOT post anything — the workflow does that.
