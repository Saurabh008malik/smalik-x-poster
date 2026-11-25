import json, sys
sys.path.insert(0,'/home/claude/lamp6/tools')
from crop import crop as autocrop
from PIL import Image
MAN={'bethl_104':(.115,.2,.885,.8),'boaz_048':(.07,.09,.93,.91),'haman_074':(.035,.07,.965,.93),
     'haman_077':(.02,.04,.98,.96),'haman_082':(0,0,1,1),'bethl_110':(0,.25,1,1)}
GOOD="""bethl_104 bethl_105 bethl_106 bethl_109 bethl_110 boaz_036 boaz_037 boaz_038 boaz_039 boaz_040 boaz_041 boaz_042 boaz_043 boaz_044 boaz_045 boaz_047 boaz_048 boaz_049 boaz_050
doreest_005 doreest_006 doreest_007 doreest_008 doreruth_001 doreruth_002 doreruth_003 doreruth_004 esther_057 esther_058 esther_060 esther_061 esther_062 esther_064 esther_065 esther_066 esther_067 esther_068 esther_069 esther_070
feast_086 feast_087 haman_074 haman_075 haman_076 haman_077 haman_081 haman_082 harvest_092 harvest_093 harvest_094 harvest_095 harvest_096 harvest_097 harvest_098 moab_103
naomi_021 naomi_022 naomi_023 naomi_024 naomi_025 naomi_026 naomi_027 naomi_028 naomi_031 naomi_032 naomi_033 night_111 schruth_088
tisest_014 tisest_015 tisest_016 tisest_017 tisest_018 tisest_019 tisest_020 tisruth_009 tisruth_010 tisruth_011 tisruth_012 tisruth_013 toilet_072""".split()
s={i['file']:i for i in json.load(open('img/sources.json'))}; out=[]
for st in GOOD:
    f=st+'.jpg'; src='img/'+f; dst='img2/'+f
    if st in MAN:
        im=Image.open(src).convert('RGB'); w,h=im.size; a,b,c,d=MAN[st]
        im=im.crop((int(a*w),int(b*h),int(c*w),int(d*h))); im.save(dst,quality=92); sz=im.size
    elif st.startswith('tis'):
        sz=autocrop(src,dst,'tissot_'+f)
    else:
        sz=autocrop(src,dst,f)
    e=dict(s[f]); e['cropped']=sz; out.append(e)
json.dump(out,open('img2/sources.json','w'),indent=0,ensure_ascii=False)
print(len(out))
