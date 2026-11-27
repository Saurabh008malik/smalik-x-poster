import json
B = '/home/claude/marie'
tl = json.load(open(B + '/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = [open(f'{B}/script/ch{n:02d}.txt').readline().split(':', 1)[1].strip() for n in range(1, 13)]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {n}. {names[n-1]}"); t += durs[n]
mins = round(tl['total'] / 60)
title = "Marie Antoinette: The Last Queen of Versailles | Biography for Sleep"
desc = f"""Fall asleep to the true story of Marie Antoinette, the little archduchess from Vienna who was sent to France at fourteen, became Queen at eighteen, and is still remembered for words she almost certainly never said. In this calm, slow biography we follow her from a November birth in the Hofburg in 1755, through an imperial childhood at Schönbrunn, the long road to France and the handover on an island in the Rhine, the rules of Versailles, the small house and the thatched village she loved at the Petit Trianon, motherhood and the portraits of Élisabeth Vigée Le Brun, the diamond necklace she never wanted, and the year 1789. Then, gently, the Tuileries, the night journey to Varennes, and her last autumn in 1793. About {mins} minutes of gentle narration over a quiet fireside sound, with calm animated chapter cards and two journey maps.

🌙 CHAPTERS
""" + "\n".join(lines) + """

📚 SOURCES
- Letters of Marie Antoinette and Maria Theresa (the Mercy-Argenteau correspondence), and Marie Antoinette's last letter to Madame Élisabeth, 16 October 1793 (public domain; short lines translated by us)
- Madame Campan, Memoirs of the Private Life of Marie Antoinette (1823) and Élisabeth Vigée Le Brun, Souvenirs (1835-37), used with care as later memoirs
- Marie-Thérèse Charlotte (Madame Royale), memoir of the Temple captivity; Jean-Baptiste Cléry, Journal of the Temple (1798)
- Johann Wolfgang von Goethe, Poetry and Truth (on the 1770 handover pavilion); Jean-Jacques Rousseau, Confessions, Book VI (the "great princess" and the brioche)
- Château de Versailles official site: the marriage of the Dauphin (1770), the Petit Trianon, the Queen's Hamlet, Richard Mique, Axel von Fersen
- Encyclopaedia Britannica: Marie Antoinette; the Affair of the Diamond Necklace; the Flight to Varennes
Stories that come from later memoirs or family tradition (Mozart at Schönbrunn, the bouquet of the Petit Trianon, the news reaching her in the grotto, her hair turning grey, the last words on the scaffold) are marked as such in the narration. The phrase "let them eat cake" has no good evidence linking it to her. The last part of her life is told gently, without graphic detail.

🎙 Narration: AI-generated voice (Kokoro, open source). Research, script writing, fact-checking and production: The Sleepy Biographer. This video is labelled as altered/synthetic content.
🖼 Images: public-domain and CC0 paintings, prints and photographs from Wikimedia Commons (including portraits by Élisabeth Vigée Le Brun, Duplessis, Wertmüller and Meytens, Bellotto's views of Schönbrunn, prints of the coronation at Reims, the balloon at Versailles, the Estates-General, the Festival of the Federation and Varennes, and views of the Hamlet and the Hall of Mirrors). Animated title, chapter cards, quote cards and maps: made by us. Fireside sound: synthesized by us.

This is a calm history story for rest and sleep. It is not medical, legal or financial advice.

New biography every Tuesday and Friday. Subscribe for more calm history for sleep.

#HistoryForSleep #BiographyForSleep #MarieAntoinette"""
tags = "marie antoinette, marie antoinette biography, queen of france, versailles, petit trianon, louis xvi, french revolution history, let them eat cake, vigee le brun, history for sleep, biography for sleep, fall asleep to history, sleep story for adults, bedtime history, calm biography, history documentary, relaxing history, kings and queens for sleep"
comment = "Welcome, and goodnight. 🌙 Marie Antoinette almost certainly never said \"let them eat cake\": a very similar story was already in Rousseau's Confessions while she was a girl in Vienna. Which part of her story surprised you most? And who should The Sleepy Biographer tell next?"
meta = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (post from the channel 60 minutes after it goes public; pin it by hand in Studio)
{comment}

PLAYLIST
Kings & Queens for Sleep

UPLOAD CHECKLIST
- Visibility: Schedule, Wed 9 Dec 2026 05:30 IST (= Tue 8 Dec 2026 7:00 PM New York = 2026-12-09T00:00:00Z)
- Altered or synthetic content: Yes
- Made for kids: No
- Category: Education; Language: English
- Thumbnail: thumbnail.jpg (variant B for Test & compare: thumbnail_b.jpg)
- Playlist: Kings & Queens for Sleep
- Chapters: on (first at 0:00)
- End screen: Subscribe + best video
- Pin the first comment by hand after it is posted

SLOT
2026-12-09 (Wed 05:30 IST), The Sleepy Biographer
"""
open(B + '/metadata.txt', 'w').write(meta)
json.dump({'title': title, 'description': desc, 'tags': [t.strip() for t in tags.split(',')], 'comment': comment}, open(B + '/meta_out.json', 'w'), indent=1, ensure_ascii=False)
print(len(desc), 'chars desc;', len(tags), 'chars tags;', len(title), 'title')
