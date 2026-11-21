import re, sys, glob, pathlib
sys.path.insert(0,'/home/claude/lamp5/tools')
from web import passage
def clean(t):
    t=re.sub(r"([.,!?;:])’", r"\1", t)
    t=t.replace('“','').replace('”','').replace('‘',"").replace('’',"'").replace('"','')
    t=t.replace("'MENE","MENE").replace("UPHARSIN.'","UPHARSIN.")
    t=t.replace('Lord GOD','Lord God').replace('LORD','Lord')
    t=re.sub(r'\s+',' ',t).strip()
    return t[0].upper()+t[1:]
tot=0
for f in sorted(glob.glob('/home/claude/lamp5/draft/ch*.txt')):
    t=open(f).read()
    t=re.sub(r'\{\{(\w+) ([\d:\-]+)\}\}', lambda m: clean(passage(m.group(1),m.group(2))), t)
    t=t.replace('’',"'").replace('‘',"'")
    out=pathlib.Path('/home/claude/lamp5/script')/pathlib.Path(f).name
    out.write_text(t); n=len(re.sub(r'##','',t).split()); tot+=n; print(out.name,n)
print('total',tot)
