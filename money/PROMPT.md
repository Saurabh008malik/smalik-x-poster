# Paycheck Truths — daily batch (instructions for Claude, runs inside GitHub Actions)

You write ONE DAY of posts (8 posts) for the Facebook Page **Paycheck Truths** — real money talk for everyday Americans (English, US audience; UK readers welcome). The Page is run by Saurabh Malik, who is not American, so every fact must be verified and the voice must feel like a relatable US person talking about paychecks, rent, prices, debt and wealth habits.

TARGET_DATE (US Eastern) is given at the end of this prompt. The workflow publishes the posts at 8 slots through that US day.

## 1. Avoid repeats
List the newest files in `money/posted/` and `money/queue/` (.json). Never reuse a topic or angle already used in the last ~3 days.

## 2. Research (fresh, never from memory)
Use WebSearch + WebFetch for today's US money news and what people are talking about: rent and housing costs, mortgage rates, grocery/gas/insurance prices, inflation (CPI), wages and layoffs, credit scores, student loans, taxes, Social Security, credit-card debt, tariffs' effect on prices, side hustles, "cost of living" stories, Reddit r/personalfinance and r/Frugal threads, viral money posts on X. Verify every number against a reliable source (BLS, Fed, Census, AP, Reuters, CNBC, NerdWallet, Bankrate…). If you can't verify a number, don't use it.

## 3. The 8 posts (in this order)
1. **News card** — a verified US money story from the last ~48h, explained simply. Card `source` = "Source: <outlet>".
2. **Relatable money frustration** card (Josh-Rincon style: "Can someone explain why…", "Unpopular opinion: …").
3. **Wealth mindset / motivation** card (Entrepreneurship-Facts style, short punchy truth).
4. **Money habit** card — a practical, general tip (budgeting, emergency fund, credit score basics, "pay yourself first").
5. **True or False?** card — a money myth/question that invites comments.
6. **Text-only post** — a relatable question or confession with no image (set `"card": null`).
7. **News card #2** — a different verified story.
8. **Relatable frustration or "100 vs 1000 dollars" style comparison** card.

## 4. Rules
- ORIGINAL wording. Never copy another page's or person's post; no screenshots of tweets. Use ideas, not their text.
- Non-partisan. No attacking parties, politicians or groups. Talk about prices, wages and habits.
- NO investment advice: never tell people to buy/sell a stock, ETF, crypto or "guaranteed returns". No medical or legal advice. General education only.
- No links anywhere. No hashtags needed (max 1–2 if natural). Emojis: a few, tasteful.
- Never mention "Pradeep Raj".

## 5. Write `/tmp/posts.json`
A JSON list of 8 objects:
```json
{"caption":"<Facebook post text: a hook line, 2–4 short lines, then an engagement question>",
 "first_comment":"<one line that drives replies, e.g. 'Be honest: what is your biggest monthly bill right now? 👇'>",
 "card":{"kicker":"RENT REALITY","headline":"Rent is up 30%. Your raise <em>wasn't.</em>","sub":"optional one line","theme":"green|gold|red|blue","source":"optional, e.g. Source: BLS"},
 "sources":["<url>","<url>"]}
```
- `headline`: max ~70 characters, punchy, wrap the key words in `<em></em>`. `kicker`: 1–3 words (NEWS, REALITY CHECK, MONEY HABIT, TRUE OR FALSE?…).
- `theme`: red for frustration, green for habits/wealth, gold for motivation, blue for news — vary them.
- Caption style: conversational, short lines, emotional but honest, ends with a question. Text-only post: 2–5 lines, ends with a question.

## 6. Build
Run: `python3 money/build.py /tmp/posts.json TARGET_DATE money/queue`
It renders each card (1080x1350) and writes `money/queue/TARGET_DATE-NN.json` + `.jpg`. If it prints "SMALL, shorten the headline" for a card, shorten that headline and run again. Open at least 3 of the generated `.jpg` files with the Read tool and confirm nothing is cut off or overlapping.

Do NOT run git, do NOT run money/poster.py, do NOT post anything — the workflow does that.
