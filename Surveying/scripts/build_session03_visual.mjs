// 第3回のMarkdown正本から、編集可能な本文・表を持つPPTXを生成する。
// 数式はKaTeX MathMLを経由して、後段のpatch_session03_math.pyでOffice数式に変換。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
process.on('uncaughtException', e=>{console.error(e.message+'\n'+e.stack?.split('\n').slice(-8).join('\n'));process.exit(1)});
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第03回_測量の座標');
const build=path.join(out,'build');
const modules=process.env.ARTIFACT_MODULES;
const marpModules=process.env.MARP_MODULES;
if(!modules||!marpModules)throw Error('ARTIFACT_MODULES と MARP_MODULES を指定してください。');
const req=createRequire(path.join(modules,'package.json'));
const mreq=createRequire(path.join(marpModules,'package.json'));
const sharp=req('sharp'),katex=mreq('katex');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
await fs.mkdir(build,{recursive:true});
const raw=await fs.readFile(path.join(out,'slides.md'),'utf8');
const pages=raw.replace(/^---[\s\S]*?\n---\s*/,'').split(/\n---\s*\n/);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#FAF9F5',ink:'#213C4B',navy:'#153D50',teal:'#137D78',gray:'#657781',line:'#D7E2E1',white:'#FFFFFF'};
const maths={},layouts=[],tableOwners=[];
let eqId=0;
function mathToken(tex,display=false){
  const id=`EQM${String(++eqId).padStart(5,'0')}`;
  const mathml=katex.renderToString(tex,{output:'mathml',displayMode:display,throwOnError:true,strict:false});
  maths[id]={tex,display,mathml:mathml.match(/<math[\s\S]*<\/math>/)[0]};
  return id;
}
function runs(str,size=28,color=C.ink,bold=false){
  const result=[];let pos=0;
  for(const m of str.matchAll(/\$([^$]+)\$|\*\*(.*?)\*\*/g)){
    if(m.index>pos) result.push({run:str.slice(pos,m.index),style:{typeface:'Meiryo',fontSize:`${size}px`,color,bold}});
    if(m[2]!==undefined)result.push(...runs(m[2],size,C.teal,true));
    else result.push({run:mathToken(m[1]),style:{typeface:'Cambria Math',fontSize:`${size}px`,color,bold}});
    pos=m.index+m[0].length;
  }
  if(pos<str.length)result.push({run:str.slice(pos),style:{typeface:'Meiryo',fontSize:`${size}px`,color,bold}});
  return result.length?result:[{run:' ',style:{typeface:'Meiryo',fontSize:`${size}px`}}];
}
function text(slide,str,x,y,w,h,size=28,color=C.ink,bold=false,align='left',name=''){
  const s=slide.shapes.add({geometry:'textbox',name:name||`本文${slide.shapes.items.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  s.text.style={typeface:'Meiryo',fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',autoFit:'none',wrap:'word',insets:0};
  s.text=[runs(str,size,color,bold)]; return s;
}
function cleanMeasure(s){return s.replace(/\$([^$]+)\$/g,(_,v)=>v.replace(/\\(?:frac|dfrac)\{([^}]+)\}\{([^}]+)\}/g,'($1)/($2)').replace(/\\[a-zA-Z]+/g,'W').replace(/[{}_^]/g,'')).replace(/\*\*/g,'');}
function units(s){return [...cleanMeasure(s)].reduce((n,c)=>n+(/[\x00-\x7f]/.test(c)?0.54:1),0);}
function lines(s,w,size){return Math.max(1,Math.ceil(units(s)*size/(w-14)));}
function blockHeight(b,w,size){
  if(b.type==='math'){
    const rows=(b.value.match(/\\\\/g)||[]).length+1;
    return /[bp]matrix/.test(b.value)?Math.max(140,rows*38):Math.max(72,rows*56)+(b.value.includes('frac')?16:0)+(b.value.includes('sum_')?34:0);
  }
  if(b.type==='table')return tableDims(b,w,size).heights.reduce((a,c)=>a+c,0);
  return lines(b.value,w-(b.type==='bullet'?24:0),size)*size*1.5+8;
}
function parse(body){
  const arr=body.split('\n'), bs=[];
  for(let i=0;i<arr.length;i++){
    let l=arr[i].trim();if(!l)continue;
    if(l==='$$'){let v=[];while(++i<arr.length&&arr[i].trim()!=='$$')v.push(arr[i]);bs.push({type:'math',value:v.join('\n')});}
    else if(l.startsWith('|')){
      let rows=[];
      while(i<arr.length&&arr[i].trim().startsWith('|')){
        l=arr[i].trim();if(!/^\|[\s:\-|]+\|$/.test(l))rows.push(l.split('|').slice(1,-1).map(v=>v.trim()));i++;
      }i--;bs.push({type:'table',rows});
    }else if(l.startsWith('![')){const m=l.match(/!\[(.*?)\]\((.*?)\)/);bs.push({type:'image',alt:m[1],src:m[2]});}
    else if(l.startsWith('> '))bs.push({type:'take',value:l.slice(2)});
    else if(/^[-*] /.test(l))bs.push({type:'bullet',value:l.slice(2)});
    else bs.push({type:'body',value:l.replace(/^### /,'')});
  }return bs;
}
function tableDims(b,w,size){
  const count=b.rows[0].length;
  const weights=count===2?[0.37,0.63]:count===3?[0.24,0.38,0.38]:Array(count).fill(1/count);
  // 解答表の根拠は右列に幅を取る。
  if(count===3&&b.rows[0][0]==='問'){weights[0]=.09;weights[1]=.19;weights[2]=.72;}
  if(count===3&&b.rows[0][2].includes('結果')){weights[0]=.19;weights[1]=.58;weights[2]=.23;}
  if(count===2&&b.rows[0][0]==='選択肢'){weights[0]=.25;weights[1]=.75;}
  if(count===2&&b.rows[0][0]==='出典'){weights[0]=.42;weights[1]=.58;}
  if(count===3&&b.rows[0][0]==='記号'){weights[0]=.12;weights[1]=.29;weights[2]=.59;}
  const widths=weights.map(v=>v*w);
  const heights=b.rows.map((r,ri)=>Math.max(ri?56:48,...r.map((v,c)=>lines(v,widths[c]-28,size)*size*1.45+22+(v.includes('frac')||v.includes('sqrt')?14:0))));
  return {widths,heights};
}
function addTable(slide,b,x,y,w,size){
  const {widths,heights}=tableDims(b,w,size),h=heights.reduce((a,c)=>a+c,0);
  const t=slide.tables.add({rows:b.rows.length,columns:b.rows[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values:b.rows.map(r=>r.map(v=>v.replace(/\*\*/g,'')))});
  t.borders.assign({fill:C.line,width:.65,style:'solid'});
  for(let r=0;r<b.rows.length;r++){
    t.rows[r].height=heights[r];
    for(let c=0;c<b.rows[0].length;c++){
      const cell=t.getCell(r,c);cell.fill=r===0?C.navy:(r%2?C.white:'#EEF4F1');
      cell.text.style={typeface:'Meiryo',fontSize:size,color:r===0?C.white:C.ink,bold:r===0,verticalAlignment:'middle',alignment:'left',insets:12,autoFit:'none'};
      cell.value=[runs(b.rows[r][c],size,r===0?C.white:C.ink,r===0)];
    }
  }return h;
}
async function picture(slide,b,box){
  const src=path.join(out,b.src.replace(/\.svg$/,'.png'));
  const buf=await fs.readFile(src);
  slide.images.add({blob:buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength),contentType:'image/png',alt:b.alt,fit:'contain',position:box});
}
function equation(slide,b,x,y,w,h,size=37){
  const token=mathToken(b.value,true);
  const s=text(slide,token,x,y,w,h,size,C.navy,false,'center',token);
  return s;
}
function drawBlock(slide,b,x,y,w,size){
  if(b.type==='table')return addTable(slide,b,x,y,w,size);
  const h=blockHeight(b,w,size);
  if(b.type==='math')equation(slide,b,x,y,w,h,Math.min(39,size+8));
  else text(slide,(b.type==='bullet'?'•  ':'')+b.value,x,y,w,h,size);
  return h;
}
for(let i=0;i<pages.length;i++){
  const n=i+1,page=pages[i];const slide=p.slides.add();slide.background.fill=C.bg;
  const allNotes=[...page.matchAll(/<!--([\s\S]*?)-->/g)].map(m=>m[1]).join('\n');slide.speakerNotes.text=allNotes;
  const title=page.match(/^#+ (.+)$/m)[1];
  const content=page.replace(/^#+ .+$/m,'').replace(/<!--[\s\S]*?-->/g,'');
  const bs=parse(content),img=bs.find(b=>b.type==='image'),take=bs.find(b=>b.type==='take');
  const body=bs.filter(b=>!['image','take'].includes(b.type));
  if(n===1){
    await picture(slide,img,{left:0,top:0,width:1280,height:720});
    text(slide,'測量学 第3回',74,51,900,46,29,C.navy);
    text(slide,title,70,105,1130,100,76,C.navy,true);
    text(slide,'位置を表す約束と、距離・角からの座標計算',76,197,1120,44,27,C.navy);
    text(slide,'AI生成の概念イラスト',950,676,270,22,16,C.navy,false,'right');
    layouts.push({slide:n,layout:'cover'});continue;
  }
  const sec=title.match(/^(3-[\dQ])\s+(.*)$/);
  const heading=sec?sec[2]:title;
  text(slide,sec?`測量の座標　${sec[1]}`:'測量の座標　資料',65,28,1100,28,17,C.gray);
  const titleSize=units(heading)>30?34:40;
  text(slide,heading,63,68,1154,62,titleSize,C.navy,true);
  text(slide,String(n).padStart(2,'0'),1150,677,65,24,17,C.gray,false,'right');
  if(take)text(slide,take.value,68,632,1125,58,23,C.teal,true);
  const bottom=take?617:653;
  let size=n===7?26:28,y=154,layout='text';
  // 絵のあるページは、既存の説明図を大きく使い、本文を短くする。
  if(img){
    layout='figure';
    const isPhoto=img.src.includes('illustrations');
    if(isPhoto && ![38].includes(n)){
      const w=458;size=29;const gap=17;
      const total=body.reduce((a,b)=>a+blockHeight(b,w,size)+gap,0);
      let ty=176+Math.max(0,(bottom-176-total)/2);
      for(const b of body)ty+=drawBlock(slide,b,66,ty,w,size)+gap;
      await picture(slide,img,{left:550,top:157,width:675,height:bottom-157});
    }else{
      size=26;let ty=y;
      for(const b of body)ty+=drawBlock(slide,b,68,ty,1144,size)+10;
      const imY=body.length?ty+5:145;
      await picture(slide,img,{left:62,top:imY,width:1156,height:bottom-imY});
      y=ty;
    }
  }else{
    // 表や連立式に必要な高さを先に確保する。
    const w=1144;
    let gap=n===3||n===81?10:18;
    const need=sz=>body.reduce((a,b)=>a+blockHeight(b,w,sz)+gap,0)-gap;
    while(need(size)>bottom-y&&size>24)size--;
    const required=need(size);
    if(required>bottom-y+2)layouts.push({slide:n,warning:'本文の高さを要確認',required,available:bottom-y});
    // 数式中心は余白を上下に配り、上端への密集を避ける。
    if(body.length<=5 && required<bottom-y-55)y+=Math.min(52,(bottom-y-required)/3);
    for(const b of body){y+=drawBlock(slide,b,68,y,w,size)+gap;if(b.type==='table')tableOwners.push(n);}
  }
  layouts.push({slide:n,layout,fontSize:size,contentBottom:y,hasImage:!!img});
}
await fs.writeFile(path.join(build,'maths.json'),JSON.stringify(maths,null,2));
await fs.writeFile(path.join(build,'layout-plan.json'),JSON.stringify(layouts,null,2));
await fs.writeFile(path.join(build,'requirements.json'),JSON.stringify({explicitTotalSlideCount:81,requiredNativeTableOwnerSlides:[...new Set(tableOwners)],fontPolicy:{basis:'design',families:['Meiryo','Cambria Math']},expectedSlideSizeEmu:'12192000,6858000'},null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
console.log(JSON.stringify({slides:pages.length,equations:eqId,tables:tableOwners.length,warnings:layouts.filter(x=>x.warning)}));
