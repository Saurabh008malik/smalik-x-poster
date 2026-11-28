import json, re, sys
sys.path.insert(0, '/home/claude/lamp7/tools')
import anim, maps7 as maps
B = '/home/claude/lamp7'
tl = json.load(open(B + '/timeline.json')); durs = {int(k): v for k, v in tl['durs'].items()}; LEAD = tl['lead']
ch = {int(k): v for k, v in json.load(open(B + '/ch_imgs.json')).items()}
starts = {}; c = LEAD
for n in range(1, 13): starts[n] = c; c += durs[n]
titles = {n: open(f'{B}/script/ch{n:02d}.txt').readline().split(':', 1)[1].strip() for n in range(1, 13)}
def at(n, needle):
    txt = open(f'{B}/script/ch{n:02d}.txt').read()
    paras = [p for p in txt.split('\n\n') if p.strip()]
    wts = [len(p) + 30 * len(re.findall(r'[.!?:]', p)) + 40 for p in paras]
    idx = next(i for i, p in enumerate(paras) if needle in p)
    return starts[n] + durs[n] * sum(wts[:idx]) / sum(wts)
import os; os.makedirs(B + '/anim', exist_ok=True)
I = lambda n, k: B + '/img/' + ch[n][k]
ev = []
ev.append(dict(t=0.0, secs=24.0, path=anim.title_card(B + '/anim/title.mp4', 'LAMPLIGHT SCRIPTURE', 'The First Christmas',
          'The Nativity story from Luke and Matthew', 'Bible stories for sleep  ·  AI-generated narration', I(1, 0))))
for n in range(2, 13):
    ev.append(dict(t=starts[n], secs=7.0, path=anim.chapter_card(f'{B}/anim/ch{n:02d}.mp4', n, titles[n], I(n, 0))))
ev.append(dict(t=at(1, 'Notice the first words the angel says'), secs=12.0, path=anim.quote_card(B + '/anim/q1.mp4',
          ['“Don’t be afraid, Zacharias,', 'because your request has been heard.”'], 'Luke 1:13 (World English Bible)', I(1, 2))))
ev.append(dict(t=at(7, 'Let us imagine the road, as one likely path'), secs=22.0, path=maps.m1(B + '/anim/map1.mp4', secs=22.0)))
ev.append(dict(t=at(9, 'Those words have been sung'), secs=12.0, path=anim.quote_card(B + '/anim/q9.mp4',
          ['“Glory to God in the highest,', 'on earth peace, good will toward men.”'], 'Luke 2:14 (World English Bible)', I(9, 3))))
ev.append(dict(t=at(9, 'While everyone else is talking'), secs=12.0, path=anim.quote_card(B + '/anim/q9b.mp4',
          ['“But Mary kept all these sayings,', 'pondering them in her heart.”'], 'Luke 2:19 (World English Bible)', I(9, 5))))
ev.append(dict(t=at(10, 'It is the song of a man whose long watch'), secs=12.0, path=anim.quote_card(B + '/anim/q10.mp4',
          ['“Now you are releasing your servant, Master,', 'according to your word, in peace.”'], 'Luke 2:29 (World English Bible)', I(10, 3))))
ev.append(dict(t=at(12, 'Egypt was beyond Herod'), secs=20.0, path=maps.m2(B + '/anim/map2.mp4', secs=20.0)))
ev.sort(key=lambda e: e['t'])
for a, b in zip(ev, ev[1:]):
    assert a['t'] + a['secs'] < b['t'], (a, b)
json.dump(ev, open(B + '/anim_events.json', 'w'), indent=1)
print(len(ev), 'animations', round(sum(e['secs'] for e in ev)), 's')
