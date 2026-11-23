import json
tl = json.load(open('/home/claude/austen/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ["Welcome, and a Winter Birth at Steventon", "A Rectory Full of Boys, and a Fever Far from Home",
         "Plays in the Barn, and Stories in Little Notebooks", "Dancing Days, and a Young Irishman",
         "First Impressions, Returned Unopened", "The White Glare of Bath", "A Proposal at Manydown, and a Winter of Loss",
         "Wandering Years, Sailor Brothers, and a Letter Signed M.A.D.", "Home at Chawton, and a Book by a Lady",
         "Her Own Darling Child", "Emma, a Royal Library, and Persuasion", "Sanditon, Winchester, and a Gentle Goodnight"]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {n}. {names[n-1]}"); t += durs[n]
mins = round(tl['total'] / 60); dur = ts(tl['total'])
title = "Jane Austen: A Quiet Life of Ink and Wit | Biography for Sleep"
desc = f"""Fall asleep to the true story of Jane Austen, the clergyman's daughter who wrote Pride and Prejudice, Emma and Persuasion at a small table in a Hampshire cottage. In this calm, slow biography we follow her from a snowy winter birth at Steventon rectory in 1775, through the family plays in the barn, her teenage notebooks, country dances and Tom Lefroy, a first novel turned down unread, the years in Bath and Southampton with her sailor brothers, the quiet home at Chawton where her books finally went out into the world "By a Lady", a visit to the Prince Regent's library, and her last days in Winchester in 1817. About {mins} minutes of gentle narration over a quiet fireside sound.

🌙 CHAPTERS
""" + "\n".join(lines) + """

📚 SOURCES
- Jane Austen's Letters (letters to Cassandra, Frank, Anna Austen, Fanny Knight, James Edward Austen and others; public-domain editions)
- Henry Austen, Biographical Notice of the Author (1817, in Northanger Abbey and Persuasion)
- James Edward Austen-Leigh, A Memoir of Jane Austen (1870)
- William and Richard Arthur Austen-Leigh, Jane Austen: Her Life and Letters, a Family Record (1913, Project Gutenberg)
- Jane Austen's House (Chawton) and Winchester Cathedral visitor information; Encyclopaedia Britannica: Jane Austen
- Bank of England, Bank Underground: Jane Austen's income (2019)
Short lines are quoted only from Jane Austen's own letters and from family letters of the time (all public domain). Stories that come only from later family memory (for example the fainting at the news of the move to Bath, the creaking door at Chawton, the young man met at the seaside) are marked as such in the narration. Nobody knows for certain what illness she died of; the narration says so.

🎙 Narration: AI-generated voice (Kokoro, open source). Research, script writing, fact-checking and production: The Sleepy Biographer. This video is labelled as altered/synthetic content.
🖼 Images: public-domain and CC0 portraits, letters, paintings, prints and book illustrations from Wikimedia Commons (including Cassandra Austen's sketch of her sister, the 1870 Memoir engraving, Hugh Thomson's and C. E. Brock's illustrations of the novels, and prints of Bath, Carlton House and Winchester). Fireside sound: synthesized by us.

This is a calm history story for rest and sleep. It is not medical, legal or financial advice.

New biography every Tuesday and Friday. Subscribe for more calm history for sleep.

#HistoryForSleep #BiographyForSleep #JaneAusten"""
tags = "jane austen, jane austen biography, pride and prejudice, life of jane austen, regency era, english literature, chawton, history for sleep, biography for sleep, fall asleep to history, sleep story for adults, bedtime history, calm biography, history documentary, relaxing history, sleepy history, boring history for sleep, writers for sleep"
comment = "Welcome, and goodnight. 🌙 Jane Austen wrote her novels on small sheets of paper at a little table by the window, and almost nobody knew her name. Which of her heroines do you love most: Elizabeth, Anne, Emma, Elinor, Fanny or Catherine? And who should The Sleepy Biographer tell next?"
meta = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (post from the channel 60 minutes after it goes public; pin it by hand in Studio)
{comment}

PLAYLIST
Artists & Writers for Sleep

UPLOAD CHECKLIST
- Visibility: Schedule, Wed 2 Dec 2026 05:30 IST (= Tue 1 Dec 2026 7:00 PM New York = 2026-12-02T00:00:00Z)
- Altered or synthetic content: Yes
- Made for kids: No
- Category: Education; Language: English
- Thumbnail: thumbnail.jpg
- Playlist: Artists & Writers for Sleep
- Chapters: on (first at 0:00)
- End screen: Subscribe + best video
- First comment: queued in ytq/comments.json (posts 60 min after public); pin it by hand

SLOT
sleepy 2026-12-02 05:30 IST (2026-12-02T00:00:00Z)

FILES
Video backup: branch backup-sleepy-austen (90 MB parts; join with: cat sleepy_v06_austen.mp4.part* > video.mp4)
Duration: {dur}
"""
open('/home/claude/austen/metadata.txt', 'w').write(meta)
json.dump({'title': title, 'comment': comment, 'duration': dur}, open('/home/claude/austen/meta_out.json', 'w'))
print(len(desc), 'chars desc;', dur)
