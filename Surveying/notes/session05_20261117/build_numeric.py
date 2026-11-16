#!/usr/bin/env python3
"""第05回改3の数値・数式入りExcel・A4演習/解答を再生成する。
python notes/session05_20261117/build_numeric.py（Surveying内または任意cwd）
依存: xlsxwriter, openpyxl, xelatex/fontspec, Noto Sans CJK JP。
角は入力から角秒で保持し、三角関数直前のみ度へ換算。成分は丸めず総和。
"""
from pathlib import Path
import json, math, subprocess
from fractions import Fraction
import xlsxwriter

N=Path(__file__).resolve().parent
ROOT=N.parents[1]
O=ROOT/'materials/slides/第05回_トラバース測量I/改3'
E=ROOT/'materials/exercises/第05回_トラバース測量I/改3'
for p in (O,E): p.mkdir(parents=True,exist_ok=True)

def sec(d,m=0,s=0): return d*3600+m*60+s

def dms(seconds, wrap=True):
    n=math.floor(abs(float(seconds))+.5)
    if wrap:n%=1296000
    d,r=divmod(n,3600);m,s=divmod(r,60)
    return ('−' if seconds<0 else '')+f'{d}°{m:02d}′{s:02d}″'

def inv(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    t=math.degrees(math.atan2(dy,dx))%360 if length else None
    return dict(start=a,end=b,dx=dx,dy=dy,distance=length,direction_deg=t,direction_dms=dms(t*3600) if t is not None else '未定義',reverse_deg=(t+180)%360 if t is not None else None,reverse_dms=dms(((t+180)%360)*3600) if t is not None else '未定義',atan_deg=math.degrees(math.atan(dy/dx)) if dx else None)

def traverse(points,obs,t0,lengths,tolerance):
    n=len(obs); theory=sec((n-2)*180);err=sum(obs)-theory;c=Fraction(-err,n)
    adjusted=[Fraction(v)+c for v in obs]
    ts=[Fraction(t0)]
    for b in adjusted[1:]+adjusted[:1]:ts.append((ts[-1]+sec(180)+b)%sec(360))
    rows=[];x=y=1000.0
    for i,(t,s) in enumerate(zip(ts,lengths)):
        dx=s*math.cos(math.radians(float(t)/3600));dy=s*math.sin(math.radians(float(t)/3600))
        x+=dx;y+=dy
        rows.append(dict(point=points[i],line=points[i]+points[(i+1)%n],observed_sec=obs[i],observed_dms=dms(obs[i]),correction_sec=float(c),adjusted_sec=float(adjusted[i]),adjusted_dms=dms(adjusted[i]),direction_sec=float(t),direction_deg=float(t)/3600,direction_dms=dms(t),distance=s,dx=dx,dy=dy,x=x,y=y,deflection_deg=float(adjusted[i])/3600-180))
    fx=math.fsum(r['dx'] for r in rows);fy=math.fsum(r['dy'] for r in rows);f=math.hypot(fx,fy);perimeter=math.fsum(lengths)
    bx=by=1000.
    for r in rows:
        r['bowditch_cx']=-fx*r['distance']/perimeter;r['bowditch_cy']=-fy*r['distance']/perimeter
        r['corrected_dx']=r['dx']+r['bowditch_cx'];r['corrected_dy']=r['dy']+r['bowditch_cy']
        bx+=r['corrected_dx'];by+=r['corrected_dy'];r['corrected_x']=bx;r['corrected_y']=by
    return dict(points=points,start=[1000.,1000.],t_start_sec=t0,t_start_dms=dms(t0),n=n,theory_sec=theory,observed_sum_sec=sum(obs),observed_sum_dms=dms(sum(obs),False),angle_error_sec=err,correction_each_sec=float(c),adjusted_sum_sec=float(sum(adjusted)),tolerance_sec=tolerance,within_tolerance=abs(err)<=tolerance,rows=rows,return_direction_sec=float(ts[-1]),return_direction_dms=dms(ts[-1]),angular_return_error_sec=float((ts[-1]-t0+sec(180))%sec(360)-sec(180)),unadjusted_return_direction_dms=dms(t0+err),perimeter=perimeter,closure_x=fx,closure_y=fy,closure_distance=f,closure_ratio_denominator=perimeter/f if f else None,display_sum_x=math.fsum(round(r['dx'],3) for r in rows),display_sum_y=math.fsum(round(r['dy'],3) for r in rows),corrected_closure_x=math.fsum(r['corrected_dx'] for r in rows),corrected_closure_y=math.fsum(r['corrected_dy'] for r in rows))

lecture=traverse('ABCD',[sec(92,10,20),sec(85,40,30),sec(98,20,10),sec(83,49,40)],sec(62,30),[120.,95.,117.015,102.977],40)
exercise=traverse('ABCDE',[sec(100,12,12),sec(118,35,52),sec(95,48,32),sec(128,10,42),sec(97,13,42)],sec(115,20,30),[85.,110.,96.,84.894,127.412],80)
inverse=inv([1500.,2300.],[1580.,2150.])
data=dict(meta=dict(coordinates='X=座標北、Y=東',angle_definition='β: 後視→前視を時計回り。反時計回りループでは内角。',direction_rule='T_next=mod(T_prev+180°+β,360°)',precision='内部成分を丸めずに計算。表示mは0.001、角は1秒。',distance='換算済みの平面計算用距離。授業では水平距離との差を無視できると仮定。',synthetic='合成教材。小さい座標閉合差や大きい閉合比は観測精度の実証ではない。',tolerance='規程値でなく授業用仮定: 講義4点40秒、演習5点80秒。等精度角。',exercise_change='旧版の5点観測値は維持。εβ=+60秒に対し演習用許容80秒を明記。旧版の閉合差が小さければ正しいとする記述を削除。'),lecture=lecture,exercise=exercise,inverse=inverse,inverse_cases=[inv([0,0],[x,y]) for x,y in [(300,400),(-300,400),(-300,-400),(300,-400),(0,200),(-50,50),(50,-50),(0,0)]])
(N/'example.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

# Excel: 数式キャッシュも保存するためExcel未導入環境でも表示できる。
book=xlsxwriter.Workbook(O/'計算ワークブック.xlsx')
book.set_properties({'title':'第05回 トラバース測量I 改3 計算ワークブック','author':'測量学教材'})
fmt={k:book.add_format(v) for k,v in dict(title={'bold':True,'font_size':16,'font_color':'#183248'},head={'bold':True,'bg_color':'#183248','font_color':'white','border':1},text={'font_size':11,'text_wrap':True},input={'bg_color':'#E9F2FA','num_format':'0.000'},sec={'num_format':'0.000','bg_color':'#F5F7F8'},number={'num_format':'+0.000;-0.000;0.000'},angle={'num_format':'0.00000000'},note={'font_color':'#626C73','text_wrap':True},ok={'bg_color':'#E6F1E9'},int={'num_format':'0'}).items()}
for f in fmt.values():f.set_font_name('Noto Sans CJK JP')
intro=book.add_worksheet('使い方')
intro.set_column('A:A',4);intro.set_column('B:B',112)
intro.write('B2','第05回 トラバース測量 I｜改3',fmt['title'])
notes=['青セルが入力、他は式。表示桁を超える内部値を保持する。成分の表示値を再入力して総和しない。','X=座標北、Y=東。方向角Tは座標北から時計回り。βは後視から前視へ時計回り。','本例は反時計回りループでβが内角。T_next=MOD(T_prev+180+β,360)。','角は入力角秒から度へ換算。三角関数では必ずRADIANS(度)を使う。DMS文字列は表示専用。','距離は換算済みの平面計算用距離。本授業では水平距離との差を無視できると仮定。','許容は講義4点40秒・演習5点80秒の授業条件。規程値ではない。各角等精度を仮定。','観測角和−理論角和がεβ。許容内かを判断してから、補正−εβ/nを各角へ加える。','合成教材のため原データがほぼ閉じている。これだけで測量精度を評価しない。','逆計算のExcel ATAN2はATAN2(ΔX,ΔY)という順序。Python atan2(ΔY,ΔX)と異なる。','同一点は距離0、方向角は未定義。未定義を0度として扱わない。','補足Bowditchは次回先取り。角調整の後に、座標閉合差を辺長に比例して配分する。','再生成: notes/session05_20261117/build_numeric.py。JSONとワークブックは同じ内部数値から作る。']
for i,t in enumerate(notes,4):intro.write(i,1,t,fmt['text']);intro.set_row(i,33)

def fw(ws,cell,formula,value,kind='angle'):ws.write_formula(cell,formula,fmt[kind],value)
def dms_formula(ref):
    # 秒を先に丸めた整数にしてから度・分・秒に分解し、60秒/360度の桁上げに対応。
    r=f'MOD(ROUND({ref}*3600,0),1296000)'
    return f'=INT({r}/3600)&"°"&TEXT(INT(MOD({r},3600)/60),"00")&"′"&TEXT(MOD({r},60),"00")&"″"'

def sheet_traverse(name,t):
    w=book.add_worksheet(name);w.freeze_panes(8,2);w.set_landscape();w.fit_to_pages(1,1)
    w.set_column('A:A',8);w.set_column('B:D',9);w.set_column('E:G',14);w.set_column('H:H',19);w.set_column('I:I',12);w.set_column('J:J',15);w.set_column('K:K',19);w.set_column('L:O',15)
    w.merge_range('A1:O1',name+'｜角調整から座標まで',fmt['title'])
    for cell,label in [('A3','既知T_AB(度)'),('D3','観測和(秒)'),('G3','理論和(秒)'),('J3','εβ(秒)'),('M3','許容(秒)')]:w.write(cell,label,fmt['text'])
    w.write_number('B3',t['t_start_sec']/3600,fmt['input']);fw(w,'E3','=SUM(E9:E%d)'%(8+t['n']),t['observed_sum_sec'],'sec');fw(w,'H3','=(COUNTA(A9:A%d)-2)*180*3600'%(8+t['n']),t['theory_sec'],'sec');fw(w,'K3','=E3-H3',t['angle_error_sec'],'sec');w.write_number('N3',t['tolerance_sec'],fmt['input'])
    w.write('A5','補正/角(秒)');fw(w,'B5','=-K3/COUNTA(A9:A%d)'%(8+t['n']),t['correction_each_sec'],'sec');w.write('D5','許容判定');fw(w,'E5','=IF(ABS(K3)<=N3,"許容内","再観測を検討")','許容内' if t['within_tolerance'] else '再観測を検討','text')
    w.write('G5','始点X');w.write_number('H5',t['start'][0],fmt['input']);w.write('J5','始点Y');w.write_number('K5',t['start'][1],fmt['input'])
    w.merge_range('A6:O6','授業用許容・等精度。合成教材の小さな閉合差を精度の証拠にしない。内部値は丸めない。X北・Y東。',fmt['note'])
    heads=['点/測線','観測 度','分','秒','観測角秒','補正秒','調整角(度)','調整角DMS','距離S(m)','T(度)','T DMS','ΔX(m)','ΔY(m)','到達X(m)','到達Y(m)']
    w.write_row(7,0,heads,fmt['head'])
    for i,r in enumerate(t['rows']):
        row=9+i;j=row-1;v=r['observed_sec'];deg,rem=divmod(v,3600);minute,second=divmod(rem,60)
        w.write(j,0,r['line']);w.write_row(j,1,[deg,minute,second],fmt['input'])
        fw(w,f'E{row}',f'=B{row}*3600+C{row}*60+D{row}',v,'sec');fw(w,f'F{row}','=$B$5',r['correction_sec'],'sec');fw(w,f'G{row}',f'=(E{row}+F{row})/3600',r['adjusted_sec']/3600)
        fw(w,f'H{row}',dms_formula(f'G{row}'),r['adjusted_dms'],'text');w.write_number(j,8,r['distance'],fmt['input'])
        form='=$B$3' if i==0 else f'=MOD(J{row-1}+180+G{row},360)'
        fw(w,f'J{row}',form,r['direction_deg']);fw(w,f'K{row}',dms_formula(f'J{row}'),r['direction_dms'],'text')
        fw(w,f'L{row}',f'=I{row}*COS(RADIANS(J{row}))',r['dx'],'number');fw(w,f'M{row}',f'=I{row}*SIN(RADIANS(J{row}))',r['dy'],'number')
        fw(w,f'N{row}',f'={"$H$5" if i==0 else "N"+str(row-1)}+L{row}',r['x'],'number');fw(w,f'O{row}',f'={"$K$5" if i==0 else "O"+str(row-1)}+M{row}',r['y'],'number')
    end=8+t['n'];total=end+2
    w.write(f'A{total}','内部総和',fmt['head'])
    for col,value in [('I',t['perimeter']),('L',t['closure_x']),('M',t['closure_y'])]:fw(w,f'{col}{total}',f'=SUM({col}9:{col}{end})',value,'number')
    w.write(f'A{total+2}','一周T(度)');fw(w,f'B{total+2}',f'=MOD(J{end}+180+G9,360)',t['return_direction_sec']/3600);fw(w,f'C{total+2}',dms_formula(f'B{total+2}'),t['return_direction_dms'],'text')
    w.write(f'E{total+2}','角一周差(秒)');fw(w,f'F{total+2}',f'=(MOD(B{total+2}-$B$3+180,360)-180)*3600',0,'sec')
    w.write(f'A{total+4}','表示値総和');fw(w,f'L{total+4}','='+'+'.join(f'ROUND(L{i},3)' for i in range(9,end+1)),t['display_sum_x'],'number');fw(w,f'M{total+4}','='+'+'.join(f'ROUND(M{i},3)' for i in range(9,end+1)),t['display_sum_y'],'number')
    w.merge_range(f'A{total+6}:O{total+6}','表示値の総和と内部値の総和は異なることがある。補正・検算は内部値で行う。',fmt['note'])
    return name,end,total
lecture_sheet=sheet_traverse('講義4点',lecture);exercise_sheet=sheet_traverse('演習5点',exercise)
w=book.add_worksheet('逆計算');w.set_column('A:F',22);w.merge_range('A1:F1','逆計算｜X北・Y東',fmt['title']);w.write_row('A3',['点','X(m)','Y(m)'],fmt['head'])
for row,label,xy in [(4,'P',inverse['start']),(5,'Q',inverse['end'])]:w.write(f'A{row}',label);w.write_row(f'B{row}',xy,fmt['input'])
for row,label,form,value,kind in [(7,'ΔX','=B5-B4',inverse['dx'],'number'),(8,'ΔY','=C5-C4',inverse['dy'],'number'),(9,'S(m)','=SQRT(B7^2+B8^2)',inverse['distance'],'number'),(10,'T_PQ(度)','=IF(B9=0,"未定義",MOD(DEGREES(ATAN2(B7,B8)),360))',inverse['direction_deg'],'angle'),(11,'T_PQ DMS','=IF(B9=0,"未定義",'+dms_formula('B10')[1:]+')',inverse['direction_dms'],'text'),(12,'T_QP(度)','=IF(B9=0,"未定義",MOD(B10+180,360))',inverse['reverse_deg'],'angle')]:w.write(f'A{row}',label);fw(w,f'B{row}',form,value,kind)
w.merge_range('A15:F15','Excel ATAN2(ΔX,ΔY)。同一点では方向角を未定義にする。',fmt['note'])
w.write_row('A17',['検証例','ΔX','ΔY','距離','T(度)','T DMS'],fmt['head'])
for idx,r in enumerate(data['inverse_cases'],18):
    w.write(f'A{idx}','同一点' if r['distance']==0 else f'例{idx-17}');w.write_number(f'B{idx}',r['dx']);w.write_number(f'C{idx}',r['dy']);fw(w,f'D{idx}',f'=SQRT(B{idx}^2+C{idx}^2)',r['distance'],'number');fw(w,f'E{idx}',f'=IF(D{idx}=0,"未定義",MOD(DEGREES(ATAN2(B{idx},C{idx})),360))',r['direction_deg'] if r['distance'] else '未定義');fw(w,f'F{idx}',f'=IF(D{idx}=0,"未定義",'+dms_formula(f'E{idx}')[1:]+')',r['direction_dms'],'text')

w=book.add_worksheet('補足Bowditch');w.set_column('A:A',11);w.set_column('B:J',17);w.merge_range('A1:J1','次回先取り｜講義4点のBowditch補正',fmt['title']);w.merge_range('A3:J3','角調整済み・距離誤差等の条件を確認した後の配分例。閉合比は合成教材の精度を実証しない。',fmt['note']);w.write_row('A5',['測線','S','未補正ΔX','未補正ΔY','補正cX','補正cY','補正後ΔX','補正後ΔY','補正後X','補正後Y'],fmt['head'])
for i,r in enumerate(lecture['rows']):
    row=6+i;src=9+i;w.write(f'A{row}',r['line'])
    previous_x="'講義4点'!$H$5" if i==0 else f'I{row-1}'
    previous_y="'講義4点'!$K$5" if i==0 else f'J{row-1}'
    for col,form,val in [('B',f"='講義4点'!I{src}",r['distance']),('C',f"='講義4点'!L{src}",r['dx']),('D',f"='講義4点'!M{src}",r['dy']),('E',f'=-$C$11*B{row}/$B$11',r['bowditch_cx']),('F',f'=-$D$11*B{row}/$B$11',r['bowditch_cy']),('G',f'=C{row}+E{row}',r['corrected_dx']),('H',f'=D{row}+F{row}',r['corrected_dy']),('I',f'={previous_x}+G{row}',r['corrected_x']),('J',f'={previous_y}+H{row}',r['corrected_y'])]:fw(w,f'{col}{row}',form,val,'number')
w.write('A11','内部総和')
for col,key in [('B','distance'),('C','dx'),('D','dy'),('E','bowditch_cx'),('F','bowditch_cy'),('G','corrected_dx'),('H','corrected_dy')]:fw(w,f'{col}11',f'=SUM({col}6:{col}9)',math.fsum(r[key] for r in lecture['rows']),'number')
w.write('A13','閉合差f(m)');fw(w,'B13','=SQRT(C11^2+D11^2)',lecture['closure_distance'],'angle');w.write('A14','閉合比1:');fw(w,'B14','=IF(B13=0,"閉合差0",B11/B13)',lecture['closure_ratio_denominator'],'number');book.close()

# A4 PDF。改3独自原稿を同じ数値から生成し、既存演習本文は保持する。
PRE=r'''\documentclass[a4paper,10pt]{article}
\usepackage[margin=17mm]{geometry}
\usepackage{fontspec,amsmath,array,tabularx,xcolor}
\setmainfont{Noto Sans CJK JP}
\setsansfont{Noto Sans CJK JP}
\XeTeXlinebreaklocale "ja"
\XeTeXlinebreakskip=0pt plus 1pt
\definecolor{navy}{HTML}{183248}
\definecolor{blue}{HTML}{276698}
\definecolor{green}{HTML}{24734A}
\definecolor{orange}{HTML}{B45B21}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\renewcommand{\arraystretch}{1.34}
\newcommand{\ttl}[2]{{\color{navy}\Large\bfseries #1}\par{\small #2}\par\vspace{2pt}\hrule\vspace{7pt}}
\newcommand{\sub}[1]{\par{\color{navy}\large\bfseries #1}\par}
\newcommand{\boxwork}[1]{\par\noindent\fbox{\parbox[t][#1][t]{0.965\linewidth}{\vspace{1pt}\hspace{2mm}{\color{gray}\small 途中式・検算}}}\par}
\newcommand{\note}[1]{{\small\color{blue}#1}\par}
\begin{document}
'''
def esc(s):return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
def tab(head,rows,widths=None):
    columns=widths or ('|'+'l|'*len(head))
    out=[r'\begin{center}\small\begin{tabular}{'+columns+'}',r'\hline', ' & '.join(r'\textbf{'+esc(h)+'}' for h in head)+r' \\ \hline']
    out += [' & '.join(esc(s) for s in row)+r' \\ \hline' for row in rows]
    return '\n'.join(out+[r'\end{tabular}\end{center}'])

def signed(v):return f'{v:+.3f}'.replace('-','−')
rows=exercise['rows'];ex=exercise
student=PRE+r'''\ttl{第05回 トラバース測量 I｜演習（改3）}{25分・10点満点　関数電卓可　問1 15分／問2 7分／検算 3分}
授業内指定の提出番号：\underline{\hspace{38mm}}　確認：\underline{\hspace{30mm}}

{\small 角は度分秒（1″）、距離・座標はm（0.001 m）まで。途中で三角関数や成分を丸めない。方向角は0°以上360°未満。電卓はDEG。}
\sub{問1　5点の閉合トラバース（6点）}
{\small Xは北、Yは東。反時計回りにA→B→C→D→E→Aと進む。βは各点の後視から前視へ時計回りに測る内角。既知方向角は $T_{AB}=$115°20′30″。距離は平面計算用距離で、水平距離との差は無視できると仮定する。}
'''+tab(['測点','観測内角β','測線','S (m)'],[[r['point'],r['observed_dms'],r['line'],f"{r['distance']:.3f}"] for r in rows])+r'''
noteplaceholder
{\small (1) 観測角和・角閉合差 εβ（観測−理論）・1角の補正を求め、表①を完成する。許容内かも判定する。（2点）}

{\small 観測和：\underline{\hspace{28mm}}　理論和：\underline{\hspace{20mm}}　εβ：\underline{\hspace{14mm}}″
　判定：\underline{\hspace{15mm}}　補正/角：\underline{\hspace{15mm}}″}
'''.replace('noteplaceholder',r'\note{授業用仮定：角閉合差の許容は±80″、各角は等精度。規程値ではない。}').replace('\\note',r'\note')
student+=tab(['表① 測点','補正 (″)','調整角'],[[r['point'],'',''] for r in rows]+[['和','','']], '|p{22mm}|p{32mm}|p{70mm}|')
student+=r'''{\small (2) 調整角を使ってBC、CD、DE、EAの方向角を求め、Aの角を使いABに戻ることを確認する。（2.5点）}
'''+tab(['表② 測線','前のT＋180°＋次の点の調整角','mod 360°後のT'],[['AB','既知','115°20′30″']]+[[r['line'],'',''] for r in rows[1:]]+[['AB 検算','','']], '|p{22mm}|p{87mm}|p{37mm}|')
student+=r'''{\small (3) BC、CD、EAのΔX・ΔYを計算する。AB・DEも元のS・Tで再計算して合計し、最後に0.001 mへ丸める。（1.5点）}
'''+tab(['表③ 測線','S (m)','ΔX＝S cos T (m)','ΔY＝S sin T (m)'],[[r['line'],f"{r['distance']:.3f}",signed(r['dx']) if i in (0,3) else '',signed(r['dy']) if i in (0,3) else ''] for i,r in enumerate(rows)]+[['内部総和','503.306','','']], '|p{22mm}|p{26mm}|p{43mm}|p{43mm}|')
student+=r'''\newpage
\ttl{問2　座標の逆計算（4点）}{X＝座標北、Y＝東／方向角は座標北から時計回り}
出発点Pから既知点Qを後視し、方向を与えたい。次の座標から計算する。
'''+tab(['点','X (m)','Y (m)'],[['P','1500.000','2300.000'],['Q','1580.000','2150.000']])+r'''
\textbf{(1)} PからQへの座標差を符号付きで求め、象限と向きを書く。（1点）

ΔX＝\underline{\hspace{30mm}} m　ΔY＝\underline{\hspace{30mm}} m

象限：\underline{\hspace{25mm}}　向き：\underline{\hspace{25mm}}
\boxwork{24mm}
\textbf{(2)} 距離 $S_{PQ}$ を求める。（1点）
\boxwork{28mm}
答：$S_{PQ}=$\underline{\hspace{40mm}} m

\textbf{(3)} 方向角 $T_{PQ}$ を求める。arctan(ΔY/ΔX)の値と加える角を書く。（1.5点）
\boxwork{34mm}
arctanの値：\underline{\hspace{34mm}}　加える角：\underline{\hspace{24mm}}

答：$T_{PQ}=$\underline{\hspace{40mm}}

\textbf{(4)} 反方向角 $T_{QP}$ を求める。（0.5点）

答：$T_{QP}=$\underline{\hspace{40mm}}

\vfill
\note{検算：順計算でPからQへ戻るか確認する。同一点なら距離0、方向角は未定義。}
{\small 発展（加点なし）：問1を観測角のままで一周するとABの方向角は既知値より何秒ずれるか。答：\underline{\hspace{20mm}}″}
\end{document}
'''
# Raw literal correction: source must contain a single TeX command slash.
student=student.replace(r'\\note{',r'\note{')
answers=PRE+r'''\ttl{第05回 トラバース測量 I｜教員用解答（改3）}{採点10点／同じ内部数値からPDF・Excel・JSONを再生成}
\sub{問1 (1)　角閉合差と等配分（2点）}
観測和は540°01′00″、理論和は$(5-2)\times180°=540°$。
\[
\varepsilon_\beta=\sum\beta_{\rm obs}-(n-2)180°=+60″,
\qquad v_\beta=-\frac{\varepsilon_\beta}{n}=-12″.
\]
授業用許容±80″に対し $|+60″|\le80″$ なので許容内。各角等精度という条件で等配分する。許容外なら機械的に配分せず、観測・記録を点検する。
'''+tab(['点','観測β','補正','調整β'],[[r['point'],r['observed_dms'],'−12″',r['adjusted_dms']] for r in rows]+[['和','540°01′00″','−60″','540°00′00″']])+r'''
\note{採点：観測和・εβと許容判定0.5点、補正−12″ 0.5点、調整角と総和1.0点。}
\sub{問1 (2)　方向角（2.5点）}
後視の方向角は前のT＋180°。そこからβを時計回りに加え、0°以上360°未満に整える。
\[T_{\rm next}=\operatorname{mod}(T_{\rm prev}+180°+\beta,\ 360°)\]
'''+tab(['測線','後視方向角＋調整β（整える前）','方向角T'],[['AB','既知','115°20′30″']]+[[rows[(i+1)%5]['line'] if i<4 else 'AB 検算',dms(rows[i]['direction_sec']+sec(180)+rows[(i+1)%5]['adjusted_sec'],False),rows[(i+1)%5]['direction_dms'] if i<4 else '115°20′30″'] for i in range(5)])+r'''
\note{採点：BC・CD・DE・EA各0.5点（±2″）、ABに戻る検算0.5点。}
{\small 旧版は5点の数値を維持し、角許容80″を授業条件として明記した。講義4点の許容40″を流用すると60″は許容外になる。両者はいずれも規程値ではない。}
\newpage
\ttl{問1 (3)　成分計算と総和（1.5点）}{X＝北・Y＝東／計算途中では丸めない}
\[\Delta X=S\cos T,\qquad \Delta Y=S\sin T\]
'''+tab(['測線','S (m)','方向角T','ΔX (m)','ΔY (m)'],[[r['line'],f"{r['distance']:.3f}",r['direction_dms'],signed(r['dx']),signed(r['dy'])] for r in rows]+[['内部総和','503.306','',signed(ex['closure_x']),signed(ex['closure_y'])]])+r'''
BCの計算例：$110.000\cos(53°56′10″)=+64.755569\ldots$ m、
$110.000\sin(53°56′10″)=+88.919717\ldots$ m。

\textbf{総和の表示に注意}

未丸めの内部値から計算すると、
'''+f"ΣΔX＝{ex['closure_x']:+.12f} m、ΣΔY＝{ex['closure_y']:+.12f} m。\n\n"+r'''したがって表の内部総和は0.001 m表示で −0.001 m、0.000 mとなる。各辺を先に0.001 mへ丸めて足すと0.000 m、＋0.001 mとなり、違う値になる。検算・補正には内部総和を使う。

\note{採点：BC・CD・EAの各辺0.5点、計1.5点。各成分の符号が正しく、±0.002 mを目安に評価する。総和は検算課題であり、得点内訳に含めない（本演習は計10点）。表示値を足した合計が出た場合は、内部値総和との違いを説明する。}
\textbf{小さい閉合差の解釈}

距離は合成教材用に設定してある。小さい座標閉合差や大きい閉合比だけを、実測の精度が高い証拠にしてはいけない。角の点検、方向角の一周検算、象限と符号をそれぞれ確認する。閉合比とBowditch補正は次回の内容で、本演習の採点対象外。

\textbf{授業で拾う誤り}

・DEG設定のまま度で計算する。ExcelはCOS(RADIANS(T))を使う。

・BCは北東で両成分が正、CDは北西でΔYが負。

・観測角で方向角を作らず、調整角を用いる。

・AB・DEの表示成分は確認用。総和を求めるときはそれらも元の距離と方向角から再計算する。

\sub{発展（加点なし）}
観測角のままで一周すると角和が理論値より60″大きいので、ABの方向角は115°21′30″となり、既知値から＋60″ずれる。
\newpage
\ttl{問2　座標の逆計算（4点）}{距離・方向角を求め、順計算で検算する}
\sub{(1) 座標差と象限（1点）}
\[\Delta X=1580-1500=+80.000\ \mathrm{m},\qquad
\Delta Y=2150-2300=-150.000\ \mathrm{m}\]
ΔX＞0、ΔY＜0なので、講義の象限表記では第4象限（北西）。
\note{採点：符号付き座標差0.5点、象限・向き0.5点。}
\sub{(2) 距離（1点）}
\[S_{PQ}=\sqrt{80^2+(-150)^2}=\sqrt{28900}=170.000\ \mathrm{m}\]
\note{採点：式と値1.0点。8：15：17の直角三角形。}
\sub{(3) 方向角（1.5点）}
\[\arctan(\Delta Y/\Delta X)=\arctan(-1.875)=-61°55′39″\]
第4象限なので360°を加え、$T_{PQ}=298°04′21″$。

内部値は298.07248693585296°。1秒表示へ丸める前の角で順計算すると、ΔX＝＋80.000 m、ΔY＝−150.000 m、Q＝(1580.000, 2150.000) mへ戻る。1秒表示角を再入力すると小さな丸め差が出るため、元の内部値と混ぜない。
\note{採点：arctanの値0.5点、＋360° 0.5点、Tの値（±2″）0.5点。}
\sub{(4) 反方向角（0.5点）}
\[T_{QP}=\operatorname{mod}(T_{PQ}+180°,360°)=118°04′21″\]
\note{採点：0.5点。}
\sub{逆計算の境界条件}
arctan(ΔY/ΔX)だけでは象限を区別できず、ΔX＝0で割れない。プログラムなら象限対応のatan2を使う。Pythonではatan2(ΔY,ΔX)、ExcelではATAN2(ΔX,ΔY)。同一点は距離0、方向角は未定義とする。

\vfill
{\small 再生成原稿：notes/session05\_20261117/build\_numeric.py。数値例は合成教材。距離は換算済み平面計算用距離。X北・Y東、Tは北から時計回り。}
\end{document}
'''
for filename,source in [('学生用演習',student),('教員用解答',answers)]:
    path=E/(filename+'.tex');path.write_text(source)
    subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(E),str(path)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

# 独立した数値・ファイル点検。相対的な誤差の判定と表示丸めの区別を記録する。
import openpyxl
checks={}
checks['lecture_angle_error_40_sec']=lecture['angle_error_sec']==40
checks['exercise_angle_error_60_sec']=exercise['angle_error_sec']==60
for name,t in [('lecture',lecture),('exercise',exercise)]:
    checks[name+'_adjusted_angle_sum_exact']=t['adjusted_sum_sec']==t['theory_sec']
    checks[name+'_angular_round_trip_exact']=t['angular_return_error_sec']==0
    checks[name+'_within_teaching_tolerance']=t['within_tolerance']
    checks[name+'_bowditch_closes_lt_1e_10_m']=max(abs(t['corrected_closure_x']),abs(t['corrected_closure_y']))<1e-10
    checks[name+'_unrounded_sum_used']=t['closure_x']!=t['display_sum_x']
    checks[name+'_positive_ccw_area']=sum(t['rows'][i]['y']*t['rows'][(i+1)%t['n']]['x']-t['rows'][(i+1)%t['n']]['y']*t['rows'][i]['x'] for i in range(t['n']))>0
checks['inverse_distance_exact_170']=inverse['distance']==170
checks['inverse_roundtrip_lt_1e_10']=abs(1500+170*math.cos(math.radians(inverse['direction_deg']))-1580)<1e-10 and abs(2300+170*math.sin(math.radians(inverse['direction_deg']))-2150)<1e-10
checks['same_point_direction_undefined']=data['inverse_cases'][-1]['direction_deg'] is None
checks['dms_half_second_rounds_up']=dms(.5)=='0°00′01″'
checks['dms_seconds_carry']=dms(sec(359,59,59)+.6)=='0°00′00″'
checks['quadrants_correct']=[r['direction_deg']//90 for r in data['inverse_cases'][:4]]==[0,1,2,3]
fbook=openpyxl.load_workbook(O/'計算ワークブック.xlsx',data_only=False)
cbook=openpyxl.load_workbook(O/'計算ワークブック.xlsx',data_only=True)
formulas=[];missing=[];errors=[]
for ws in fbook:
    for row in ws:
        for cell in row:
            if cell.data_type=='f':
                formulas.append([ws.title,cell.coordinate,cell.value])
                cached=cbook[ws.title][cell.coordinate]
                if cached.value is None:missing.append([ws.title,cell.coordinate])
                if cached.data_type=='e':errors.append([ws.title,cell.coordinate,cached.value])
checks['xlsx_formulas_present']=len(formulas)>150
checks['xlsx_formula_cache_complete']=not missing
checks['xlsx_cached_no_errors']=not errors
checks['xlsx_same_point_cached_undefined']=cbook['逆計算']['E25'].value=='未定義'
checks['xlsx_trig_radians']=all('RADIANS(' in form for _,_,form in formulas if '*COS(' in form or '*SIN(' in form)
# 保存済み式を読み、始点だけを変えて座標加算の依存鎖を独立評価する。
# G/H列の補正後成分は始点に依存しないので保存キャッシュを用いる。
import re
coordinate_cells={('補足Bowditch',f'{col}{row}') for col in ('I','J') for row in range(6,10)}
def evaluate_coordinate(sheet,cell,inputs):
    key=(sheet,cell.replace('$',''))
    if key in inputs:return inputs[key]
    if key not in coordinate_cells:return cbook[key[0]][key[1]].value
    formula=fbook[key[0]][key[1]].value
    match=re.fullmatch(r"=(?:'([^']+)'!)?(\$?[A-Z]+\$?[1-9][0-9]*)\+(\$?[A-Z]+\$?[1-9][0-9]*)",formula)
    if match is None:raise ValueError(f'座標加算式の形式不正: {key}: {formula}')
    source,left,right=match.groups()
    return evaluate_coordinate(source or sheet,left,inputs)+evaluate_coordinate(sheet,right,inputs)
bowditch=fbook['補足Bowditch']
checks['xlsx_bowditch_start_references']=bowditch['I6'].value=="='講義4点'!$H$5+G6" and bowditch['J6'].value=="='講義4点'!$K$5+H6"
checks['xlsx_bowditch_coordinate_cache_consistent']=all(abs(evaluate_coordinate(sheet,cell,{})-cbook[sheet][cell].value)<1e-10 for sheet,cell in coordinate_cells)
start_change_cases=[]
for start_x,start_y in [(1234.5,-200.0),(-30.0,4500.25)]:
    overrides={('講義4点','H5'):start_x,('講義4点','K5'):start_y}
    max_error=0.0
    for row in range(6,10):
        for col,source,start in [('I','H5',start_x),('J','K5',start_y)]:
            actual=evaluate_coordinate('補足Bowditch',f'{col}{row}',overrides)
            expected=cbook['補足Bowditch'][f'{col}{row}'].value+start-cbook['講義4点'][source].value
            max_error=max(max_error,abs(actual-expected))
    final=[evaluate_coordinate('補足Bowditch',f'{col}9',overrides) for col in ('I','J')]
    closes=max(abs(final[0]-start_x),abs(final[1]-start_y))<1e-10
    start_change_cases.append(dict(start=[start_x,start_y],max_translation_error_m=max_error,final=final,closes_to_changed_start=closes))
checks['xlsx_bowditch_follows_changed_start']=all(case['max_translation_error_m']<1e-10 and case['closes_to_changed_start'] for case in start_change_cases)
pdf_pages={}
for filename,expected in [('学生用演習',2),('教員用解答',3)]:
    info=subprocess.check_output(['pdfinfo',str(E/(filename+'.pdf'))],text=True)
    pages=int(next(line.split(':')[1].strip() for line in info.splitlines() if line.startswith('Pages:')))
    pdf_pages[filename]=pages
    checks[filename+'_page_count']=pages==expected
    checks[filename+'_a4']='595.28 x 841.89' in info
    log=(E/(filename+'.log')).read_text()
    checks[filename+'_no_overfull_or_missing_fonts']=not any(t in log for t in ['Overfull','Missing character','Undefined control sequence'])
validation=dict(pdf_pages=pdf_pages,visual_review='2026-11-16: 全5ページをPNG化して目視。記入欄、罫線、数式、行切れ、余白を確認。',checks=checks,passed=all(checks.values()),formula_count=len(formulas),formula_cache_missing=missing,formula_errors=errors,lecture_closure_internal=[lecture['closure_x'],lecture['closure_y']],exercise_closure_internal=[exercise['closure_x'],exercise['closure_y']],exercise_sum_display_components=[exercise['display_sum_x'],exercise['display_sum_y']],notes=['角入力は整数角秒、等配分はFractionを使い浮動小数の角和誤差を回避。','内部成分は未丸めで総和。表示0.001mの総和を別記。','Excel数式はxlsxwriterでキャッシュ保存。数式再計算は未実施のためキャッシュ・式参照を点検。','PDFは原稿texとPythonを同梱。'],pdf_files=['学生用演習.pdf','教員用解答.pdf'])
validation['bowditch_changed_start_cases']=start_change_cases
(N/'numeric_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
if not validation['passed']:raise RuntimeError('数値点検失敗: '+str([k for k,v in checks.items() if not v]))
print(json.dumps({'passed':True,'formula_count':len(formulas),'outputs':[str(O/'計算ワークブック.xlsx'),str(E/'学生用演習.pdf'),str(E/'教員用解答.pdf')]},ensure_ascii=False))
