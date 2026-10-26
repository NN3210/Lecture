"""原寸レビューで確認した求心図と偏心図の最終修正。"""
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'materials/slides/第04回_角測量/diagram_helpers.mjs'
s=p.read_text(encoding='utf-8-sig')
a='line(s,r-17,y+58,r+12,g-8,C.warn,5);circle(s,l,y+h*.38,Math.min(34,h*.13),C.pale,3);circle(s,r,y+h*.38,Math.min(34,h*.13),C.pale,3);'
b='line(s,isLevel?r-17:r+45,y+58,isLevel?r+12:r+45,g-8,C.warn,5);if(!isLevel)line(s,r,y+58,r,g-8,C.grid,2,"dash");circle(s,l,y+h*.38,Math.min(34,h*.13),C.pale,3);circle(s,isLevel?r:r+45,y+h*.38,Math.min(34,h*.13),C.pale,3);'
s=s.replace(a,b).replace('text(s,"器械中心",r-61,y+h*.38-13','text(s,"器械中心",(isLevel?r:r+45)-61,y+h*.38-13')
s=s.replace('text(s,"OB=100 m",O.x+len*.42,O.y-37,106,26','text(s,"OB=100 m",B.x+55,O.y-22,106,26')
p.write_text(s,encoding='utf-8')
print('Final centering and eccentric labels fixed')
