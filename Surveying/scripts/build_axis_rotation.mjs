// 軸回転の式の導出を、編集可能な本文とOffice数式の素案で作成する。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第03回_測量の座標/軸回転の式導入');
const build=path.join(out,'build');
const modules=process.env.ARTIFACT_MODULES;
const katexModules=process.env.MARP_MODULES;
if(!modules||!katexModules)throw Error('ARTIFACT_MODULES と MARP_MODULES を指定してください。');
const req=createRequire(path.join(katexModules,'package.json'));
const katex=req('katex');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
await fs.mkdir(build,{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#FAF9F5',ink:'#213C4B',navy:'#153D50',teal:'#137D78',muted:'#657781',orange:'#AC492D'};
const maths={};let count=0;
const manuscript=[];
function text(s,value,x,y,w,h,size=29,color=C.ink,bold=false,align='left',font='Meiryo'){
  const shape=s.shapes.add({geometry:'textbox',name:`本文${s.shapes.items.length+1}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  shape.text=value;
  shape.text.style={typeface:font,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'word'};
  return shape;
}
function math(s,tex,y,{x=76,w=1128,h=78,size=40,color=C.navy,align='center'}={}){
  const token=`EQM${String(++count).padStart(5,'0')}`;
  const rendered=katex.renderToString(tex,{output:'mathml',displayMode:true,throwOnError:true,strict:false});
  maths[token]={tex,display:true,mathml:rendered.match(/<math[\s\S]*<\/math>/)[0]};
  const shape=text(s,token,x,y,w,h,size,color,false,align,'Cambria Math');
  shape.name=token;
  manuscript.at(-1).formulae.push(tex);
}
function slide(title,notes=''){
  const s=p.slides.add();s.background.fill=C.bg;
  text(s,title,68,58,1144,70,44,C.navy,true);
  text(s,String(p.slides.items.length).padStart(2,'0'),1140,675,72,28,18,C.muted,false,'right');
  s.speakerNotes.text=notes;
  manuscript.push({slide:p.slides.items.length,title,notes,formulae:[]});
  return s;
}
function body(s,value,y,{x=76,w=1128,h=58,size=29,color=C.ink,bold=false}={}){text(s,value,x,y,w,h,size,color,bold);}
function take(s,value){body(s,value,619,{h:52,size:27,color:C.teal,bold:true});}

{
 const s=p.slides.add();s.background.fill=C.bg;
 text(s,'測量学　第3回「測量の座標」補足',78,95,1124,52,28,C.teal);
 text(s,'軸回転の式の導出',72,236,1136,100,64,C.navy,true);
 text(s,'原点の移動と、反時計回りの座標軸の回転',80,363,1120,60,31,C.ink);
 text(s,'点の位置を保ったまま、新しい座標を求める',80,518,1120,50,28,C.muted);
 s.speakerNotes.text='添付画像と、このスレッドで説明した導出をもとにした補足教材。一般的な平面直交座標の約束として、x軸を右向き、y軸を上向き、角度を反時計回り正とする。日本の測量のX軸北向き・Y軸東向きや方向角の約束と混同しない。点そのものは移動させない。';
 manuscript.push({slide:1,title:'軸回転の式の導出',notes:s.speakerNotes.text,formulae:[]});
}
{
 const s=slide('同じ点を、新しい座標で読む','出典：ユーザー添付の座標変換の図（原図）。原図のQの新座標(1.54,2.33)は誤記。O′=(1,0.5)、θ=30度、Q=(1,3)からは(1.25,2.1650635…)となる。Pの新座標は原図と一致する。図は模式図として読む。');
 const b=await fs.readFile(path.join(out,'参考図_添付.png'));
 s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'原点を(1,0.5)へ移し、軸を30度回す参考図。Qの表示値は誤記のため下に訂正を記載。',fit:'contain',position:{left:60,top:140,width:775,height:510}});
 body(s,'もとの座標',176,{x:876,w:328,size:28,bold:true});
 math(s,'P=(3,2)',233,{x:860,w:344,h:66,size:33});
 body(s,'新しい原点と回転角',328,{x:876,w:328,size:25,bold:true});
 math(s,"O'=(1,0.5)",390,{x:860,w:344,h:68,size:32});
 math(s,'\\theta=30^\\circ',466,{x:860,w:344,h:68,size:34});
 body(s,'原図の Q の新座標を訂正：正しくは (1.25, 2.17)',648,{h:44,size:25,color:C.orange,bold:true});
}
{
 const s=slide('① 原点を移す','もとの原点Oから見たPとO′の座標を用意する。O′からPへのベクトルは、Pの位置ベクトルからO′の位置ベクトルを引いたもの。原点だけを移した座標を一時的に大文字X,Yで表し、軸回転と分けて計算する。');
 body(s,'新しい原点から点までの差を取る',162);
 math(s,"P=(x,y),\\qquad O'=(x_0,y_0)",242,{size:40});
 math(s,"\\overrightarrow{O'P}=\\begin{pmatrix}x-x_0\\\\y-y_0\\end{pmatrix}",348,{h:125,size:39});
 math(s,'X=x-x_0,\\qquad Y=y-y_0',499,{h:85,size:42,color:C.teal});
 take(s,'この段階では、軸の向きはもとのまま');
}
{
 const s=slide('② 新しい x′ 軸の向き','新しいx′軸はもとのx軸から反時計回りにθの方向を向く。この軸に沿って1だけ進むと、もとのx方向にはcosθ、y方向にはsinθ進む。したがって新しいx′軸の単位ベクトルは(cosθ,sinθ)。');
 body(s,'x′ 軸は、もとの x 軸から反時計回りに θ 回した方向',157,{size:28});
 math(s,"\\boldsymbol e_{x'}=\\begin{pmatrix}\\cos\\theta\\\\\\sin\\theta\\end{pmatrix}",252,{h:135,size:45});
 body(s,'x′ 軸に沿って 1 だけ進むときの、もとの軸方向の成分',419,{size:28});
 math(s,'x\\text{方向}:\\cos\\theta,\\qquad y\\text{方向}:\\sin\\theta',490,{h:82,size:38});
 take(s,'単位ベクトルで、新しい軸の向きを表す');
}
{
 const s=slide('③ 新しい y′ 軸の向き','y′軸はx′軸からさらに反時計回りに90度の方向。cos(θ+90度)=-sinθ、sin(θ+90度)=cosθを用いる。0<θ<90度ならy′軸は左上向きなので、横成分の符号は負、縦成分は正になる。');
 body(s,'y′ 軸は、もとの x 軸から θ + 90° の方向',157);
 math(s,"\\boldsymbol e_{y'}=\\begin{pmatrix}\\cos(\\theta+90^\\circ)\\\\\\sin(\\theta+90^\\circ)\\end{pmatrix}=\\begin{pmatrix}-\\sin\\theta\\\\\\cos\\theta\\end{pmatrix}",246,{h:150,size:42});
 math(s,'\\cos(\\theta+90^\\circ)=-\\sin\\theta',435,{h:70,size:36});
 math(s,'\\sin(\\theta+90^\\circ)=\\cos\\theta',513,{h:70,size:36});
 take(s,'0 < θ < 90° では左上向きなので、横成分が負になる');
}
{
 const s=slide('④ 同じベクトルを二通りに表す','新しい座標(x′,y′)は、x′軸とy′軸を基底としたベクトルの係数である。O′P=x′e_x′+y′e_y′と書き、もとの軸での成分(X,Y)と比較する。次の2枚ではこの連立方程式を解く。');
 math(s,"\\overrightarrow{O'P}=x'\\boldsymbol e_{x'}+y'\\boldsymbol e_{y'}",154,{h:80,size:39});
 math(s,"\\begin{pmatrix}X\\\\Y\\end{pmatrix}=x'\\begin{pmatrix}\\cos\\theta\\\\\\sin\\theta\\end{pmatrix}+y'\\begin{pmatrix}-\\sin\\theta\\\\\\cos\\theta\\end{pmatrix}",250,{h:135,size:40});
 body(s,'横方向と縦方向の成分を、それぞれ比較する',407,{size:29});
 math(s,"X=x'\\cos\\theta-y'\\sin\\theta\\qquad(1)",470,{h:65,size:39});
 math(s,"Y=x'\\sin\\theta+y'\\cos\\theta\\qquad(2)",546,{h:65,size:39});
}
{
 const s=slide('⑤ x′ の導出：y′ を消去する','式(1)をcosθ倍、式(2)をsinθ倍して加える。-y′sinθcosθと+y′cosθsinθが打ち消し合う。残ったx′(cos²θ+sin²θ)は三角関数の恒等式によりx′となる。');
 body(s,'式 (1) を cos θ 倍し、式 (2) を sin θ 倍して足す',154,{size:28});
 math(s,'X\\cos\\theta+Y\\sin\\theta',225,{h:62,size:37});
 math(s,"=(x'\\cos\\theta-y'\\sin\\theta)\\cos\\theta+(x'\\sin\\theta+y'\\cos\\theta)\\sin\\theta",301,{h:70,size:31});
 math(s,"=x'\\cos^2\\theta-y'\\sin\\theta\\cos\\theta+x'\\sin^2\\theta+y'\\cos\\theta\\sin\\theta",383,{h:70,size:33});
 math(s,"=x'(\\cos^2\\theta+\\sin^2\\theta)=x'",466,{h:72,size:39});
 math(s,"x'=X\\cos\\theta+Y\\sin\\theta",555,{h:78,size:44,color:C.teal});
}
{
 const s=slide('⑥ y′ の導出：x′ を消去する','式(1)を-sinθ倍、式(2)をcosθ倍して加える。-x′cosθsinθと+x′sinθcosθが打ち消し合う。残ったy′(sin²θ+cos²θ)はy′となる。x′の式と同じ恒等式を使う。');
 body(s,'式 (1) を −sin θ 倍し、式 (2) を cos θ 倍して足す',154,{size:28});
 math(s,'-X\\sin\\theta+Y\\cos\\theta',225,{h:62,size:37});
 math(s,"=-(x'\\cos\\theta-y'\\sin\\theta)\\sin\\theta+(x'\\sin\\theta+y'\\cos\\theta)\\cos\\theta",301,{h:70,size:31});
 math(s,"=-x'\\cos\\theta\\sin\\theta+y'\\sin^2\\theta+x'\\sin\\theta\\cos\\theta+y'\\cos^2\\theta",383,{h:70,size:33});
 math(s,"=y'(\\sin^2\\theta+\\cos^2\\theta)=y'",466,{h:72,size:39});
 math(s,"y'=-X\\sin\\theta+Y\\cos\\theta",555,{h:78,size:44,color:C.teal});
}
{
 const s=slide('⑦ 原点移動と軸回転を合わせる','X=x−x0、Y=y−y0を、導出したx′とy′の式に代入する。計算の順は、元の座標から新しい原点を引き、続いて軸回転の式を適用する。平面内の剛体的な座標系変更であり、長さの単位は共通とする。');
 math(s,'X=x-x_0,\\qquad Y=y-y_0',160,{h:90,size:39});
 body(s,'導出した式に代入する',282,{size:29});
 math(s,"x'=(x-x_0)\\cos\\theta+(y-y_0)\\sin\\theta",361,{h:92,size:43,color:C.teal});
 math(s,"y'=-(x-x_0)\\sin\\theta+(y-y_0)\\cos\\theta",465,{h:92,size:43,color:C.teal});
 take(s,'先に原点を引き、その差を新しい軸方向に分ける');
}
{
 const s=slide('符号の確認：軸を回すと、角度を引く','原点移動後のベクトルを極座標でX=r cosφ、Y=r sinφとする。軸をθ回すと、新しいx′軸から測る点の方向はφ−θになる。加法定理から同じ座標変換式を確認できる。θ=90度、X=1、Y=0ならx′=0、y′=−1となり、新しい軸では下側に位置する。点を回す能動回転とは符号の組合せが異なる。');
 math(s,'X=r\\cos\\varphi,\\qquad Y=r\\sin\\varphi',159,{h:82,size:38});
 math(s,"x'=r\\cos(\\varphi-\\theta)=X\\cos\\theta+Y\\sin\\theta",270,{h:90,size:38});
 math(s,"y'=r\\sin(\\varphi-\\theta)=-X\\sin\\theta+Y\\cos\\theta",376,{h:90,size:38});
 body(s,'例：もとの x 軸上の点を、90° 回した軸で読む',501,{size:28});
 math(s,"(X,Y)=(1,0),\\quad\\theta=90^\\circ\\qquad(x',y')=(0,-1)",560,{h:74,size:36,color:C.teal});
}
{
 const s=slide('計算例 P：原点を移して回転する','条件はP=(3,2)、O′=(1,0.5)、θ=30度。原点移動後は(X,Y)=(2,1.5)。cos30度=√3/2、sin30度=1/2を代入するとx′=√3+0.75=2.4820508…、y′=−1+3√3/4=0.2990381…。小数第2位へ丸める。');
 math(s,"P=(3,2),\\quad O'=(1,0.5),\\quad\\theta=30^\\circ",154,{h:78,size:37});
 math(s,'(X,Y)=(3-1,\\ 2-0.5)=(2,\\ 1.5)',245,{h:85,size:38});
 math(s,"x'=2\\frac{\\sqrt3}{2}+1.5\\frac12=\\sqrt3+0.75\\approx2.48",349,{h:105,size:37});
 math(s,"y'=-2\\frac12+1.5\\frac{\\sqrt3}{2}=-1+\\frac{3\\sqrt3}{4}\\approx0.30",465,{h:105,size:37});
 take(s,'新しい座標は (2.48, 0.30)');
}
{
 const s=slide('計算例 Q：同じ式で確かめる','条件はQ=(1,3)、O′=(1,0.5)、θ=30度。原点移動後は(X,Y)=(0,2.5)なので、x′=1.25、y′=5√3/4=2.1650635…。元画像の(1.54,2.33)は同じ条件を満たさない。原点O′からの距離は元も新も2.5で、1.25²+(5√3/4)²=6.25を確認できる。');
 math(s,"Q=(1,3),\\quad O'=(1,0.5),\\quad\\theta=30^\\circ",154,{h:78,size:37});
 math(s,'(X,Y)=(1-1,\\ 3-0.5)=(0,\\ 2.5)',245,{h:85,size:38});
 math(s,"x'=0\\frac{\\sqrt3}{2}+2.5\\frac12=1.25",349,{h:105,size:39});
 math(s,"y'=-0\\frac12+2.5\\frac{\\sqrt3}{2}=\\frac{5\\sqrt3}{4}\\approx2.17",465,{h:105,size:39});
 body(s,'新しい座標は (1.25, 2.17)。添付図の Q の表示を訂正',619,{h:52,size:26,color:C.orange,bold:true});
}
{
 const s=slide('行列での表現と逆変換','導出した2式を行列にまとめる。軸を反時計回りにθ回した座標の変換行列は、成分で見た点の回転行列R(−θ)に対応する。逆変換ではθの符号を反転し、最後に原点の座標を足す。回転行列の逆行列は転置行列であり、距離と角度を保つ。日本の測量の軸・方向角へ適用するときは、その約束に合わせて符号を確認する。');
 body(s,'もとの座標から、新しい座標へ',153,{size:29});
 math(s,"\\begin{pmatrix}x'\\\\y'\\end{pmatrix}=\\begin{pmatrix}\\cos\\theta&\\sin\\theta\\\\-\\sin\\theta&\\cos\\theta\\end{pmatrix}\\begin{pmatrix}x-x_0\\\\y-y_0\\end{pmatrix}",220,{h:145,size:38});
 body(s,'新しい座標から、もとの座標へ',400,{size:29});
 math(s,"\\begin{pmatrix}x\\\\y\\end{pmatrix}=\\begin{pmatrix}x_0\\\\y_0\\end{pmatrix}+\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\\\sin\\theta&\\cos\\theta\\end{pmatrix}\\begin{pmatrix}x'\\\\y'\\end{pmatrix}",470,{h:140,size:38});
 take(s,'逆変換は、回転を戻してから原点の座標を足す');
}

await fs.writeFile(path.join(build,'maths.json'),JSON.stringify(maths,null,2));
await fs.writeFile(path.join(out,'スライド原稿.json'),JSON.stringify(manuscript,null,2));
await fs.writeFile(path.join(build,'requirements.json'),JSON.stringify({explicitTotalSlideCount:p.slides.items.length,requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'design',families:['Meiryo','Cambria Math']},expectedSlideSizeEmu:'12192000,6858000'},null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
console.log(JSON.stringify({slides:p.slides.items.length,equations:count}));
