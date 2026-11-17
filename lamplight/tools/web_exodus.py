import re, sys
def load(path='/home/claude/lamp3/web/03-EXOengwebp.usfm'):
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
        v = re.sub(r'([.!?:;“‘]\s*|^)the Lord', lambda m: m.group(1) + 'The Lord' if m.group(1).strip() in '.!?“‘' and m.group(1).strip() != '' or m.group(1) == '' else m.group(0), v)
        vs[k] = v
    return vs
VS = load()
def passage(ref):
    a, b = ref.split('-') if '-' in ref else (ref, ref)
    c1, v1 = map(int, a.split(':'))
    c2, v2 = map(int, b.split(':')) if ':' in b else (c1, int(b))
    return ' '.join(v for (c, n), v in sorted(VS.items()) if (c1, v1) <= (c, n) <= (c2, v2))
if __name__ == '__main__':
    for r in sys.argv[1:]: print(r, '|', passage(r)); print()
