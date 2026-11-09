"""Hand a finished video to the GitHub auto-uploader.
usage: python3 handover.py <video.mp4> <thumb.jpg> <metadata.txt> <id> <schedule_at_utc_iso>
Splits the video in 90 MB parts onto a temporary branch feed-<id>, adds the item to sleepy/queue.json on main."""
import sys, os, re, json, hashlib, subprocess, shutil, datetime as dt
video, thumb, meta, vid_id, sched = sys.argv[1:6]
REPO = '/home/claude/poster-repo'
def sh(*a, **k): return subprocess.run(a, check=True, cwd=REPO, **k)
txt = open(meta).read()
def sec(name, nxt):
    m = re.search(rf'^{name}\n(.*?)(?=^{nxt}\b)', txt, re.S | re.M); return m.group(1).strip()
title = sec('TITLE', 'DESCRIPTION')
desc = sec('DESCRIPTION', 'TAGS')
desc = desc.split('TAGS (comma separated)')[0].strip()
tags = [t.strip() for t in re.search(r'^TAGS \(comma separated\)\n(.*?)\n\n', txt, re.S | re.M).group(1).split(',')]
comment = re.search(r'^FIRST COMMENT[^\n]*\n(.*?)\n\n', txt, re.S | re.M).group(1).strip()
assert len(title) <= 100 and '<' not in desc and '>' not in desc and len(desc) < 5000
h = hashlib.sha256()
with open(video, 'rb') as f:
    for b in iter(lambda: f.read(8 << 20), b''): h.update(b)
br = f'feed-{vid_id}'
sh('git', 'checkout', '-q', 'main'); sh('git', 'pull', '-q', '--rebase', 'origin', 'main')
sh('git', 'checkout', '-q', '--orphan', br); sh('git', 'rm', '-rf', '-q', '.')
n = 0
with open(video, 'rb') as f:
    while True:
        b = f.read(90_000_000)
        if not b: break
        open(f'{REPO}/video.mp4.part{n:03d}', 'wb').write(b); n += 1
shutil.copy(thumb, f'{REPO}/thumbnail.jpg')
sh('git', 'add', '-A')
sh('git', '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', f'video parts for {vid_id} (temporary)\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_013Q1eVK7pL63D4YTJpcgzzr')
sh('git', 'push', '-q', 'origin', br)
sh('git', 'checkout', '-q', '-f', 'main'); sh('git', 'branch', '-D', '-q', br)
q = json.load(open(f'{REPO}/sleepy/queue.json'))
q = [i for i in q if i['id'] != vid_id]
q.append({'id': vid_id, 'kind': 'long', 'publish_after': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
          'schedule_at': sched, 'parts_branch': br, 'sha256': h.hexdigest(), 'video': 'video.mp4', 'thumbnail': 'thumbnail.jpg',
          'title': title, 'description': desc, 'tags': tags, 'comment': comment, 'category': '27', 'done': False})
json.dump(q, open(f'{REPO}/sleepy/queue.json', 'w'), indent=2, ensure_ascii=False)
sh('git', 'add', 'sleepy/queue.json')
sh('git', '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', f'Queue {vid_id}: upload now, public at {sched}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_013Q1eVK7pL63D4YTJpcgzzr')
sh('git', 'push', '-q', 'origin', 'main')
print('handed over', n, 'parts; sha', h.hexdigest()[:12])
