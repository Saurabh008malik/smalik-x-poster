# Smalik Cricket Poster

Auto-posts queued cricket tweets (text + image) to **@Smalik_wc** on X.

- Claude adds each tweet to `queue/` (a `.json` with the text + a `.png` card).
- GitHub Actions checks every 15 min during 8:30–11:30 AM and 7:30–10:30 PM IST.
- A tweet posts once it has waited **45 minutes**. **To cancel: delete its files from `queue/`** before then.
- Posted tweets move to `posted/` (with the tweet link), failed ones to `failed/`.
- Max 3 posts per day. X keys live only in repo Secrets.

**Test the keys:** Actions tab → "Post queued tweets" → Run workflow → mode `check`.
