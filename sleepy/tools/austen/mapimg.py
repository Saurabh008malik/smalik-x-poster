import json,shutil,os
src={}
for tag,d in (('r1','raw'),('r2','raw2'),('r3','raw3')):
    for s in json.load(open(f'{d}/sources.json')): src[f"{tag}_{s['file'][:-4]}"]=(d,s)
C={
1:"r1_cassandra_075 r3_snow_097 r1_church_110 r3_gainsborough_089 r3_snow_101 r3_gainsborough_087 r1_austen_020 r3_snow_098 r3_constable_077 r3_reading2_121 r3_gainsborough_092 r1_godmersham_069",
2:"r3_gainsborough_090 r3_constable_074 r3_gainsborough_091 r3_constable_081 r3_reading_053 r3_reading_056 r3_reading_057 r3_reading_052 r3_constable_075 r3_gainsborough_093 r3_constable_082 r1_brock_048",
3:"r3_eliza_125 r1_mansfield_096 r3_eliza_126 r1_mansfield_098 r1_austen_025 r1_mansfield_097 r1_austen_005 r3_reading2_121 r1_mansfield_100 r1_austen_006 r1_mansfield_102 r1_cassandra_074",
4:"r3_rowlandson_017 r3_fashion_010 r1_thomson_032 r1_brock_042 r1_thomson_033 r1_austen_003 r1_brock_043 r3_fashion_008 r1_thomson_038 r1_brock_046 r2_ships_016 r1_austen_004 r1_brock_047",
5:"r1_thomson_030 r1_thomson_031 r1_thomson_034 r3_lane_106 r1_thomson_035 r1_sense_086 r1_thomson_036 r3_constable_078 r1_sense_088 r1_austen_012 r1_thomson_037 r3_lane_108",
6:"r3_pump_022 r3_rowlandson_018 r3_pump_024 r3_rowlandson_012 r3_fashion_005 r3_rowlandson_014 r3_rowlandson_016 r1_persuasion_090 r3_rowlandson_021 r3_lyme_030 r3_fashion_003 r3_lyme_031",
7:"r3_constable_084 r3_lane_110 r3_constable_085 r1_brock_050 r3_constable_076 r1_austen_025 r1_brock_051 r3_snow_100 r3_rowlandson_020 r3_constable_072 r1_cassandra_073 r3_constable_086",
8:"r2_stoneleigh_003 r2_stoneleigh_004 r2_ships_011 r2_ships_014 r3_netley_059 r2_ships_015 r3_netley_063 r1_godmersham_065 r2_ships_018 r3_netley_062 r1_godmersham_070 r2_ships_017 r1_cassandra_073 r2_constable_001",
9:"r3_chawtonhouse_044 r1_cassandra_077 r3_chawtonhouse_047 r1_church_111 r3_gainsborough_094 r1_sense_086 r3_chawtonhouse_045 r1_brock_052 r3_fashion_001 r1_brock_053 r3_constable_073 r1_brock_054",
10:"r1_thomson_039 r1_brock_056 r1_thomson_040 r1_cassandra_078 r1_brock_057 r1_mansfield_099 r1_thomson_041 r1_godmersham_066 r1_mansfield_101 r1_brock_058 r3_fashion_009 r1_mansfield_103 r1_brock_059",
11:"r3_emmat_111 r1_emma_085 r1_regent_084 r3_regent_129 r1_regent_080 r1_regent_083 r3_regent_131 r3_scott_135 r1_persuasion_089 r2_ships_012 r1_persuasion_094 r1_persuasion_091 r1_persuasion_095 r1_persuasion_092",
12:"r3_winchester_036 r3_college_043 r3_winchester_039 r1_austen_024 r3_winchester_041 r1_winchester_063 r3_winchester_035 r1_winchester_064 r1_austen_002 r3_jeal_128 r3_constable_076 r1_cassandra_076 r3_reading2_121",
}
os.makedirs('img',exist_ok=True); used=set(); ch={}
for n,s in C.items():
    lst=[]
    for k in s.split():
        d,meta=src[k]; fn=k+'.jpg'
        if not os.path.exists('img/'+fn): shutil.copy(f'{d}/img/{meta["file"]}','img/'+fn)
        lst.append(fn); used.add(k)
    ch[str(n)]=lst
json.dump(ch,open('ch_imgs.json','w'),indent=1)
sources=[dict(src[k][1],file=k+'.jpg') for k in sorted(used)]
json.dump(sources,open('img/sources.json','w'),indent=1)
json.dump(sources,open('image_sources.json','w'),indent=1)
print(len(used),'images')
