// 分散の定義と導出の原稿から、編集可能な補足スライドを作る。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第02回_測量の基礎と誤差論/補足_分散の定義と導出_20261015');
const build=path.join(out,'build');
const modules=process.env.ARTIFACT_MODULES,skill=process.env.PRESENTATION_SKILL;
const python=process.env.RUNTIME_PYTHON,katexPath=process.env.KATEX_MODULE;
if(!modules||!skill||!python||!katexPath)throw Error('READMEの実行環境変数を指定してください。');
process.env.RUNTIME_NODE_MODULES=modules;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const {default:katex}=await import(pathToFileURL(katexPath));
await fs.mkdir(build,{recursive:true});
const records=path.join(root,'notes/variance_derivation_20261015');
await fs.mkdir(records,{recursive:true});
const finalPath=path.join(out,'分散の定義と導出_補足スライド.pptx');
const C={bg:'#FAF8F2',navy:'#183E50',ink:'#243C48',teal:'#137B78',gray:'#64757D',line:'#D9E0DB'};
const maths={};
function text(s,str,y,h,size=28,color=C.ink,bold=false,x=80,w=1120,font='Meiryo'){
 const sh=s.shapes.add({geometry:'textbox',name:str.slice(0,48),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={typeface:font,fontSize:size,color,bold,alignment:'left',verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};return sh;
}
const p=Presentation.create({slideSize:{width:1280,height:720}});
const raw=await fs.readFile(path.join(out,'slides.md'),'utf8');
const pages=raw.replace(/^---[\s\S]*?---\s*/,'').split(/\n---\s*\n/);
const tableOwners=[];
for(const [index,page] of pages.entries()){
 const s=p.slides.add();s.background.fill=C.bg;
 const title=page.match(/^## (.+)$/m)[1];
 text(s,title,44,78,38,C.navy,true,72,1136);
 text(s,`${index+1} / ${pages.length}`,677,23,16,C.gray,false,1130,90);
 s.speakerNotes.text=page.match(/<!-- notes: ([\s\S]*?) -->/)[1];
 const lines=page.replace(/^## .+$/m,'').replace(/<!--[\s\S]*?-->/g,'').split('\n').map(l=>l.trim()).filter(Boolean);
 const blocks=[];let take='';
 for(let k=0;k<lines.length;k++){
  const l=lines[k];
  if(l.startsWith('> 要点：')){take=l.slice(5);continue;}
  if(l.startsWith('|')){
   const rows=[];
   while(k<lines.length&&lines[k].startsWith('|')){if(!/^\|[\s:|\-]+\|$/.test(lines[k]))rows.push(lines[k].split('|').slice(1,-1).map(c=>c.trim()));k++;}k--;
   blocks.push({type:'table',rows,height:162});
  }else if(l.startsWith('$$'))blocks.push({type:'math',value:l.slice(2,-2),height:/\\frac|\\sqrt/.test(l)?100:78});
  else blocks.push({type:'body',value:l,height:45});
 }
 const total=blocks.reduce((a,b)=>a+b.height,0),gap=(450-total)/Math.max(1,blocks.length-1);let y=146;
 for(const b of blocks){
  if(b.type==='body')text(s,b.value,y,b.height,26);
  if(b.type==='math'){
   const id=`EQM${String(Object.keys(maths).length).padStart(5,'0')}`;
   const html=katex.renderToString(b.value,{output:'mathml',displayMode:true,throwOnError:true});
   maths[id]={tex:b.value,mathml:html.match(/<math[\s\S]*?<\/math>/)[0],display:true};
   const sh=text(s,id,y,b.height,b.value.length>105?33:37,C.navy,false,80,1120,'Cambria Math');sh.text.alignment='center';
  }
  if(b.type==='table'){
   tableOwners.push(index+1);
   const t=s.tables.add({rows:b.rows.length,columns:4,left:80,top:y,width:1120,height:b.height,columnWidths:[484,212,212,212],values:b.rows});
   t.borders.assign({fill:C.line,width:1,style:'solid'});
   for(let r=0;r<b.rows.length;r++){
    t.rows[r].height=b.height/b.rows.length;
    for(let c=0;c<4;c++){
     const ce=t.getCell(r,c);ce.fill=r===0?C.navy:r%2?'#FFFFFF':'#F0F3EF';
     ce.text.style={typeface:'Meiryo',fontSize:25,color:r===0?'#FFFFFF':C.ink,bold:r===0,alignment:c===0?'left':'center',verticalAlignment:'middle',insets:10};
    }
   }
  }
  y+=b.height+gap;
 }
 text(s,take,627,51,26,C.teal,true);
}
if(!process.argv.includes('--finalize-only')){
 await(await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
 await fs.writeFile(path.join(build,'maths.json'),JSON.stringify(maths,null,2));
 const run=spawnSync(python,[path.join(root,'scripts/patch_session03_math.py'),'native-math.pptx',out],{encoding:'utf8',env:{...process.env,PYTHONIOENCODING:'utf-8'}});
 if(run.status!==0)throw Error(run.stderr||run.stdout);console.log(run.stdout.trim());
}
if(!process.argv.includes('--draft')){
 await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'native-math.pptx'),finalPath,pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:5,requiredNativeTableOwnerSlides:tableOwners,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
 fontPolicy:{basis:'design',families:['Meiryo','Cambria Math']},verifyArtifactToolImport:true,
 receiptPath:path.join(records,`validation-${Date.now()}.json`)});
 // 公開する検証記録からローカル個人プロファイルの絶対パスを除く。
 for(const name of await fs.readdir(records)){
  if(!name.endsWith('.json'))continue;
  const filename=path.join(records,name);let content=await fs.readFile(filename,'utf8');
  if(process.env.USERPROFILE)for(const variant of [process.env.USERPROFILE,process.env.USERPROFILE.replaceAll('\\','/')])
   content=content.replaceAll(JSON.stringify(variant).slice(1,-1),'<user-profile>');
  await fs.writeFile(filename,content);
 }
 console.log('検証済みPPTXを保存');
}
