import json,shutil,os,sys
sys.path.insert(0,'/home/claude/dickens')
from autocrop import crop
src={}
for tag,d in (('r1','dickens1'),('r2','dickens2'),('r3','dickens3')):
    for s in json.load(open(f'{d}/sources.json')): src[f"{tag}_{s['file'][:-4]}"]=(d,s)
CROP=('dore_','copper_','manch_','carol_')
C={
1:"r1_portrait_001 r2_birth_019 r2_birth_017 r3_roch_004 r2_birth_016 r3_chat_012 r2_birth_018 r1_leech_031 r2_london_037 r2_dore_011 r1_portrait_013 r3_medway_019",
2:"r3_roch_000 r3_roch_001 r3_roch_002 r3_medway_016 r3_roch_003 r3_roch_005 r3_medway_017 r2_gadshill_028 r3_roch_004 r3_coach_020 r3_coach_025 r2_dore_000 r2_london_037",
3:"r2_dore_002 r2_marshalsea_025 r2_dore_003 r2_marshalsea_026 r2_dore_005 r3_dorrit_078 r2_dore_012 r2_marshalsea_024 r2_dore_006 r1_copper_061 r2_dore_015 r2_marshalsea_023 r2_dore_004",
4:"r1_portrait_004 r1_copper_063 r3_whall_028 r1_copper_064 r2_dore_011 r1_portrait_009 r1_copper_065 r3_fleet_038 r1_copper_069 r2_dore_000 r3_rcath_008 r1_copper_067 r2_dore_009",
5:"r3_commons_030 r3_commons_031 r3_coach_021 r3_coach_020 r3_whall_029 r3_whall_027 r3_fleet_038 r1_photo_020 r1_portrait_012 r2_catherine_033 r3_coach_025 r2_dore_009 r1_portrait_004",
6:"r3_seymour_089 r1_barnard_073 r3_seymour_090 r1_pickwick_047 r3_seymour_091 r1_pickwick_049 r1_pickwick_050 r1_oliver_051 r1_oliver_053 r1_oliver_055 r1_oliver_058 r1_pickwick_048 r1_portrait_001 r2_dream_044",
7:"r3_nickleby_041 r3_nickleby_042 r3_nickleby_043 r1_portrait_013 r3_nell_044 r3_nell_046 r3_nell_045 r3_nell_047 r1_oliver_057 r1_photo_020 r2_dream_045 r3_seymour_093 r1_oliver_060",
8:"r3_ship_059 r3_ship_062 r3_ship_060 r3_boston_066 r1_portrait_000 r3_boston_065 r3_ship_061 r3_coach_021 r2_america_063 r3_niagara_053 r3_niagara_056 r3_niagara_057 r3_niagara_058 r3_niagara_054",
9:"r2_ragged_067 r2_ragged_068 r2_ragged_066 r2_ragged_069 r2_dore_003 r2_dore_004 r1_barnard_074 r1_leech_028 r1_leech_025 r1_leech_031 r1_carol_039 r1_leech_027 r1_leech_030 r1_carol_041 r1_carol_044 r1_carol_045",
10:"r1_leech_021 r1_leech_026 r1_leech_031 r2_xmas_055 r1_leech_025 r2_xmas_059 r2_xmas_057 r1_barnard_076 r2_xmas_054 r1_barnard_075 r1_portrait_013 r1_leech_029 r1_carol_035",
11:"r3_genova_072 r3_genova_071 r2_reading_041 r1_copper_068 r1_copper_069 r1_copper_070 r1_copper_062 r1_portrait_005 r3_dorrit_079 r3_dorrit_081 r1_portrait_002 r2_catherine_032 r3_dorrit_082 r1_photo_019",
12:"r2_gadshill_028 r2_gadshill_029 r2_gadshill_031 r1_photo_017 r2_reading_038 r3_two_073 r3_crash_083 r2_reading_040 r1_portrait_011 r1_photo_015 r2_reading_042 r2_dream_045 r2_abbey_050 r1_photo_018 r1_leech_031",
}
os.makedirs('img',exist_ok=True); used=set(); ch={}
for n,s in C.items():
    lst=[]
    for k in s.split():
        d,meta=src[k]; fn=k+'.jpg'
        if not os.path.exists('img/'+fn):
            p=f'{d}/img/{meta["file"]}'
            if any(meta['file'].startswith(c) for c in CROP):
                crop(p,'img/'+fn)
            else: shutil.copy(p,'img/'+fn)
        lst.append(fn); used.add(k)
    ch[str(n)]=lst
json.dump(ch,open('ch_imgs.json','w'),indent=1)
sources=[dict(src[k][1],file=k+'.jpg') for k in sorted(used)]
json.dump(sources,open('img/sources.json','w'),indent=1)
json.dump(sources,open('image_sources.json','w'),indent=1)
print(len(used),'images')
