// 方向角と象限の補足。表・数式・座標差の散布図は編集可能。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const deps=process.env.CODEX_RUNTIME_DEPENDENCIES||path.resolve(path.dirname(process.execPath),'../..');
const skill=process.env.PRESENTATION_SKILL;
if(!skill)throw Error('PRESENTATION_SKILL を指定してください。');
const modules=path.join(deps,'node/node_modules');
process.env.RUNTIME_NODE_MODULES=modules;
const {Presentation,PresentationFile,FileBlob}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const out=path.join(root,'materials/slides/第03回_測量の座標/補足_方向角と象限_20261015');
const build=path.join(out,'build');
const previews=path.join(out,'preview');
const records=path.join(root,'notes/direction_angle_20261015');
await fs.mkdir(build,{recursive:true});await fs.mkdir(previews,{recursive:true});await fs.mkdir(records,{recursive:true});
const C={bg:'#FAF9F5',ink:'#153D50',blue:'#245989',teal:'#117E7A',rust:'#BB542E',muted:'#637680',grid:'#D8E1E5'};
const ppt=Presentation.create({slideSize:{width:1280,height:720}});
const manuscript=[];
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false,align='left',font='Meiryo'){
 const a=s.shapes.add({geometry:'textbox',name:str.slice(0,50),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=str;a.text.style={typeface:font,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};return a;
}
function eq(s,str,x,y,w,h,size=36,color=C.blue){return text(s,str,x,y,w,h,size,color,false,'left','Cambria Math');}
function base(title,sub,notes){
 const s=ppt.slides.add();s.background.fill=C.bg;
 text(s,'測量の座標　方向角と象限',58,20,1050,28,18,C.muted);
 text(s,title,58,65,1160,66,40,C.ink,true);
 if(sub)text(s,sub,61,140,1154,46,26);
 text(s,String(ppt.slides.items.length).padStart(2,'0'),1165,673,55,26,18,C.muted,false,'right');
 s.speakerNotes.text=notes;
 manuscript.push({title,sub,notes});return s;
}
function takeaway(s,str){text(s,str,61,618,1148,45,30,C.teal,true);}
function table(s,rows,x,y,widths,rowHeight=62,fontSize=27){
 const t=s.tables.add({rows:rows.length,columns:widths.length,left:x,top:y,width:widths.reduce((a,b)=>a+b,0),height:rowHeight*rows.length,columnWidths:widths,values:rows});
 t.borders.assign({fill:C.grid,width:1,style:'solid'});
 rows.forEach((row,r)=>{t.rows[r].height=rowHeight;row.forEach((v,c)=>{
  const cell=t.getCell(r,c);cell.fill=r===0?'#EAF0F3':r%2?'#FFFFFF':'#F5F7F7';
  cell.text.style={typeface:'Meiryo',fontSize:r===0?fontSize-2:fontSize,color:r===0?C.blue:C.ink,bold:r===0,alignment:'center',verticalAlignment:'middle',insets:7,autoFit:'none'};
 });});return t;
}
function scatter(s,series,x=684,y=207,w=500,h=360,max=1.4,unit=1){
 // 同じ縮尺の座標図にする。軸名は余白に配置し、中央での重なりを避ける。
 const d=360;x+=(w-d)/2;w=d;h=d;
 const chart=s.charts.add('scatter',{
  position:{left:x,top:y,width:w,height:h},hasLegend:false,scatterOptions:{style:'lineWithMarkers'},
  series:series.map(a=>({name:a.label,xValues:[0,a.dy],values:[0,a.dx],line:{fill:a.color,width:3},marker:{symbol:'circle',size:7,fill:a.color},dataLabels:{showValue:false}})),
  xAxis:{visible:true,min:-max,max,majorUnit:unit,crossesAt:0,tickLabelPosition:'none',textStyle:{fontSize:18,fill:C.muted},line:{fill:C.blue,width:1.5},majorGridlines:null},
  yAxis:{visible:true,min:-max,max,majorUnit:unit,crossesAt:0,tickLabelPosition:'none',textStyle:{fontSize:18,fill:C.muted},line:{fill:C.blue,width:1.5},majorGridlines:null},
  chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},
 });
 applyPresentationChartFont(chart,{fontFamily:'Meiryo'});
 series.forEach((a,i)=>{
  const sr=chart.series.getItemAt(i);sr.dataLabels.textStyle.typeface='Meiryo';
  sr.dataLabels.showLegendKey=false;sr.dataLabels.showValue=false;sr.dataLabels.showSeriesName=false;
  // ネイティブの点ラベルはPowerPointで幅が縮むため、数値に対応する注記を別に置く。
  if(series.length<=2){
   const px=x+w/2+a.dy/max*(w-30)/2,py=y+h/2-a.dx/max*(h-30)/2;
   text(s,a.label,px+(a.dy>0?12:-145),py+(a.dx>0?-38:10),160,36,25,a.color,true);
  }
 });
 text(s,'北（＋ΔX）',x+55,y-18,250,35,23,C.blue,true,'center');
 text(s,'東（＋ΔY）',x+w-65,y+h/2+34,170,34,23,C.blue,true);
 return chart;
}

{
 const s=base('方向角は、北から時計回りに測る','X は北向き、Y は東向き。始点から終点への座標差で向きを表す。',
 '添付スライドと同じ測量の約束を使う。X軸は北向き、Y軸は東向き。数学の通常の図のx軸右・y軸上とは異なる。方向角θはX軸の正方向（北）から時計回り。0°以上360°未満で表す。ΔX=X終点−X始点、ΔY=Y終点−Y始点。散布図は横軸ΔY、縦軸ΔX。象限番号は北東から時計回りに第1、第2、第3、第4。図の数値は説明用の座標差。');
 eq(s,'ΔX = X終点 − X始点',65,225,560,55,34);
 eq(s,'ΔY = Y終点 − Y始点',65,294,560,55,34);
 text(s,'北 0°　　東 90°',65,390,560,48,32,C.blue,true);
 text(s,'南 180°　西 270°',65,450,560,48,32,C.blue,true);
 scatter(s,[{dx:1,dy:0,label:'北 0°',color:C.blue,pos:'top'},{dx:0,dy:1,label:'東 90°',color:C.teal,pos:'right'},{dx:-1,dy:0,label:'南 180°',color:C.blue,pos:'bottom'},{dx:0,dy:-1,label:'西 270°',color:C.teal,pos:'left'}],670,207,540,360,1.65,1);
 takeaway(s,'象限は、ΔX・ΔY の符号から向きを確かめるために使う。');
}
{
 const s=base('正反対の方向でも、ΔY / ΔX は同じ','比を計算すると、両方が＋なのか、両方が−なのかを区別できない。',
 '北東AはΔX=1、ΔY=1で方向角45°。南西BはΔX=−1、ΔY=−1で方向角225°。ともにΔY/ΔX=1。同じ直線上の正反対の方向になる。tanの値だけでは、向きは180°の違いを残してしか決まらない。座標差が持っていた符号の組合せの情報が、比を作る際に失われる。点名A・Bと色を併用し、色だけに依存しない。');
 scatter(s,[{dx:1,dy:1,label:'A 45°',color:C.teal,pos:'top'},{dx:-1,dy:-1,label:'B 225°',color:C.rust,pos:'bottom'}],60,207,550,360,1.6,1);
 text(s,'A：北東（ΔX, ΔY）=（1, 1）',665,222,550,44,27,C.teal,true);
 eq(s,'ΔY / ΔX = 1 / 1 = 1',665,280,550,52,34,C.teal);
 text(s,'B：南西（ΔX, ΔY）=（−1, −1）',665,377,550,44,27,C.rust,true);
 eq(s,'ΔY / ΔX = (−1) / (−1) = 1',665,435,550,52,32,C.rust);
 takeaway(s,'同じ比でも、方向角は 45° と 225°。向きが180°違う。');
}
{
 const s=base('逆正接が返す角度の範囲','arctan は、tan が同じ値になる角度のうち、決められた範囲の角を返す。',
 '有限の実数rについて、α=arctan(r)の主値は−90°<α<90°。たとえばtan45°=tan225°=1だが、arctan1は45°を返す。同様にtan135°=tan315°=−1だがarctan(−1)は−45°を返す。arctanは全周の方向角を直接返す関数ではない。電卓のtanの逆関数を表すtan⁻¹は、この資料のarctanと同じ意味。1/tanを表すものではない。以後は度数法で計算する。');
 eq(s,'α = arctan(ΔY / ΔX)',65,211,1145,65,43);
 eq(s,'−90° < α < 90°',65,290,1145,60,43,C.teal);
 table(s,[['同じ tan の値になる方向角','比の値','arctan の答え α'],['45° と 225°','1','45°'],['135° と 315°','−1','−45°']],65,382,[550,220,375],59,28);
 takeaway(s,'α を求めたあと、元の座標差の符号で向きを確定する。');
}
{
 const s=base('象限の表は、向きを確定する手順','α = arctan(ΔY / ΔX) を求め、方向角 θ を 0°以上360°未満にそろえる。',
 '軸上でない場合の整理。第1象限はΔX>0かつΔY>0でθ=α。第2・第3象限はΔX<0なのでθ=α+180°。第4象限はΔX>0かつΔY<0でα<0なのでθ=α+360°。180°は正反対の向きへの補正、360°は同じ向きの表記を正にそろえる操作であり、意味が異なる。αは絶対値の比から得た鋭角ではなく、符号付きの比の逆正接である。絶対値を使う方位角表とは補正式を混用しない。軸上は7枚目で扱う。');
 table(s,[['象限・向き','ΔX','ΔY','α の例','加える角','θ の例'],['第1・北東','＋','＋','45°','0°','45°'],['第2・南東','−','＋','−45°','180°','135°'],['第3・南西','−','−','45°','180°','225°'],['第4・北西','＋','−','−45°','360°','315°']],65,220,[260,120,120,210,220,215],64,27);
 text(s,'180°：正反対の方向へ直す',65,557,550,39,27,C.rust,true);
 text(s,'360°：同じ向きを正の角度で表す',625,557,600,39,27,C.blue,true);
 takeaway(s,'南向き（ΔX < 0）なら180°。北西なら負の角に360°。');
}
{
 const s=base('計算例：同じ比でも、補正は異なる','南東と北西はいずれも ΔY / ΔX = −4 / 3。まず向きの見当をつける。',
 '説明用の座標差。南東AはΔX=−30m、ΔY=40m。北西BはΔX=30m、ΔY=−40m。α=arctan(−4/3)=−53.130102...°。AはΔX<0だからα+180=126.869897...°、Bは北西だからα+360=306.869897...°。表示は小数第2位に四捨五入。南東の角は90〜180°、北西の角は270〜360°に入ることを確認する。散布図の座標差単位はm。');
 text(s,'A：ΔX = −30 m、ΔY = ＋40 m',65,216,650,44,27,C.rust,true);
 eq(s,'α = arctan(−4/3) ≈ −53.13°',65,269,650,50,33);
 eq(s,'θ ≈ −53.13° + 180° = 126.87°',65,326,650,52,33,C.rust);
 text(s,'B：ΔX = ＋30 m、ΔY = −40 m',65,426,650,44,27,C.teal,true);
 eq(s,'θ ≈ −53.13° + 360° = 306.87°',65,481,650,52,33,C.teal);
 scatter(s,[{dx:-30,dy:40,label:'A 南東',color:C.rust,pos:'right'},{dx:30,dy:-40,label:'B 北西',color:C.teal,pos:'top'}],735,210,475,363,70,40);
 takeaway(s,'答えの角度が、座標差から予想した向きに入るか確かめる。');
}
{
 const s=base('トラバースでは、計算の向きで扱いが変わる','距離・方向角から座標差を求める場合と、その逆を区別する。',
 'トラバースの座標計算で、Lと0〜360°の方向角θが与えられていればΔX=Lcosθ、ΔY=Lsinθを直接計算する。cos・sinが象限に応じた符号を返すので、象限別の公式に分ける必要はない。例L=100m、θ=120°ならΔX=−50m、ΔY=86.60254...mで南東。逆に座標差から方向角を求める際は、比を作ると符号の組合せを失うためarctanの後に補正する。昔の関数表や鋭角だけを扱う手計算では、象限ごとに正負を付ける形で整理できるが、方向角全体のcos・sinを使う計算では不要。観測角から次の辺の方向角を求める漸化計算は別の段階で、0〜360°への正規化を行う。');
 text(s,'距離・方向角から座標差',65,215,660,46,31,C.blue,true);
 eq(s,'ΔX = L cos θ',65,282,650,52,39);
 eq(s,'ΔY = L sin θ',65,342,650,52,39);
 text(s,'cos・sin が正負も返す。',65,424,650,42,29,C.teal,true);
 text(s,'L = 100 m、θ = 120° の例',65,487,650,39,25);
 eq(s,'ΔX = −50 m,   ΔY ≈ 86.60 m',65,537,650,45,31);
 text(s,'座標差から方向角',775,215,440,46,31,C.blue,true);
 eq(s,'α = arctan(ΔY / ΔX)',775,285,440,52,32);
 text(s,'元の符号を確認し、',775,371,440,40,29);
 text(s,'必要なら180°か360°を加える。',775,420,440,40,26,C.rust,true);
 text(s,'atan2 なら、この判定も関数が行う。',775,510,440,64,24);
 takeaway(s,'象限分けが必要になるのは、主に「比から向きを戻す」とき。');
}
{
 const s=base('atan2 は、二つの座標差を別々に受け取る','比にする前の符号を使うため、全周の向きを求められる。',
 'atan2は2つの引数の符号を使って象限を判定する。Pythonではdegrees(atan2(ΔY, ΔX)) % 360で北から時計回りの方向角になる。数学でのatan2(y,x)のyに測量のΔY、xに測量のΔXを対応させる。Excelの関数はATAN2(x_num,y_num)で引数順が逆なので、B2=ΔX、C2=ΔYなら=MOD(DEGREES(ATAN2(B2,C2)),360)。ラジアンから度への変換を含む。関数によって負の角を返すため正規化が必要。ΔX=ΔY=0は同一点で方向を定められず、呼び出し前に検査する。Pythonの返り値が0になっても幾何学的に方向角が定まることは意味しない。軸上では比ΔY/ΔXを使わず向きを直接決める。出典：Python公式 math.atan2 https://docs.python.org/3/library/math.html#math.atan2 、Microsoft公式 ATAN2 https://support.microsoft.com/ja-jp/excel/functions/atan2-function （2026-10-15確認）。');
 text(s,'Excel の例：B2 に ΔX、C2 に ΔY',65,215,1140,44,29,C.blue,true);
 eq(s,'=MOD(DEGREES(ATAN2(B2,C2)),360)',65,276,1150,57,38);
 text(s,'引数の順序はソフトによって異なる。返り値を度に直し、0〜360°にそろえる。',65,347,1150,40,24);
 table(s,[['軸上の向き','北','東','南','西'],['ΔX','＋','0','−','0'],['ΔY','0','＋','0','−'],['方向角','0°','90°','180°','270°']],65,411,[280,215,215,215,220],43,25);
 takeaway(s,'ΔX = 0、ΔY = 0 のときは、方向角が定まらない。');
}
{
 const s=base('確認問題：比の計算前に、向きを予想する','各行について、向き・arctan の答え α・補正後の方向角 θ を求める。',
 '確認問題の解答。①ΔX=30、ΔY=40：北東、第1象限、α=53.130102...°、補正なし、θ=53.13°。②ΔX=−30、ΔY=40：南東、第2象限、α=−53.130102...°、180°を加えθ=126.87°。③ΔX=30、ΔY=−40：北西、第4象限、α=−53.130102...°、360°を加えθ=306.87°。②と③の比はいずれも−4/3だが方向角は180°異なる。数値の答えだけでなく、どの符号を見て補正したかを説明させる。最後に、arctanが使うのは一つの比、atan2が使うのは二つの座標差であることを確認する。');
 table(s,[['問題','ΔX [m]','ΔY [m]','向き','α','θ'],['①','＋30','＋40','？','？','？'],['②','−30','＋40','？','？','？'],['③','＋30','−40','？','？','？']],65,227,[140,180,180,215,215,215],72,29);
 text(s,'② と ③ は比が同じ。方向角も同じになるだろうか。',65,552,1140,43,30,C.blue,true);
 takeaway(s,'「どの象限か」から、「なぜその補正か」まで説明する。');
}

// 全象限・軸上・逆計算の数値を検算する。
const numerical=[];
for(const [dx,dy] of [[1,1],[-1,1],[-1,-1],[1,-1],[-30,40],[30,-40],[30,40],[1,0],[0,1],[-1,0],[0,-1]]){
 const expected=(Math.atan2(dy,dx)*180/Math.PI+360)%360;
 let actual;
 if(dx===0)actual=dy>0?90:270;
 else if(dy===0)actual=dx>0?0:180;
 else{actual=Math.atan(dy/dx)*180/Math.PI;if(dx<0)actual+=180;else if(dy<0)actual+=360;}
 if(Math.abs(actual-expected)>1e-10)throw Error('方向角の検算が一致しません');
 numerical.push({deltaX:dx,deltaY:dy,directionDegrees:actual});
}
await fs.writeFile(path.join(build,'numerical_check.json'),JSON.stringify(numerical,null,2));
await fs.writeFile(path.join(out,'講師用原稿.md'),'# 方向角と象限\n\n'+manuscript.map((a,i)=>`## ${i+1}. ${a.title}\n\n${a.sub}\n\n${a.notes}\n`).join('\n'));
const candidatePath=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(ppt)).save(candidatePath);
const finalPath=path.join(out,'方向角と象限_補足スライド.pptx');
const receipt=path.join(records,'final_validation_v3.json');
const result=await finalizePresentation({workspaceDir:root,candidatePath,finalPath,
 pythonExecutable:path.join(deps,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:8,requiredNativeTableOwnerSlides:[3,4,7,8],requiredNativeChartOwnerSlides:[1,2,5],materializeLiteralChartWorkbooks:true,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[3,4,7,8].flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'design',families:['Meiryo','Cambria Math']},verifyArtifactToolImport:true,receiptPath:receipt});
// 最終ファイルを読み直し、同じ内容から表示用画像・PDFを作る。
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(const [i,s] of final.slides.items.entries()){
 const blob=await final.export({slide:s,format:'png',scale:1.5});
 await fs.writeFile(path.join(previews,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
// PDFはPowerPointで出力する。COM利用不可の環境では同じ確認画像をPDF化する。
// 公開用の検証記録には個人プロファイルの絶対パスを残さない。
const report=receipt;
let raw=await fs.readFile(report,'utf8');
for(const variant of [root,root.replaceAll('\\','/')])raw=raw.replaceAll(JSON.stringify(variant).slice(1,-1),'.');
if(process.env.USERPROFILE)for(const variant of [process.env.USERPROFILE,process.env.USERPROFILE.replaceAll('\\','/')])raw=raw.replaceAll(JSON.stringify(variant).slice(1,-1),'<user-profile>');
await fs.writeFile(report,raw);
console.log(JSON.stringify({slides:8,pptx:path.relative(root,result.finalPath),pdfRequiresPowerPoint:true}));
