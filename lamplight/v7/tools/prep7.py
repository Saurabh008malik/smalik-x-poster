import json,shutil,os,sys
sys.path.insert(0,'/home/claude/lamp7/tools')
from autocrop import crop
from PIL import Image
B='/home/claude/lamp7'
src={}
for tag,d in (('a','n1'),('b','n2')):
    for s in json.load(open(f'{B}/{d}/sources.json')): src[f"{tag}_{s['file'][:-4]}"]=(d,s)
CROP=('a_rb_','a_rn_','b_bn_026','b_bn_027','b_bn_028','b_bb_','b_dj_','b_hw_','b_kp_','b_sp_','b_hg_','b_t12_','a_tsi_','a_sb_139','b_jb_')
MANUAL={'b_zw_013':(0.055,0.11,0.945,0.89)}
C={
1:"a_as_016 a_sb_139 a_zt_116 a_pt_070 a_rb_122 a_aa_034 a_am_052 a_ng_030 a_fe_073 a_pt_071 a_rn_127 a_gd_119",
2:"a_zt_116 a_pt_071 b_dj_036 a_vi_045 b_bb_022 a_rb_121 a_vi_046 a_pt_062 a_sb_139 b_dj_038",
3:"b_t2_000 b_bn_026 a_aa_034 a_al_039 b_bn_027 a_aa_033 a_rn_127 b_ta_004 a_aa_035 b_bn_028 a_rn_128 b_bn_029 b_hw_019",
4:"a_vi_041 a_vi_044 a_vi_045 a_vi_043 a_vi_040 a_vi_046 b_dj_037 b_bj2_032 a_rb_121 b_bj2_031 a_vi_042 b_dj_036",
5:"b_zw_013 a_vi_045 b_bj_008 b_dj_036 a_pt_070 a_rb_121 b_bb_022 a_vi_046 a_sb_139 b_bj2_033 a_zt_116",
6:"a_dj_096 a_dj_094 a_dj_095 a_dj_097 a_dj_098 a_dj_099 b_hw_019 b_bn_030 a_rn_127 b_bn_026 b_t2_000 a_rn_128",
7:"a_cb_008 a_cb_009 b_bj2_032 b_dj_037 b_bj2_033 b_jb_043 b_hg_049 b_dj_038 a_rb_122 b_bb_020 a_cb_010 a_rb_121 b_bb_025",
8:"a_ng_030 a_gd_119 a_as_016 a_ng_027 a_gd_118 a_as_024 a_as_020 a_as_015 a_rb_123 a_as_022 a_ng_029 b_bb_024 a_as_023",
9:"b_ta_005 a_ans_112 a_ans_111 a_ans_109 b_sp_034 a_as_018 a_as_019 a_ans_108 a_as_021 a_ans_114 a_as_017 a_ans_110 b_sp_035 a_as_022",
10:"a_pt_069 a_pt_071 a_pt_063 b_t12_003 a_pt_068 a_pt_070 a_pt_067 a_pt_062 a_pt_065 a_pt_064 a_rb_122",
11:"a_tm_002 a_sb_139 a_am_054 a_am_057 a_am_053 b_kp_051 a_sb_137 a_am_055 a_am_052 a_am_061 a_sb_136 a_am_059 a_sb_138 b_dj_038",
12:"a_fe_073 a_fe_083 a_fe_076 a_fe_081 a_fe_084 a_rf_086 a_fe_072 a_fe_075 a_fe_079 b_bn_026 b_hw_019 a_cd_101 a_cd_103 a_cd_107 a_tt_004 a_cd_106 a_cd_100 a_as_016 a_sb_139 a_ng_030",
}
os.makedirs(B+'/img',exist_ok=True); used=set(); ch={}
for n,s in C.items():
    lst=[]
    for k in s.split():
        d,meta=src[k]; fn=k+'.jpg'; p=f'{B}/{d}/img/{meta["file"]}'
        if not os.path.exists(B+'/img/'+fn):
            if k in MANUAL:
                im=Image.open(p).convert('RGB'); a,b_,c,e=MANUAL[k]; im.crop((int(a*im.width),int(b_*im.height),int(c*im.width),int(e*im.height))).save(B+'/img/'+fn,quality=92)
            elif any(k.startswith(c) for c in CROP): crop(p,B+'/img/'+fn)
            else: Image.open(p).convert('RGB').save(B+'/img/'+fn,quality=92)
        lst.append(fn); used.add(k)
    ch[str(n)]=lst
json.dump(ch,open(B+'/ch_imgs.json','w'),indent=1)
sources=[dict(src[k][1],file=k+'.jpg') for k in sorted(used)]
json.dump(sources,open(B+'/img/sources.json','w'),indent=1)
json.dump(sources,open(B+'/sources.json','w'),indent=1)
print(len(used),'images')
