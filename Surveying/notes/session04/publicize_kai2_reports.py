"""検証の結果・ハッシュは保持し、公開レポートの個人環境パスを一般化する。"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
PROFILE=ROOT.parents[4]
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    if isinstance(v,list):return [clean(x) for x in v]
    if isinstance(v,str):
        return v.replace(str(ROOT),'Surveying').replace(ROOT.as_posix(),'Surveying').replace(str(PROFILE),'<user-profile>').replace(PROFILE.as_posix(),'<user-profile>')
    return v
for p in (ROOT/'notes/session04/kai2').glob('final_validation*.json'):
    p.write_text(json.dumps(clean(json.loads(p.read_text(encoding='utf-8'))),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('公開検証レポートの個人環境パスを一般化')
