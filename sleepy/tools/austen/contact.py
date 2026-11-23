import sys,glob,os
from PIL import Image,ImageDraw
files=sorted(glob.glob(sys.argv[1]+'/*.jpg')); out=sys.argv[2]; per=48
for p in range(0,len(files),per):
    chunk=files[p:p+per]; W,H=8,6; tw,th=240,180
    sheet=Image.new('RGB',(W*tw,H*th),'black'); d=ImageDraw.Draw(sheet)
    for i,f in enumerate(chunk):
        im=Image.open(f).convert('RGB'); im.thumbnail((tw-4,th-18))
        x,y=(i%W)*tw,(i//W)*th; sheet.paste(im,(x+2,y+2)); d.text((x+3,y+th-15),os.path.basename(f)[:-4],fill='yellow')
    sheet.save(f'{out}_{p//per}.jpg',quality=80)
