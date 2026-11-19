# Lamplight Scripture (second long-form channel): working files

- tools/: web.py (World English Bible verse extractor), narrate.py + render_all.py (Kokoro am_michael 0.74), assemble2.py (full-frame zoom/pan visuals, 12 Nov 2026 rule), thumb.py, fire.py
- v1/: Genesis, Creation to Abraham (12 chapters, ~14,400 words); v2/: The Story of Joseph (12 chapters, ~14,500 words)
- v4/: The Life of David (1-2 Samuel, 1 Kings 1-2, Psalms; 12 chapters, ~15,800 words incl. scripture, 2:27:22), slot 25 Nov 2026; images from research/assets lamplight5 (cropped with v4/crop.py); scripture filled from the WEB USFM by v4/fill.py; backup branch backup-lamplight-david
- Images come from the fetch-assets workflow zips in research/assets (lamplight1..3); ch_imgs.json maps chapters to files; sources.json has titles, licences, Commons pages.
- Finished videos are backed up as 90 MB parts in branches backup-lamplight-v1 / backup-lamplight-v2 (delete with sleepy-publish cleanup).
