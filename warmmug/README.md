# ☕ Warm Mug Radio (music channel)

Separate from the cricket and money pages. Builds cozy jazz-hop / lofi mixes and posts them to the
Warm Mug Radio YouTube channel on **Tuesday and Saturday ~6 AM IST** (evening in the US).

## How it works
1. Claude adds finished tracks to `inbox.json` (name + download link). Only royalty-free / commercially
   licensed music goes in: vidIQ music, or Suno songs made on a **paid** Suno plan.
2. `warmmug-publish.yml` takes up to 60 min of new tracks, crossfades them, levels the volume, draws a cozy
   window scene + thumbnail (`art.py`), renders the video and uploads it with the next title from `titles.txt`,
   a tracklist with chapters, and YouTube's "altered or synthetic content" flag switched on.
3. Posted mixes are logged in `published.json`; their tracks are never reused.
4. If less than 12 min of new music is waiting, nothing is posted that day.

## One-time setup (phone is fine)
1. Google Cloud: project → enable **YouTube Data API v3** → OAuth consent screen (External, then **Publish app**)
   → Credentials → OAuth client ID → type **TVs and Limited Input devices**. Put the client ID and secret in
   `oauth_client.json` as `{"client_id": "...", "client_secret": "..."}`.
2. Actions → **Warm Mug Radio - connect YouTube (one time)** → Run → open the run's Summary for the code →
   google.com/device → choose the **Warm Mug Radio** channel → Allow.
3. Test: Actions → **Warm Mug Radio - build and post a mix** → mode `preview` → download the video from Artifacts.

The saved login (`secret/yt_token.enc`) is encrypted with the `CLAUDE_CODE_OAUTH_TOKEN` secret.
If that secret is ever renewed, run the connect workflow again.
