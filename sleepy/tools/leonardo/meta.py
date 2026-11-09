import json, re, glob
tl=json.load(open('timeline.json')); durs={int(k):v for k,v in tl['durs'].items()}
titles=[re.match(r'## Chapter \d+: (.*)',open(f'script/ch{n:02d}.txt').readline()).group(1) for n in range(1,13)]
def ts(sec):
    sec=int(round(sec)); h,m,s=sec//3600,sec%3600//60,sec%60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
lines=[]; cum=6.0
for n in range(1,13):
    lines.append(f'{ts(0 if n==1 else cum)} {titles[n-1]}')
    cum+=durs[n]
total=tl['total']; hrs=int(total//3600); mins=int(round(total%3600/60))
src=json.load(open('img/sources.json'))
used=set()
import ast
for l in open('assemble.py'):
    pass
dur_txt=f'{hrs} hours {mins} minutes' if hrs else f'{mins} minutes'
M=f'''TITLE
Fall Asleep to the Life of Leonardo da Vinci | Biography for Sleep

DESCRIPTION
Settle in, dim the lights and listen to the life of Leonardo da Vinci: the boy from the hills of Vinci who became a painter, an engineer, a student of water and birds and the human heart, and one of the most curious people who ever lived. A calm, slow-paced biography for sleep, about {hrs} hours long, told gently from his birth in Tuscany in 1452 to his last days beside the river Loire in 1519.

🌙 Best with a low volume and the screen dimmed. You can let it play through the night.

CHAPTERS
''' + "\n".join(lines) + f'''

ABOUT THIS VIDEO
The narration is AI-generated (open-source text-to-speech voice) and is disclosed as altered or synthetic content. The script was written and fact-checked from reliable sources. The images are historical public-domain artworks, drawings, manuscripts and prints. The fireplace sound is synthesized and copyright free. Imagined scenes are marked as imagined in the narration, and later stories about Leonardo are marked as stories.

MAIN SOURCES
- Museo Galileo, Florence: Leonardo's childhood and his years in Milan
- Encyclopaedia Britannica: Leonardo da Vinci
- The Louvre Museum: Mona Lisa
- UNESCO World Heritage: Santa Maria delle Grazie and The Last Supper
- Royal Collection Trust: Leonardo's study of anatomy
- Museo Leonardiano, Vinci: biography
- Google Arts and Culture: Clos Lucé

IMAGE CREDITS
Public-domain images from Wikimedia Commons, including paintings, drawings and manuscript pages by Leonardo da Vinci, works by Verrocchio, Raphael, Titian, Ingres and Rubens, and period maps and prints. Full list of file pages on request in the comments.

This video is for history and relaxation only. It is not medical advice. If you have trouble sleeping regularly, please talk to a doctor.

Subscribe to The Sleepy Biographer for a new calm biography every week.

#BiographyForSleep #LeonardoDaVinci #HistoryForSleep #SleepStory #BedtimeHistory

TAGS (comma separated)
leonardo da vinci, leonardo da vinci biography, biography for sleep, history for sleep, sleep story, bedtime history, fall asleep to history, boring history for sleep, leonardo da vinci documentary, leonardo da vinci life story, renaissance history, mona lisa, the last supper, italian renaissance, relaxing history, calm narration, sleepy biographer, history to fall asleep to, 2 hour biography, fireplace history

FIRST COMMENT (post right after publishing, then pin it)
Welcome, and goodnight. 🌙 If you are listening tonight, tell us where you are in the world and what time it is there. And who should The Sleepy Biographer put to bed next? Leave a name below.

UPLOAD CHECKLIST (YouTube Studio)
1. Upload video.mp4, set the thumbnail to thumbnail.jpg.
2. Visibility: Schedule for Tuesday 17 Nov 2026, 7:00 pm New York time (= Wed 18 Nov, 5:30 am IST).
3. Audience: No, it's not made for kids.
4. Altered content: Yes (AI-generated voice).
5. Category: Education. Language: English.
6. Playlist: Artists & Writers for Sleep.
7. Paste the first comment, pin it.
8. After 48 hours and 7 days, send Claude the views, average view duration and click-through rate for the Results log.
'''
open('metadata.txt','w').write(M); print(M[:1500])
