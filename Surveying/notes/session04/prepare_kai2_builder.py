from pathlib import Path
root=Path(__file__).resolve().parents[2]
folder=root/'materials/slides/第04回_角測量'
base=(folder/'diagram_helpers.mjs').read_text(encoding='utf-8')
base=base.replace('O.x+10,O.y-r*.43','O.x+65,O.y-r*.65')
base=base.replace('O.x-35,O.y-r*.72','O.x+r*.5,O.y-r*.5')
base=base.replace('x+w*.58,y+h*.46,w*.38','x+w*.58,y+h*.64,w*.38')
base=base.replace('O.x+r*.38,O.y-40','O.x+r*.49,O.y-40')
base=base.replace('O.x+r*.14,y+29','O.x+r*.28,y+29')
base=base.replace('"器械中心",l-61,y+h*.38-13','"器械中心",l-155,y+h*.38-13')
base=base.replace('"器械中心",(isLevel?r:r+45)-61,y+h*.38-13','"器械中心",(isLevel?r:r+45)-155,y+h*.38-13')
base=base.replace('O.x+r*.45,O.y,90,27','O.x+r*.65,O.y+3,90,27')
base=base.replace('O.x,O.y,O.x,y+20,C.ink,4','O.x,O.y,O.x,y+42,C.ink,4')
old='P={x:D.x+r*.93,y:D.y-r*.22},Q={x:D.x-r*.93,y:D.y+r*.22}'
new='u={x:.973139,y:-.230205},dx=R.x-D.x,dy=R.y-D.y,proj=dx*u.x+dy*u.y,span=Math.sqrt(proj*proj+r*r-dx*dx-dy*dy),tp=-proj+span,tq=-proj-span,P={x:R.x+tp*u.x,y:R.y+tp*u.y},Q={x:R.x+tq*u.x,y:R.y+tq*u.y}'
assert old in base
base=base.replace(old,new)
(folder/'diagram_kai2_base.mjs').write_text(base,encoding='utf-8')
src=(folder/'build_deck.mjs').read_text(encoding='utf-8')
src=src.replace('./diagram_helpers.mjs','./diagram_kai2.mjs')
src=src.replace('},42,C.ink,true);shape(s,"line"','},[...d.title].length>27?36:42,C.ink,true);shape(s,"line"')
# ラベルを付けた計算は言葉で読める長さで改行し、図の領域と交差させない。
src=src.replace('txt(s,d.result,{left:82,top:548,width:d.diagram?545:1080,height:90},35', 'txt(s,wrapResult(d.result,d.diagram?16:31),{left:82,top:548,width:d.diagram?545:1080,height:90},35')
# 図解ページの長い文章は既存の2行枠へ。箇条書きマークを除き余白でまとめる。
old='txt(s,"●",{left:x,top:y+i*gap,width:24,height:44},Math.max(15,z-11),C.teal,true,"center");'
src=src.replace(old,'')
src=src.replace('const data=await loadData();','function wrapResult(v,n){const a=String(v??"").split("\\n");return a.flatMap(t=>{const r=[];while([...t].length>n){let chars=[...t],j=chars.slice(0,n+1).lastIndexOf("／");if(j<5)j=n;r.push(chars.slice(0,j).join(""));t=chars.slice(j).join("");}r.push(t);return r;}).join("\\n")}\nconst data=await loadData();')
needle='txt(s,String(d.id??i+1).padStart(2,"0")'
src=src.replace(needle,'txt(s,"読む → 据える → 減らす → 点検 → 戻す",{left:66,top:666,width:900,height:28},17,C.muted);'+needle)
(folder/'build_kai2.mjs').write_text(src,encoding='utf-8')
# HTML模式図は入力範囲全体で描画領域に収める。
p=folder/'explanation_回2.html'
s=p.read_text(encoding='utf-8').replace('e方向を8倍に拡大','ずれを拡大した模式図').replace('let dx=190*8*e/s','let dx=Math.min(190*8*e/s,180)').replace('details>summary{display:none}', 'details>summary{display:block}')
p.write_text(s,encoding='utf-8')
print('回2専用生成器を作成')
