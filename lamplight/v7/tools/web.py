import re, glob
def load(path):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'\\f .*?\\f\*', '', t, flags=re.S); t = re.sub(r'\\x .*?\\x\*', '', t, flags=re.S)
    t = re.sub(r'\\\+?w ([^|\\]*)\|[^\\]*\\\+?w\*', r'\1', t)
    vs = {}; c = 0; cur = None
    for line in t.splitlines():
        m = re.match(r'\\c (\d+)', line)
        if m: c = int(m.group(1)); cur = None; continue
        m = re.match(r'\\v (\d+) (.*)', line)
        if m: cur = (c, int(m.group(1))); vs[cur] = m.group(2); continue
        if cur and not re.match(r'\\(s|ms|mr|r|d)\d?\b', line):
            s = re.sub(r'^\\[a-z]+\d?\s*', '', line)
            if s.strip(): vs[cur] += ' ' + s
    for k, v in vs.items():
        v = re.sub(r'\\[a-z]+\d?\*?', '', v); v = re.sub(r'\s+', ' ', v).strip()
        v = v.replace('the Lord Yahweh', 'the Lord God').replace('Lord Yahweh', 'Lord God')
        v = v.replace('Yahweh’s', 'the Lord’s').replace('Yahweh', 'the Lord')
        vs[k] = v
    return vs
BOOK = {}
def passage(code, ref):
    if code not in BOOK: BOOK[code] = load(glob.glob(f'/home/claude/w/web/*-{code}engwebp.usfm')[0])
    VS = BOOK[code]
    a, b = ref.split('-') if '-' in ref else (ref, ref)
    c1, v1 = map(int, a.split(':'))
    c2, v2 = map(int, b.split(':')) if ':' in b else (c1, int(b))
    out = ' '.join(v for (c, n), v in sorted(VS.items()) if (c1, v1) <= (c, n) <= (c2, v2))
    assert out, (code, ref); return out
if __name__ == '__main__':
    import sys
    for r in sys.argv[2:]: print(r, '|', passage(sys.argv[1], r)); print()
