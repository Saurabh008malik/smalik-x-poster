import json,shutil,os,sys
sys.path.insert(0,'/home/claude/marie')
from autocrop import crop
src={}
for tag,d in (('r1','marie1'),('r2','marie2'),('r3','marie3')):
    for s in json.load(open(f'{d}/sources.json')): src[f"{tag}_{s['file'][:-4]}"]=(d,s)
CROP=('reims_','varennes_','october_028','october_031','necklace_018','clery_','martin_','wedding_','strasbourg_','balloon_','temple_002','portrait2_025','gluck_','bertin_032','amour_017','amour_016','theatre_022','dubarry_038','vlb_049')
C={
1:"r1_portrait_014 r3_amour_016 r1_hameau_073 r3_belved_020 r1_portrait_013 r3_amour_019 r1_portrait_001 r3_bellotto_078 r3_bellotto_079 r1_maria_028 r1_maria_029 r1_vienna_042 r1_maria_033",
2:"r1_schon_040 r1_schon_038 r3_ballet_028 r1_maria_037 r1_maria_030 r1_schon_041 r1_schon_039 r1_maria_033 r3_joseph_043 r1_maria_028 r3_bellotto_078 r1_portrait2_025",
3:"r2_wedding_001 r1_portrait2_025 r3_august_009 r3_bellotto_079 r2_strasbourg_004 r3_louisxv_041 r1_louis_044 r3_chapel_063 r3_chapel_065 r3_chapel_062 r3_opera_068 r3_opera_067 r2_wedding_000 r1_mirrors_058",
4:"r1_mirrors_060 r1_portrait2_025 r1_mirrors_057 r1_versailles_052 r3_dubarry_037 r3_dubarry_038 r3_martin_058 r3_martin_059 r3_martin_060 r1_versailles_053 r3_louisxv_040 r1_mirrors_061 r2_tuileries_033 r1_mirrors_062",
5:"r2_reims_011 r1_louis_044 r2_reims_007 r2_reims_009 r3_bertin_032 r1_portrait_012 r3_opera_067 r3_opera_066 r1_lamballe_100 r1_polignac_105 r1_polignac_103 r1_versailles_053 r1_mirrors_059 r3_louisxv_039",
6:"r3_amour_017 r3_amour_016 r1_trianon_063 r3_amour_018 r3_belved_020 r3_belved_021 r3_theatre_024 r3_theatre_022 r1_hameau_073 r1_hameau_076 r1_hameau_077 r1_hameau_078 r1_portrait_001 r3_amour_019",
7:"r3_joseph_042 r1_versailles_046 r1_fersen_095 r3_joseph_044 r1_dauphin_091 r1_portrait_017 r3_chapel_064 r1_dauphin_094 r1_dauphin_093 r1_children_084 r1_louis_044 r1_mirrors_058 r3_amour_018",
8:"r3_vlb_050 r1_portrait_014 r1_portrait_013 r1_portrait_001 r1_portrait_008 r3_vlb_049 r1_portrait_011 r1_portrait2_027 r1_portrait_000 r1_portrait_003 r1_children_084 r1_dauphin_092 r2_balloon_013 r1_portrait_017",
9:"r2_necklace_020 r2_necklace_016 r2_necklace_018 r2_necklace_019 r3_martin_061 r3_martin_060 r1_portrait_012 r1_portrait_015 r2_necklace_017 r1_louis_044 r1_portrait_000 r3_martin_058 r1_mirrors_062",
10:"r2_estates_021 r1_dauphin_094 r1_dauphin_093 r3_chapel_065 r1_polignac_105 r2_october_031 r2_october_028 r2_october_030 r1_portrait_017 r3_chapel_062 r1_mirrors_057 r3_amour_017 r3_belved_021",
11:"r2_tuileries_034 r2_federation_062 r2_federation_063 r2_stcloud_057 r2_stcloud_059 r3_mirabeau_045 r1_fersen_095 r2_varennes_041 r2_varennes_043 r2_varennes_042 r2_varennes_046 r2_varennes_045 r2_federation_064 r3_temple_003 r1_portrait_015",
12:"r3_temple_003 r2_family_067 r3_temple_004 r2_family_068 r3_clery_071 r3_temple_002 r3_cell_069 r2_family_066 r1_portrait_014 r3_amour_016 r1_hameau_076 r1_portrait_001 r3_belved_020 r1_portrait_013",
}
os.makedirs('img',exist_ok=True); used=set(); ch={}
for n,s in C.items():
    lst=[]
    for k in s.split():
        d,meta=src[k]; fn=k+'.jpg'
        if not os.path.exists('img/'+fn):
            p=f'{d}/img/{meta["file"]}'
            if any(meta['file'].startswith(c) for c in CROP): crop(p,'img/'+fn)
            else: shutil.copy(p,'img/'+fn)
        lst.append(fn); used.add(k)
    ch[str(n)]=lst
json.dump(ch,open('ch_imgs.json','w'),indent=1)
sources=[dict(src[k][1],file=k+'.jpg') for k in sorted(used)]
json.dump(sources,open('img/sources.json','w'),indent=1)
json.dump(sources,open('image_sources.json','w'),indent=1)
print(len(used),'images')
