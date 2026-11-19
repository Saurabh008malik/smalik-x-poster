import re, sys, glob, pathlib
sys.path.insert(0,'/home/claude/lamplight/tools')
import importlib.util
spec=importlib.util.spec_from_file_location('w','/home/claude/lamplight/tools/web_exodus.py')
src=open('/home/claude/lamplight/tools/web_exodus.py').read().replace("VS = load()","VS = {}")
ns={}; exec(src, ns)
BOOK={}
for code in ['1SA','2SA','1KI','PSA']:
    f=glob.glob(f'/home/claude/lamp4/web/*-{code}engwebp.usfm')[0]; BOOK[code]=ns['load'](f)
def passage(code, ref):
    VS=BOOK[code]
    a,b=ref.split('-') if '-' in ref else (ref,ref)
    c1,v1=map(int,a.split(':'))
    c2,v2=map(int,b.split(':')) if ':' in b else (c1,int(b))
    out=' '.join(v for (c,n),v in sorted(VS.items()) if (c1,v1)<=(c,n)<=(c2,v2))
    assert out, (code,ref)
    return out
def clean(t):
    t=t.replace('“','"').replace('”','"').replace('‘',"'").replace('’',"'")
    t=t.replace('"','').replace('Lord GOD','Lord God').replace('LORD','Lord').replace('GOD','God')
    t=re.sub(r'\s+',' ',t).strip()
    t=re.sub(r'^and he said: ','',t)
    return t[0].upper()+t[1:]
tot=0
for f in sorted(glob.glob('/home/claude/lamp4/draft/ch*.txt')):
    t=open(f).read()
    t=re.sub(r'\{\{(\w+) ([\d:\-]+)\}\}', lambda m: clean(passage(m.group(1),m.group(2))), t)
    out=pathlib.Path('/home/claude/lamp4/script')/pathlib.Path(f).name
    out.write_text(t); n=len(re.sub(r'##','',t).split()); tot+=n; print(out.name,n)
print('total',tot)
