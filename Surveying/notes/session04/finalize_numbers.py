"""方向法の公表用定義を、架空の生読定値から再計算する。"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
src = json.loads((ROOT / 'numbers.json').read_text(encoding='utf-8-sig'))
rounds = []
for r in src['direction_method']['rounds']:
    base = r['observations'][0]
    targets = []
    for row in r['observations'][1:3]:
        p = (row['L_sec'] - base['L_sec']) % 1296000
        q = (row['R_sec'] - base['R_sec']) % 1296000
        targets.append(dict(target=row['sight'], p_sec=p, q_sec=q,
                            C_sec=p-q, D_sec=p+q, mean_sec=(p+q)/2))
    rounds.append(dict(round=r['round'], targets=targets))
checks=[]
for j,name in enumerate(['B','C']):
    vals=[r['targets'][j] for r in rounds]
    checks.append(dict(target=name,
                       double_angle_range_sec=max(v['D_sec'] for v in vals)-min(v['D_sec'] for v in vals),
                       observation_range_sec=max(v['C_sec'] for v in vals)-min(v['C_sec'] for v in vals),
                       final_angle_sec=sum(v['mean_sec'] for v in vals)/len(vals)))
assert [r['targets'][0]['C_sec'] for r in rounds]==[4,-2]
assert [x['double_angle_range_sec'] for x in checks]==[6,10]
assert [x['observation_range_sec'] for x in checks]==[6,0]
assert [x['final_angle_sec'] for x in checks]==[264311.5,512271.5]
out=dict(definitions=dict(p='正読定から正の零方向を差引き',q='反読定から反の零方向を差引き',
                         C='較差=p-q',D='倍角=p+q',
                         double_angle_range='同一目標の対回間最大D-最小D',
                         observation_range='同一目標の対回間最大C-最小C'),
         rounds=rounds,checks=checks,
         zenith=dict(K_sec=24,i_sec=12,Z_sec=281550,elevation_sec=42450))
(ROOT/'verified_numbers.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
