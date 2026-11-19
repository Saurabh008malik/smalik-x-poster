import json, numpy as np
from PIL import Image
def runs(mask, gap):
    idx=np.where(mask)[0]
    if len(idx)==0: return None
    best=None; s=idx[0]; p=idx[0]
    for i in list(idx[1:])+[10**9]:
        if i-p>gap:
            if best is None or (p-s)>(best[1]-best[0]): best=(s,p)
            s=i
        p=i
    return best
def crop(src,dst,f):
    im=Image.open(src).convert('RGB'); a=np.asarray(im.convert('L')).astype(np.float32)
    h,w=a.shape
    border=np.concatenate([a[:max(3,h//50)].ravel(),a[-max(3,h//50):].ravel(),a[:,:max(3,w//50)].ravel(),a[:,-max(3,w//50):].ravel()])
    paper=np.percentile(a,90)
    if f.split('_')[0] in ('jerusalem','bethlehem','engedi'):
        im=im.crop((int(w*.035),int(h*.035),int(w*.965),int(h*.965))); im.save(dst,quality=92); return im.size
    if f.startswith('tissot') or f.startswith('absalom_185'):
        dk=a<90
        rr=np.where(dk.mean(1)>0.3)[0]; cc=np.where(dk.mean(0)>0.3)[0]
        rr=rr[(rr>h*0.02)&(rr<h*0.98)]; cc=cc[(cc>w*0.02)&(cc<w*0.98)]
        if len(rr)>=2 and len(cc)>=2 and rr[-1]-rr[0]>h*0.4 and cc[-1]-cc[0]>w*0.4:
            t,b,l,r_=rr[0],rr[-1],cc[0],cc[-1]; ih,iw=b-t,r_-l
            im=im.crop((l+int(iw*.03),t+int(ih*.03),r_-int(iw*.03),b-int(ih*.03)))
        im.save(dst,quality=92); return im.size
    if np.median(border)>150:
        dark=a<paper-55
        r=runs(dark.mean(1)>0.06, max(4,h//60)); c=runs(dark.mean(0)>0.06, max(4,w//60))
        if r and c and (r[1]-r[0])>h*0.3 and (c[1]-c[0])>w*0.3:
            t,b,l,rr=r[0],r[1],c[0],c[1]
            ins=0.045 if f.startswith('tissot') else 0.012
            ih,iw=b-t,rr-l; t+=int(ih*ins); b-=int(ih*ins); l+=int(iw*ins); rr-=int(iw*ins)
            im=im.crop((l,t,rr,b))
    im.save(dst,quality=92); return im.size
if __name__=='__main__':
    s={i['file']:i for i in json.load(open('a/sources.json'))}
    out=[]
    for f in json.load(open('good.json')):
        e=dict(s[f]); e['cropped']=crop('a/img/'+f,'img2/'+f,f); out.append(e)
    json.dump(out,open('img2/sources.json','w'),indent=0,ensure_ascii=False)
