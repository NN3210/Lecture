// UTMの原点を説明する差し替え用1枚。本文・原点一覧は編集可能。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const deps=process.env.CODEX_RUNTIME_DEPENDENCIES||path.resolve(path.dirname(process.execPath),'../..');
const skill=process.env.PRESENTATION_SKILL;
if(!skill)throw Error('PRESENTATION_SKILLにPresentationsスキルのディレクトリを指定してください。');
process.env.RUNTIME_NODE_MODULES=path.join(deps,'node/node_modules');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(process.env.RUNTIME_NODE_MODULES,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const out=path.join(root,'materials/slides/第03回_測量の座標/UTM原点_修正版_20261015');
const build=path.join(root,'notes/utm_origin_20261015');
await fs.mkdir(build,{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const s=p.slides.add();s.background.fill='#FAF9F5';
const C={ink:'#153D50',blue:'#245989',muted:'#657781',accent:'#BD4A24'};
function text(str,x,y,w,h,size=24,color=C.ink,bold=false){
 const sh=s.shapes.add({geometry:'textbox',name:str.slice(0,40),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={typeface:'Meiryo',fontSize:size,color,bold,alignment:'left',verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};
 return sh;
}
text('測量の座標　3-3',52,15,650,25,18,C.muted);
text('UTMの原点：中央子午線と赤道の交点',52,54,1176,66,42,C.ink,true);
text('各帯に別々の原点がある。北半球では、その座標を E = 500,000 m、N = 0 m とする。',54,125,1170,40,25,C.blue);
text('日本にかかる6帯と、それぞれの投影原点',54,184,675,40,25,C.ink,true);
const rows=[['帯','経度の範囲（東経）','原点（緯度, 経度）'],...Array.from({length:6},(_,i)=>[String(51+i),`${120+6*i}°〜${126+6*i}°`,`0°, ${123+6*i}°E`])];
const t=s.tables.add({rows:7,columns:3,left:54,top:235,width:678,height:322,columnWidths:[72,284,322],values:rows});
t.borders.assign({fill:'#D7E2E1',width:0.7,style:'solid'});
for(let r=0;r<7;r++){
 t.rows[r].height=46;
 for(let c=0;c<3;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?'#153D50':r===4?'#E4F1EC':r%2?'#FFFFFF':'#F0F3F3';
  cell.text.style={typeface:'Meiryo',fontSize:23,color:r===0?'#FFFFFF':r===4?C.accent:C.ink,bold:r===0||r===4,alignment:c===0?'center':'left',verticalAlignment:'middle',insets:11,autoFit:'none'};
 }
}
text('帯広は第54帯。原点は赤道上の東経141°。',54,570,680,34,24,C.accent,true);
text('元の日本付近の図では、赤道は図の南側の外にある。',54,610,680,30,21,C.muted);
text('E：中央子午線を500,000 mにする',776,184,455,40,25,C.blue,true);
text('E = 中央子午線からの東西座標',776,239,455,33,24);
text('       ＋ 500,000 m（西側の負値を避ける）',776,272,455,33,21);
text('例：投影面上で西へ100 kmなら',776,313,455,31,23);
text('E = −100,000 + 500,000 = 400,000 m',776,348,455,34,22,C.blue,true);
text('縮尺係数0.9996：距離を少し縮める',776,405,455,36,25,C.blue,true);
text('中央子午線上の楕円体上1,000 mを',776,453,455,31,23);
text('平面上999.6 mにする（0.4 m短い）。',776,486,455,31,23);
text('帯全体の距離のひずみを抑えるため。',776,531,455,31,23);
text('平面直角座標系との比較：日本を19系に分け、各系の原点は (X, Y) = (0, 0)。',54,657,1175,27,21,C.muted);
text('中央子午線上の縮尺係数は0.9999、東西それぞれ約130 kmが適用範囲の目安。',54,687,1150,27,21,C.muted);
s.speakerNotes.text=await fs.readFile(path.join(out,'解説.md'),'utf8');
const candidatePath=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(out,'UTMの原点と座標の読み方.pptx');
if(!process.argv.includes('--preview-only'))await finalizePresentation({workspaceDir:root,candidatePath,finalPath,pythonExecutable:path.join(deps,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:1,requiredNativeTableOwnerSlides:[1],layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','1'],fontPolicy:{basis:'design',families:['Meiryo']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
await fs.writeFile(path.join(build,'preview.png'),new Uint8Array(await(await p.export({slide:s,format:'png',scale:1.5})).arrayBuffer()));
console.log(JSON.stringify({saved:finalPath}));
