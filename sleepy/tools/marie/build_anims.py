"""Render the calm animated segments and write anim_events.json (needs timeline.json and ch_imgs.json)."""
import json, re, sys
sys.path.insert(0, '/home/claude/marie')
import anim, maps
B = '/home/claude/marie'
tl = json.load(open(B + '/timeline.json')); durs = {int(k): v for k, v in tl['durs'].items()}; LEAD = tl['lead']
ch = {int(k): v for k, v in json.load(open(B + '/ch_imgs.json')).items()}
starts = {}; c = LEAD
for n in range(1, 13): starts[n] = c; c += durs[n]
titles = {n: open(f'{B}/script/ch{n:02d}.txt').readline().split(':', 1)[1].strip() for n in range(1, 13)}

def at(n, needle):
    """approximate time (s from video start) when the paragraph containing needle begins, by weighted length."""
    txt = open(f'{B}/script/ch{n:02d}.txt').read()
    paras = [p for p in txt.split('\n\n') if p.strip()]
    wts = [len(p) + 30 * len(re.findall(r'[.!?:]', p)) + 40 for p in paras]   # pauses ~ sentence/para gaps
    idx = next(i for i, p in enumerate(paras) if needle in p)
    return starts[n] + durs[n] * sum(wts[:idx]) / sum(wts)

ev = []
ev.append(dict(t=0.0, secs=24.0, path=anim.title_card(B + '/anim/title.mp4', 'THE SLEEPY BIOGRAPHER', 'Marie Antoinette',
          'The Last Queen of Versailles', 'A calm biography for sleep  ·  AI-generated narration', B + '/img/' + ch[1][0])))
for n in range(2, 13):
    ev.append(dict(t=starts[n], secs=7.0, path=anim.chapter_card(f'{B}/anim/ch{n:02d}.mp4', n, titles[n], B + '/img/' + ch[n][0])))
ev.append(dict(t=at(1, 'Now here is the strange thing') + 6, secs=12.0, path=anim.quote_card(B + '/anim/q1.mp4',
          ['“Let them eat cake.”'], 'A line with no good evidence that she ever said it', B + '/img/' + ch[1][1])))
ev.append(dict(t=at(3, 'The journey took more than two weeks') + 4, secs=22.0, path=maps.m1(B + '/anim/map1.mp4', secs=22.0)))
ev.append(dict(t=at(4, 'In one of them, written in the summer'), secs=12.0, path=anim.quote_card(B + '/anim/q4.mp4',
          ['“I put on my rouge and wash my hands', 'in front of the whole world.”'], 'Marie Antoinette to her mother, 1770 (translated)', B + '/img/' + ch[4][1])))
ev.append(dict(t=at(11, 'On the night of the twentieth of June'), secs=20.0, path=maps.m2(B + '/anim/map2.mp4', secs=20.0)))
ev.append(dict(t=at(12, 'she wrote a last letter') + 8, secs=12.0, path=anim.quote_card(B + '/anim/q12.mp4',
          ['“I am calm, as one is when', 'one’s conscience has nothing to reproach.”'], 'Her last letter, 16 October 1793 (translated)', B + '/img/' + ch[12][1])))
ev.sort(key=lambda e: e['t'])
for a, b in zip(ev, ev[1:]):
    assert a['t'] + a['secs'] < b['t'], (a, b)
json.dump(ev, open(B + '/anim_events.json', 'w'), indent=1)
print(len(ev), 'animations', round(sum(e['secs'] for e in ev)), 's')
