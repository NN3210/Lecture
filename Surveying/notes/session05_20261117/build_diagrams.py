#!/usr/bin/env python3
"""第5回改3: 再現可能な講義用SVG/PNG。X北・Y東、角は時計回り。"""
from pathlib import Path
import math, html, subprocess, concurrent.futures
from PIL import Image, ImageDraw, ImageFont
N=Path(__file__).resolve().parent
O=N.parents[1]/'materials/slides/第05回_トラバース測量I/改3/assets'
O.mkdir(parents=True,exist_ok=True)
NAVY='#19354a'; BLUE='#287cb5'; ORANGE='#d77c26'; GREEN='#16866d'; GRAY='#728491'; LIGHT='#dce6eb'; PALE='#f2f6f8'
class SVG:
 def __init__(self,name,title):
  self.name=name; self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="720" viewBox="0 0 900 720" role="img"><title>{html.escape(title)}</title><desc>Xは北、Yは東。方向角Tおよび観測角βは時計回り。</desc><defs>']
  for c in [NAVY,BLUE,ORANGE,GREEN,GRAY]:
   self.s.append(f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>')
  self.s.append('</defs><rect width="900" height="720" fill="white"/><g font-family="Noto Sans CJK JP, sans-serif" fill="'+NAVY+'" stroke-linecap="round" stroke-linejoin="round">')
 def text(self,x,y,t,size=32,c=NAVY,anchor='middle',weight=500):
  self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(str(t))}</text>')
 def line(self,x1,y1,x2,y2,c=BLUE,w=6,arrow=False,dash=False):
  self.s.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"'+(f' marker-end="url(#a{c[1:]})"' if arrow else '')+(' stroke-dasharray="10 10"' if dash else '')+'/>')
 def path(self,pts,c=BLUE,w=6,arrow=False,dash=False,fill='none',close=False):
  d='M '+' L '.join(f'{x:.2f} {y:.2f}' for x,y in pts)+(' Z' if close else '')
  self.s.append(f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}"'+(f' marker-end="url(#a{c[1:]})"' if arrow else '')+(' stroke-dasharray="10 10"' if dash else '')+'/>')
 def rect(self,x,y,w,h,fill=PALE,stroke='none',r=18): self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 def point(self,x,y,label=None,dx=0,dy=-22,c=NAVY):
  self.s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="white" stroke="{c}" stroke-width="5"/>')
  if label:self.text(x+dx,y+dy,label,36,c,weight=700)
 def arc(self,x,y,r,a,b,c=GREEN,w=5,arrow=True):
  # Compass angles: 0=north, positive clockwise; preserve signed sweep.
  pts=[(x+r*math.sin(math.radians(a+(b-a)*i/60)),y-r*math.cos(math.radians(a+(b-a)*i/60))) for i in range(61)]
  self.path(pts,c,w,arrow)
 def footer(self,t,c=NAVY):
  self.rect(35,634,830,64); self.text(450,677,t,29,c)
 def save(self):
  p=O/(self.name+'.svg'); tmp=p.with_suffix('.svg.tmp'); tmp.write_text(''.join(self.s)+'</g></svg>',encoding='utf-8');tmp.replace(p);return p

def vec(T,L):return (L*math.sin(math.radians(T)),-L*math.cos(math.radians(T)))
def ray(g,p,T,L,c=BLUE,arrow=True,w=6):
 d=vec(T,L);g.line(*p,p[0]+d[0],p[1]+d[1],c,w,arrow);return p[0]+d[0],p[1]+d[1]
def north(g,x=790,y=160,L=80):
 g.line(x,y,x,y-L,NAVY,4,True);g.text(x,y-L-22,'座標北 X',25)
def traverse_coords(n=4):
 if n==4: lens=[120,95,117.015,102.977]; angles=[62.5,328+10/60+20/3600,246+30/60+20/3600,150+19/60+50/3600]
 else:lens=[85,110,96,84.894,127.412]; angles=[115+20/60+30/3600,53+56/60+10/3600,329+44/60+30/3600,277+55/60,195+8/60+30/3600]
 p=[(0,0)]
 for s,t in zip(lens,angles):p.append((p[-1][0]+s*math.sin(math.radians(t)),p[-1][1]-s*math.cos(math.radians(t))))
 return p[:-1]
def map_pts(pts,box):
 x,y,w,h=box;xs=[p[0] for p in pts];ys=[p[1] for p in pts];k=min(w/(max(xs)-min(xs)),h/(max(ys)-min(ys)))
 return [(x+(a-min(xs))*k+(w-(max(xs)-min(xs))*k)/2,y+(b-min(ys))*k+(h-(max(ys)-min(ys))*k)/2) for a,b in pts]
def loop(g,pts,labels=True,c=BLUE):
 for i,p in enumerate(pts):
  q=pts[(i+1)%len(pts)];g.line(*p,*q,c,6)
  a=(p[0]*.54+q[0]*.46,p[1]*.54+q[1]*.46);b=(p[0]*.38+q[0]*.62,p[1]*.38+q[1]*.62);g.line(*a,*b,c,6,True)
 center=(sum(x for x,y in pts)/len(pts),sum(y for x,y in pts)/len(pts))
 for i,p in enumerate(pts):
  dx=p[0]-center[0];dy=p[1]-center[1];d=math.hypot(dx,dy);g.point(*p,chr(65+i) if labels else None,dx/d*34,dy/d*34+10)

def generate_deflection():
 """共通例題B。後視基準のβと進行方向基準の符号付きδを分離する。"""
 g=SVG('deflection','共通例題B：進行方向の延長から測る符号付き偏角')
 p=(500,430); t_ab=62.5; t_bc=328+10/60+20/3600
 g.text(450,66,'共通例題B：進行方向からの曲がり',34)
 # BA is the backsight; AB has the opposite direction on the same line.
 a=ray(g,p,t_ab+180,340,GRAY)
 c=ray(g,p,t_bc,325,BLUE)
 ext=vec(t_ab,330)
 g.line(*p,p[0]+ext[0],p[1]+ext[1],NAVY,5,True,True)
 # A short travel arrow, physically separated from the backsight arrowhead.
 u=vec(t_ab+180,235); v=vec(t_ab+180,145)
 g.line(p[0]+u[0],p[1]+u[1],p[0]+v[0],p[1]+v[1],NAVY,7,True)
 g.arc(*p,105,t_ab+180,t_bc,ORANGE,6)
 # End at T_BC-360, so the arc explicitly sweeps left (negative).
 g.arc(*p,175,t_ab,t_bc-360,GREEN,6)
 g.point(*p,'B',32,37);g.point(*a,'A',-28,15);g.point(*c,'C',-24,-22)
 g.text(220,465,'後視 BA',31,GRAY)
 g.text(335,570,'進行 AB',31,NAVY)
 g.text(270,333,'β = 85°40′20″',30,ORANGE)
 g.text(365,400,'右回り',25,ORANGE)
 g.text(625,194,'δ ＜ 0',37,GREEN)
 g.text(625,235,'左へ曲がる',29,GREEN)
 g.text(727,410,'進行 AB の延長',29,NAVY)
 g.text(347,202,'前視 BC',28,BLUE,anchor='end')
 g.footer('δ = β − 180° = −94°19′40″（左折）',GREEN)
 return g.save()

# 1. Coordinate axes and clockwise direction angle.
g=SVG('axes','座標軸と方向角');p=(230,520)
g.line(*p,230,105,NAVY,5,True);g.line(*p,785,520,NAVY,5,True);g.text(230,70,'X：座標北',35);g.text(770,575,'Y：東',35)
ray(g,p,55,470);g.point(*p,'A',-35,32);g.point(*ray(SVG('_',''),p,55,470),None) if False else None
g.point(230+vec(55,470)[0],520+vec(55,470)[1],'B',30,-10);g.arc(*p,140,0,55);g.text(303,336,'T',42,GREEN);g.footer('座標北を 0° とし、時計回りに測る');g.save()
# Reverse line direction.
g=SVG('reverse','前方と後方の方向角')
for cx,cy,T,label,color in [(245,280,62.5,'A → B',BLUE),(650,280,242.5,'B → A',ORANGE)]:
 g.line(cx,cy,cx,cy-145,GRAY,3,True,True);ray(g,(cx,cy),T,175,color);g.arc(cx,cy,83,0,T,color,4);g.point(cx,cy);g.text(cx,80,label,38,color);g.text(cx,510,'62°30′00″' if T<180 else '242°30′00″',34,color)
g.text(450,582,'＋180° → 360°で整える',33);g.footer('逆方向は 180° 違う');g.save()
# Backsight bridge, exact prior lesson example.
g=SVG('backsight','後視の方位から前視へ');p=(485,380)
ray(g,p,0,280,GRAY,False,3);g.text(555,105,'座標北',29);a=ray(g,p,220,260,GRAY);c=ray(g,p,320,310,BLUE)
g.point(*p,'B',40,35);g.point(*a,'A',-38,20);g.point(*c,'C',-20,-25);g.arc(*p,105,220,320,GREEN);g.text(277,370,'100°',34,GREEN)
g.text(660,240,'後視 BA',31,GRAY);g.text(660,287,'220°',36,GRAY);g.text(650,425,'前視 BC',31,BLUE);g.text(650,472,'320°',36,BLUE);g.footer('AB 40° → BA 220° → BC 320°');g.save()
# Observation angle at B, same geometry as lecture data.
g=SVG('turning','観測角β：後視から前視へ');p=(580,405);a=ray(g,p,242.5,380,GRAY);c=ray(g,p,328+10/60+20/3600,330,BLUE)
g.point(*p,'B',38,32);g.point(*a,'後視 A',-10,36);g.point(*c,'前視 C',-20,-30);g.arc(*p,140,242.5,328+10/60+20/3600,GREEN,6);g.text(375,370,'β',48,GREEN);g.text(685,260,'時計回り',32,GREEN);g.footer('必ず「B→A」から「B→C」へ');g.save()
generate_deflection()
# Interior vs observed angle.
g=SVG('interior','内角と時計回りの観測角')
g.text(235,70,'反時計回りの巡回',33);g.text(665,70,'時計回りの巡回',33)
p1=[(90,430),(355,430),(355,190),(90,190)];p2=[(530,430),(530,190),(795,190),(795,430)];loop(g,p1);loop(g,p2)
g.arc(355,430,64,270,360,GREEN,5);g.text(285,365,'β',36,GREEN);g.arc(530,190,75,180,450,ORANGE,5);g.text(635,285,'β',36,ORANGE)
g.text(235,550,'β＝内角',36,GREEN);g.text(665,550,'β＝360°−内角',32,ORANGE);g.footer('巡回方向で「内角との関係」が変わる');g.save()
# Angular adjustment.
g=SVG('angle_adjust','角閉合差を等配分');g.text(450,70,'観測和の超過 ＋40″',38,ORANGE)
g.rect(300,110,300,95,'#fff1e4');g.text(450,173,'εβ = ＋40″',38,ORANGE)
for x,label in [(125,'A'),(340,'B'),(555,'C'),(770,'D')]:
 g.line(450,215,x,325,GRAY,3,True);g.rect(x-90,355,180,160,'#edf8f3');g.text(x,410,label,36);g.text(x,475,'−10″',42,GREEN)
g.text(450,585,'−40″ ÷ 4点 ＝ −10″ / 角',34,GREEN);g.footer('等精度なら、反対符号で均等に配分');g.save()
# Four-point loop.
for name,title in [('direction_loop','講義例の方向角を一周'),('cover','点を結び、位置を求める')]:
 g=SVG(name,title);pts=map_pts(traverse_coords(),(160,135,535,405));loop(g,pts);north(g,790,160,80)
 g.text(450,72,'A → B → C → D → A',36);g.footer('反時計回りに巡回する閉合トラバース');g.save()
# Components.
g=SVG('components','距離を北と東の成分へ');a=(180,530);b=(690,180);e=(180,180)
g.path([a,e,b],GRAY,4,False,True);g.line(*a,*b,BLUE,7,True);g.line(*a,*e,GREEN,6,True);g.line(*e,*b,ORANGE,6,True);g.point(*a,'A',-28,35);g.point(*b,'B',32,-5)
g.text(95,360,'ΔX',38,GREEN);g.text(440,145,'ΔY',38,ORANGE);g.text(475,395,'S',42,BLUE);g.arc(*a,105,0,math.degrees(math.atan2(510,350)),GREEN);g.text(223,386,'T',38,GREEN);g.path([(180,205),(205,205),(205,180)],GRAY,3);g.footer('ΔX = S cos T　　ΔY = S sin T');g.save()
# Quadrants.
g=SVG('quadrants','象限と成分の符号');cx,cy=450,335
g.line(450,590,450,95,NAVY,4,True);g.line(100,335,795,335,NAVY,4,True);g.text(450,60,'X 座標北：0°',32);g.text(780,385,'Y 東',28)
for x,y,t,s,c in [(650,175,'0° < T < 90°','ΔX ＋　ΔY ＋',GREEN),(650,470,'90° < T < 180°','ΔX −　ΔY ＋',BLUE),(240,470,'180° < T < 270°','ΔX −　ΔY −',ORANGE),(240,175,'270° < T < 360°','ΔX ＋　ΔY −',GREEN)]:
 g.text(x,y,t,28,c);g.text(x,y+49,s,29,c)
g.footer('X の符号は南北、Y の符号は東西');g.save()
# Forward.
g=SVG('forward','既知点に成分を足す');a=(180,520);b=(680,200)
g.line(*a,*b,BLUE,7,True);g.path([a,(180,200),b],GRAY,4,False,True);g.point(*a,'A',-28,32);g.point(*b,'B',28,-10);g.text(185,590,'既知 (XA, YA)',31);g.text(665,125,'求める (XB, YB)',31);g.text(465,410,'S, T',37,BLUE);g.text(105,345,'ΔX',34,GREEN);g.text(420,165,'ΔY',34,ORANGE);g.footer('出発点の座標 ＋ 成分 ＝ 到着点の座標');g.save()
# Inverse generic northwest.
g=SVG('inverse','座標差から距離と方向角へ');a=(665,530);b=(240,220)
g.line(*a,*b,BLUE,7,True);g.path([a,(665,220),b],GRAY,4,False,True);g.line(*a,665,105,GRAY,3,True);g.point(*a,'P',35,30);g.point(*b,'Q',-30,-15);g.text(758,365,'ΔX ＋',32,GREEN);g.text(445,180,'ΔY −',32,ORANGE);g.arc(*a,95,0,306,BLUE,4);g.text(543,415,'T',37,BLUE);g.text(420,420,'S',37,BLUE);g.footer('まず ΔX = XQ−XP、ΔY = YQ−YP');g.save()
# Small loop closure, deliberately schematic gap.
g=SVG('closure','座標閉合差の概念');pts=[(195,500),(695,375),(530,135),(155,260)];g.path(pts+[ (250,480) ],BLUE,6)
for i,p in enumerate(pts):g.point(*p,chr(65+i),36 if i==1 else -24,35 if i==0 else -24)
g.point(250,480,'A′',40,25,c=ORANGE);g.line(195,500,250,480,ORANGE,7,True);g.rect(465,470,345,105,'#fff1e4');g.text(637,512,'A′ − A',33,ORANGE);g.text(637,554,'(fX, fY)',35,ORANGE);g.text(450,70,'一周後の座標が出発点とずれる',33);g.footer('図は閉合差を拡大した概念図');g.save()
# Bowditch weights visually proportional.
g=SVG('bowditch','距離に比例して閉合差を配分');g.text(450,70,'長い辺ほど補正量を大きく',35)
for y,label,L in [(180,'AB',420),(285,'BC',333),(390,'CD',410),(495,'DA',360)]:
 g.text(100,y+15,label,36);g.rect(170,y-22,L,48,'#dcecf5',r=8);g.line(170,y+43,170+L,y+43,GREEN,7,True);g.text(730,y+15,'S に比例',30,GREEN)
g.footer('cXi = −fX·Si / ΣS　（Y も同様）',GREEN);g.save()
# Three types.
g=SVG('types','トラバースの3つの形')
for y,label in [(120,'閉合'),(310,'結合'),(505,'開放')]:g.text(100,y,label,36)
loop(g,[(260,90),(470,75),(525,170),(320,180)],False)
g.point(260,90,None,c=GREEN);g.text(695,145,'同じ点へ戻る',31)
g.path([(260,300),(350,250),(435,330),(525,275)],BLUE,6);g.point(260,300,None,c=GREEN);g.point(525,275,None,c=GREEN);g.text(695,305,'別の既知点へ',31)
g.path([(260,505),(350,455),(435,535),(525,480)],BLUE,6,True);g.point(260,505,None,c=GREEN);g.text(695,510,'終点は未知点',31)
g.footer('緑の点：既知点　　青の線：測線');g.save()
# Site concept clean top-down agricultural roads / water.
g=SVG('site','農地と水路の周りに測点を置く')
for x in [95,310,525]:
 for y in [130,315]:g.rect(x,y,175,145,'#eaf1d9','#cbd9b6',8)
g.rect(740,80,85,485,'#d6edf7',r=0);g.line(782,100,782,540,BLUE,3,True);g.text(780,614,'水路',32,BLUE)
g.path([(70,100),(700,100),(700,520),(70,520),(70,100)],GRAY,22)
pts=[(70,520),(700,520),(700,100),(70,100)];loop(g,pts);g.text(390,280,'農地',38,GREEN);g.footer('見通し・安定・安全を確保して測点を選ぶ');g.save()
# Workflow vertical, simple and legible.
g=SVG('workflow','観測から座標までの流れ')
steps=[('現場観測','距離 S・角 β'),('角の点検・調整','内角和 → εβ'),('方向角を伝える','後視 → 時計回り β'),('成分に分ける','ΔX・ΔY'),('座標を足す','X・Y')]
for i,(title,sub) in enumerate(steps):
 y=30+i*120;g.rect(100,y,700,95,PALE);g.text(135,y+59,str(i+1),34,BLUE);g.text(435,y+42,title,33);g.text(435,y+79,sub,27,GRAY)
 if i<4:g.line(450,y+100,450,y+120,BLUE,4,True)
g.footer('点検しながら、順序を守って進める');g.save()
# Five-point exercise, computed positions with exact adjusted directions.
g=SVG('exercise_traverse','5点トラバース演習の見取り図');pts=map_pts(traverse_coords(5),(175,145,540,390));loop(g,pts);north(g,790,160,80);g.text(450,70,'A → B → C → D → E → A',34)
g.footer('始めの方向角：T_AB = 115°20′30″');g.save()
# Exercise inverse, no answers.
g=SVG('exercise_inverse','Pから北西にあるQへの逆計算');p=(710,520);q=(230,264)
g.path([p,(710,264),q],GRAY,4,False,True);g.line(*p,*q,BLUE,7,True);g.point(*p,'P',30,32);g.point(*q,'Q',-30,-15);g.line(710,520,710,125,GRAY,3,True);g.text(710,85,'座標北 X',30)
g.text(793,395,'ΔX',32,GREEN);g.text(793,435,'＋80',32,GREEN);g.text(455,225,'ΔY = −150',34,ORANGE)
g.text(235,135,'Q (1580, 2150)',31);g.text(620,595,'P (1500, 2300)',31);g.footer('P→Q は北西：距離と方向角を求める');g.save()

# Triangulation: one diagonal partitions a quadrilateral into two triangles.
g=SVG('triangulation','四角形の内角和を三角形2つで確かめる')
pts=[(275,530),(720,360),(550,130),(145,290)]
g.path([pts[0],pts[1],pts[2]],BLUE,0,fill='#edf5fb',close=True)
g.path([pts[0],pts[2],pts[3]],GREEN,0,fill='#edf8f3',close=True)
loop(g,pts,c=NAVY)
g.line(*pts[0],*pts[2],ORANGE,5,False,True)
g.text(530,365,'180°',44,BLUE);g.text(310,315,'180°',44,GREEN)
g.text(450,70,'対角線 1本 → 三角形 2つ',35)
g.footer('180° ＋ 180° ＝ 360°');g.save()

# Render all PNGs; sources stay editable, PNGs 2x for projection.
svgs=sorted(O.glob('*.svg'))
def render(p):
 target=p.with_suffix(".png"); tmp=p.with_suffix(".render.png")
 out=subprocess.run(['inkscape',str(p),'--export-type=png',f'--export-filename={tmp}','--export-width=1800'],capture_output=True,text=True)
 if out.returncode:raise RuntimeError(out.stderr)
 tmp.replace(target)
 return p.stem
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(render,svgs))
thumbs=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
for p in svgs:
 im=Image.open(p.with_suffix('.png')).convert('RGB');im.thumbnail((450,360));tile=Image.new('RGB',(470,410),'#e7edf0');tile.paste(im,((470-im.width)//2,40));ImageDraw.Draw(tile).text((12,6),p.stem,font=font,fill='#19354a');thumbs.append(tile)
sheet=Image.new('RGB',(470*4,410*math.ceil(len(thumbs)/4)),'#ccd6dd')
for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*470,(i//4)*410))
sheet.save(N/'diagrams_contact_sheet.jpg',quality=93)
print(f'{len(svgs)} diagrams generated in {O}')
