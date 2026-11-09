# The Sleepy Biographer - automatic publishing

Claude produces each video (script, AI narration, public-domain images, video, thumbnail) and puts it in a **draft GitHub release**.
It adds one line per video/Short to `queue.json`. This repo then posts it at the planned time:
video + thumbnail + "altered/synthetic content" flag + playlist + first comment.

- Long videos: Tue & Fri, 23:40 UTC (6:40 pm New York, 11:40 pm London)
- Shorts: Mon, Wed, Thu, Sat, 15:10 UTC (10:10 am New York) - cut from the same stories, never reused
- Policy: AI voice always disclosed, no mass-produced or repeated uploads, original script each time, public-domain images only,
  first comment is posted by the channel (YouTube's API cannot pin it - pin it by hand in Studio when you like).

## One-time setup
1. Sign in at script.google.com with saurabh.malik008@gmail.com, New project "Sleepy Biographer uploader".
2. Project Settings -> "Show appsscript.json manifest file" -> replace its contents with `sleepy/appsscript.json`.
3. Editor: replace Code.gs with `sleepy/appsscript.gs` and put the KEY Claude gives you on the first line.
4. Services (+) -> YouTube Data API v3 -> Add.
5. Run `testConnection` -> Allow -> when Google asks which channel, choose **The Sleepy Biographer**.
6. Deploy -> New deployment -> Web app -> Execute as **Me**, Who has access **Anyone** -> Deploy -> copy the Web app URL.
7. Send Claude the URL (it is not a password; the KEY is what protects it). Claude stores `URL?k=KEY` as GitHub secret `SLEEPY_HOOK`.
8. Actions -> "The Sleepy Biographer - publish due videos and Shorts" -> Run workflow -> action `whoami` -> it must say The Sleepy Biographer.
