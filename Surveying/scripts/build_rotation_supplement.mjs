// 点の回転と座標軸の回転を対比する、編集可能な2枚の補足スライド。
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第03回_測量の座標/補足_点と座標軸の回転_20261015');
const deps=path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const modules=process.env.ARTIFACT_MODULES||path.join(deps,'node/node_modules');
const skill=process.env.PRESENTATION_SKILL;
const python=process.env.RUNTIME_PYTHON||path.join(deps,'python/python.exe');
if(!skill||!process.env.MARP_MODULES)throw Error('PRESENTATION_SKILL と MARP_MODULES を指定してください。');
process.env.RUNTIME_NODE_MODULES=modules;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const req=createRequire(path.join(process.env.MARP_MODULES,'package.json'));
const katex=req('katex');
const C={bg:'#FAF9F5',navy:'#203E4C',teal:'#117E7A',gray:'#87959A',gold:'#AD763A'};
const build=path.join(out,'build');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(root,'notes/rotation_supplement'),{recursive:true});
const ppt=Presentation.create({slideSize:{width:1280,height:720}});
const maths={};
function text(s,str,x,y,w,h,size=28,color=C.navy,bold=false,font='Meiryo'){
  const sh=s.shapes.add({geometry:'textbox',name:str.slice(0,30),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=str;sh.text.style={typeface:font,fontSize:size,color,bold,alignment:'left',verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};return sh;
}
function math(s,tex,x,y,w,h,size=31,color=C.navy){
  const id=`EQM${String(Object.keys(maths).length).padStart(5,'0')}`;
  const html=katex.renderToString(tex,{output:'mathml',displayMode:true,throwOnError:true});
  maths[id]={tex,mathml:html.match(/<math[\s\S]*?<\/math>/)[0],display:true};
  const shape=text(s,id,x,y,w,h,size,color,false,'Cambria Math');shape.text.alignment='center';return shape;
}
function arrow(s,x1,y1,x2,y2,color,width=3){
  s.shapes.add({geometry:'connector',kind:'straight',position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.abs(x2-x1),height:Math.abs(y2-y1),horizontalFlip:x2<x1,verticalFlip:y2<y1},line:{fill:color,width},tail:{type:'triangle',width:'sm',length:'sm'}});
}
function point(s,x,y,color){s.shapes.add({geometry:'ellipse',name:'点',position:{left:x-6,top:y-6,width:12,height:12},fill:color,line:{fill:color,width:1}});}
function quarterArc(s,cx,cy,r,color){
  const k=0.55228475;
  s.shapes.add({geometry:'custom',name:'反時計回りの90度',position:{left:cx,top:cy-r,width:r,height:r},fill:'none',line:{fill:color,width:3},customPaths:[{width:r,height:r,commands:[{moveTo:{x:r,y:r}},{cubicBezTo:{x1:r,y1:r*(1-k),x2:r*k,y2:0,x:0,y:0}}]}]});
  const tx=cx+r*0.5,ty=cy-r*Math.sqrt(3)/2;
  s.shapes.add({geometry:'custom',name:'反時計回りの矢印',position:{left:tx,top:ty,width:16,height:12},fill:color,line:{fill:color,width:0},customPaths:[{width:16,height:12,commands:[{moveTo:{x:0,y:0}},{lineTo:{x:16,y:1}},{lineTo:{x:10,y:12}},{close:{}}]}]});
}
function diagram(s,active){
  const ox=982,oy=422,r=145;
  text(s,'θ = 90°、原点は固定',834,175,380,40,25,C.navy);
  arrow(s,830,oy,1195,oy,C.gray,2);
  arrow(s,ox,465,ox,229,C.gray,2);
  text(s,'x',1202,402,35,38,27,C.gray,false,'Cambria Math');
  text(s,'y',965,191,35,38,27,C.gray,false,'Cambria Math');
  text(s,'O',954,435,35,38,25,C.navy,false,'Cambria Math');
  if(active){
    point(s,ox+r,oy,C.gold);point(s,ox,oy-r,C.teal);
    text(s,'P (1, 0)',1046,440,175,43,28,C.gold,false,'Cambria Math');
    text(s,'P′ (0, 1)',841,246,145,43,28,C.teal,false,'Cambria Math');
    quarterArc(s,ox,oy,r,C.teal);
    text(s,'90°',1040,316,92,42,27,C.teal,false,'Cambria Math');
    text(s,'点が右から上へ移る',835,520,380,43,27,C.teal,true);
  }else{
    arrow(s,ox,oy,ox,229,C.teal,4);arrow(s,ox,oy,830,oy,C.teal,4);
    text(s,'x′',1002,228,58,40,31,C.teal,false,'Cambria Math');
    text(s,'y′',807,371,60,40,31,C.teal,false,'Cambria Math');
    point(s,ox+r,oy,C.navy);
    text(s,'P (1, 0)',1060,446,160,41,28,C.navy,false,'Cambria Math');
    quarterArc(s,ox,oy,75,C.teal);
    text(s,'90°',1047,314,90,40,27,C.teal,false,'Cambria Math');
    text(s,'新しい座標は (0, −1)',821,520,410,43,27,C.teal,true);
  }
}
for(const active of [true,false]){
  const s=ppt.slides.add();s.background.fill=C.bg;
  text(s,active?'点を反時計回りに回す':'座標軸を反時計回りに回す',64,42,1152,70,42,C.navy,true);
  text(s,active?'座標軸を固定し、点 P を原点のまわりに θ 回す。':'点 P を固定し、座標軸を原点のまわりに θ 回す。',67,117,1150,48,27);
  text(s,'r：原点からの距離　φ：元の x 軸から測った角度',70,170,720,28,22);
  math(s,'x=r\\cos\\phi,\\qquad y=r\\sin\\phi',65,204,700,47,31);
  text(s,active?'回転後の角度は φ + θ':'新しい x′ 軸から見た角度は φ − θ',70,253,730,45,27,C.teal,true);
  math(s,active?"x'=r\\cos(\\phi+\\theta)=x\\cos\\theta-y\\sin\\theta":"x'=r\\cos(\\phi-\\theta)=x\\cos\\theta+y\\sin\\theta",65,307,715,57,29);
  math(s,active?"y'=r\\sin(\\phi+\\theta)=x\\sin\\theta+y\\cos\\theta":"y'=r\\sin(\\phi-\\theta)=-x\\sin\\theta+y\\cos\\theta",65,367,715,57,29);
  math(s,active?'\\begin{pmatrix}x\'\\\\y\'\\end{pmatrix}=\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\\\sin\\theta&\\cos\\theta\\end{pmatrix}\\begin{pmatrix}x\\\\y\\end{pmatrix}':'\\begin{pmatrix}x\'\\\\y\'\\end{pmatrix}=\\begin{pmatrix}\\cos\\theta&\\sin\\theta\\\\-\\sin\\theta&\\cos\\theta\\end{pmatrix}\\begin{pmatrix}x\\\\y\\end{pmatrix}',75,451,690,120,34);
  diagram(s,active);
  if(!active)text(s,'原点も (x₀, y₀) に移す場合：x, y を x − x₀, y − y₀ に置き換える。',70,590,1140,45,25);
  text(s,active?'点の角度に θ を足すので、回転行列は R(θ)。':'軸が θ 回ると、点の相対角度は θ 減る。回転行列は R(−θ)。',70,648,1130,42,27,C.teal,true);
  s.speakerNotes.text=active?'通常の数学の座標系（x軸は右向き、y軸は上向き）。φはもとのx軸から点Pまでの反時計回りの角。rは原点から点までの距離。角度がφ+θになるので、三角関数の加法定理を適用する。x′,y′は、固定した同じ座標軸で表す回転後の点の座標。θ=90°、P=(1,0)ならP′=(0,1)。':'通常の数学の座標系（x軸は右向き、y軸は上向き）。点は動かさず、軸だけを反時計回りに回す。新しいx′軸から点までの角度はφ−θ。加法定理cos(φ−θ)=cosφcosθ+sinφsinθ、sin(φ−θ)=sinφcosθ−cosφsinθを使う。x′,y′は同じ点の新しい座標。図ではx′軸が上、y′軸が左なので、右側の点はy′が負になる。原点を(x₀,y₀)に移す場合は、先にu=x−x₀、v=y−y₀と置き、x′=u cosθ+v sinθ、y′=−u sinθ+v cosθ。R(−θ)=R(θ)の逆行列=R(θ)の転置。測量のX北・Y東・方向角の約束とは区別して説明する。';
}
const checks=[0,Math.PI/2,Math.PI/6,-Math.PI/3].map(theta=>{const c=Math.cos(theta),s=Math.sin(theta);const x=2,y=1;const xp=x*c-y*s,yp=x*s+y*c;const backX=xp*c+yp*s,backY=-xp*s+yp*c;if(Math.abs(backX-x)>1e-12||Math.abs(backY-y)>1e-12)throw Error('逆回転の検算不一致');return {theta,pointRotation:[xp,yp],restored:[backX,backY]};});
await fs.writeFile(path.join(build,'numerical_check.json'),JSON.stringify(checks,null,2));
await fs.writeFile(path.join(build,'maths.json'),JSON.stringify(maths,null,2));
if(!process.argv.includes('--finalize-only')){
  await(await PresentationFile.exportPptx(ppt)).save(path.join(build,'candidate.pptx'));
  console.log('2枚の候補とOffice数式変換用データを保存');
}else{
  const finalPath=path.join(out,'点の回転と座標軸の回転_図解.pptx');
  const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'native-math.pptx'),finalPath,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:2,layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Meiryo','Cambria Math']},verifyArtifactToolImport:false,receiptPath:path.join(root,'notes/rotation_supplement/validation_図解.json')});
  console.log(JSON.stringify({finalPath:result.finalPath}));
}
