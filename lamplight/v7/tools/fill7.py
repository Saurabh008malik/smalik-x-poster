import re, sys, glob, pathlib
sys.path.insert(0,'/home/claude/lamp7/tools')
from web import passage
def clean(t):
    t=re.sub(r"([.,!?;:])’", r"\1", t)
    t=t.replace('“','').replace('”','').replace('‘',"").replace('’',"'").replace('"','')
    t=t.replace('Lord GOD','Lord God').replace('LORD','Lord')
    t=t.replace(' (',', ').replace(')',',').replace(',,',',')
    t=re.sub(r'\s+',' ',t).strip()
    return t[0].upper()+t[1:]
tot=0; scr=0
files=sys.argv[1:] or sorted(glob.glob('/home/claude/lamp7/draft/ch*.txt'))
for f in files:
    t=open(f).read()
    def rep(m):
        global scr
        s=clean(passage(m.group(1),m.group(2))); scr+=len(s.split()); return s
    t=re.sub(r'\{\{(\w+) ([\d:\-]+)\}\}', rep, t)
    t=t.replace('’',"'").replace('‘',"'")
    out=pathlib.Path('/home/claude/lamp7/script')/pathlib.Path(f).name
    out.write_text(t); n=len(re.sub(r'##','',t).split()); tot+=n; print(out.name,n)
print('total',tot,'scripture',scr)
