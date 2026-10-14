// 平均の誤差伝播の補足資料をMarkdownから再生成する。
// 環境変数 ARTIFACT_MODULES、PRESENTATION_SKILL、RUNTIME_PYTHON を指定する。
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out=path.join(root,'materials/slides/第02回_測量の基礎と誤差論/補足_平均の誤差伝播_20261014');
const outputStem='平均の誤差伝播_現場例追加_20261015';
const modules=process.env.ARTIFACT_MODULES;
const skill=process.env.PRESENTATION_SKILL;
if(!modules || !skill || !process.env.RUNTIME_PYTHON) throw new Error('READMEの環境変数を指定してください。');
process.env.RUNTIME_NODE_MODULES=modules;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const runtimeRequire=createRequire(path.join(modules,'package.json'));
const sharp=runtimeRequire('sharp');
const raw=await fs.readFile(path.join(out,'slides.md'),'utf8');
const pages=raw.replace(/^---[\s\S]*?---\s*/,'').split(/\n---\s*\n/);
const ppt=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#FAF8F2',navy:'#183E50',teal:'#137B78',gold:'#B2712E',ink:'#243C48',gray:'#64757D',line:'#D9E0DB'};
const F='Meiryo';
const tableOwners=[],chartOwners=[];
function text(slide,str,x,y,w,h,size=28,color=C.ink,bold=false,align='left'){
  const s=slide.shapes.add({geometry:'textbox',name:`text-${slide.shapes.items.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  // Meiryoの結合マクロンは右にずれるため、数式・欧文はArialで組版する。
  const parts=str.split(/([\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}。、「」（）]+)/u).filter(Boolean);
  s.text.style={typeface:F,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',autoFit:'none',wrap:'none',insets:0};
  s.text=[parts.map(part=>({run:part,style:{typeface:/[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u.test(part)?F:'Arial'}}))]; return s;
}
async function picture(slide,name,box){
  const b=await fs.readFile(path.join(out,'assets',name));
  slide.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:name==='survey_hero.png'?'測距のAI生成概念イラスト':'観測値と組平均の広がりのAI生成概念図',fit:'contain',position:box});
}
function table(slide,rows,y,h){
  const widths=rows[0].length===3?[550,270,300]:Array(rows[0].length).fill(1120/rows[0].length);
  const t=slide.tables.add({rows:rows.length,columns:rows[0].length,left:80,top:y,width:1120,height:h,columnWidths:widths,values:rows});
  t.borders.assign({fill:C.line,width:1,style:'solid'});
  for(let r=0;r<rows.length;r++){
    t.rows[r].height=h/rows.length;
    for(let c=0;c<rows[0].length;c++){
      const ce=t.getCell(r,c);ce.fill=r===0?C.navy:(r%2?'#FFFFFF':'#F0F3EF');
      ce.text.style={typeface:F,fontSize:rows[0].length>=5?24:25,color:r===0?'#FFFFFF':C.ink,bold:r===0,alignment:c===0?'left':'center',verticalAlignment:'middle',insets:10};
    }
  }
  return t;
}
function blocks(body){
  const lines=body.split('\n').map(s=>s.trim()).filter(Boolean), result=[];
  for(let i=0;i<lines.length;i++){
    const ln=lines[i];
    if(ln.startsWith('|')){
      const rows=[];while(i<lines.length&&lines[i].startsWith('|')){if(!/^\|[\s:|\-]+\|$/.test(lines[i]))rows.push(lines[i].split('|').slice(1,-1).map(s=>s.trim()));i++;}i--;result.push({type:'table',rows});
    }else if(ln.startsWith('> 式：'))result.push({type:'formula',value:ln.slice(4)});
    else if(ln.startsWith('> 要点：'))result.push({type:'take',value:ln.slice(5)});
    else if(!ln.startsWith('!['))result.push({type:'body',value:ln});
  }return result;
}
for(let i=0;i<pages.length;i++){
  const page=pages[i], slide=ppt.slides.add();slide.background.fill=C.bg;
  const title=page.match(/^#+ (.+)$/m)?.[1]||'';
  const notes=page.match(/<!-- notes: ([\s\S]*?) -->/)?.[1]||'';
  slide.speakerNotes.text=notes+(i>=4&&i<=17?'\n参考：JCGM 100:2008 4.2.2–4.2.3、5.1.2、5.2.2。https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf':'');
  const layout=page.match(/<!-- layout: (\w+) -->/)?.[1];
  const body=page.replace(/^#+ .+$/m,'').replace(/<!--[\s\S]*?-->/g,'');
  if(layout==='cover'){
    await picture(slide,'survey_hero.png',{left:0,top:0,width:1280,height:720});
    text(slide,'測量学 第2回 補足',435,60,760,44,25,C.navy);
    text(slide,title,435,117,790,85,62,C.navy,true);
    text(slide,'なぜ、平均のばらつきは',440,214,750,48,31,C.navy);
    text(slide,'√n で小さくなるのか',440,263,750,56,38,C.teal,true);
    text(slide,'AI生成の概念イラスト',980,681,260,22,14,C.navy,false,'right');
    continue;
  }
  text(slide,title,72,47,1136,76,40,C.navy,true);
  text(slide,String(i+1).padStart(2,'0'),1150,671,55,25,17,C.gray,false,'right');
  const bs=blocks(body);
  if(layout==='field_count'){
    const sc=JSON.parse(page.match(/<!-- scenario: (.*?) -->/)[1]);
    const nMin=Math.ceil((sc.sigma/sc.target)**2), ns=Array.from({length:12},(_,k)=>k+1);
    const sentences=bs.filter(b=>b.type==='body');
    text(slide,sentences[0].value,80,142,1120,40,27);
    text(slide,sentences[1].value,80,188,1120,40,27);
    text(slide,'平均の標準偏差（mm）',80,241,650,32,22,C.gray);
    const ch=slide.charts.add('line',{position:{left:70,top:280,width:730,height:310},categories:ns.map(String),series:[{name:'平均の標準偏差',values:ns.map(n=>Number((sc.sigma/Math.sqrt(n)).toPrecision(12))),fill:C.teal,line:{fill:C.teal,width:3}},{name:'目標 2 mm',values:ns.map(()=>sc.target),fill:C.gold,line:{fill:C.gold,width:2}}],hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:19}},lineOptions:{smooth:false},xAxis:{textStyle:{fontSize:19,fill:C.ink}},yAxis:{min:0,max:6,majorUnit:2,textStyle:{fontSize:20,fill:C.gray},majorGridlines:{fill:C.line,width:1}},chartFill:C.bg,plotAreaFill:C.bg});
    applyPresentationChartFont(ch,{fontFamily:F});chartOwners.push(i+1);
    text(slide,'測定回数 n（回）',550,578,250,30,21,C.gray,false,'right');
    const equations=bs.filter(b=>b.type==='formula');
    equations.forEach((b,k)=>text(slide,b.value,855,271+k*56,350,50,32,C.navy,true));
    text(slide,`${nMin}回以上`,850,459,350,80,57,C.teal,true);
    text(slide,'独立・同精度、偏り補正済みの例。2 mmは最大誤差を保証する値ではない。',80,606,1120,30,21,C.gray);
    text(slide,bs.find(b=>b.type==='take').value,80,646,1120,35,26,C.teal,true);
    continue;
  }
  if(layout==='field_time'){
    const sentences=bs.filter(b=>b.type==='body');
    text(slide,sentences[0].value,80,142,1120,42,28);
    text(slide,sentences[1].value,80,189,1120,42,28);
    const rows=bs.find(b=>b.type==='table').rows;
    const t=table(slide,rows,255,232);tableOwners.push(i+1);
    for(let c=0;c<rows[0].length;c++) {t.getCell(2,c).fill='#DCEFE9';t.getCell(2,c).text.bold=true;}
    text(slide,bs.find(b=>b.type==='formula').value,80,515,1120,50,31,C.navy,true);
    text(slide,'時間は観測のみ。準備・器械設置・点検の時間は別途見込む。',80,581,1120,35,23,C.gray);
    text(slide,bs.find(b=>b.type==='take').value,80,631,1120,45,27,C.teal,true);
    continue;
  }
  if(layout==='targets'){
    text(slide,'1回ずつの測定値',300,145,360,42,28,C.teal,true,'center');
    text(slide,'4回ずつ測った平均値',630,145,360,42,28,C.gold,true,'center');
    await picture(slide,'mean_targets.png',{left:70,top:196,width:1140,height:365});
    text(slide,'概念図。同じ尺度で比較。右の各点は、別々の4回分の組の平均。',80,572,1120,30,21,C.gray);
    text(slide,bs.find(b=>b.type==='take').value,80,625,1120,45,27,C.teal,true);continue;
  }
  if(layout==='chart'){
    text(slide,'1回の標準偏差 τ = 4 mm の理論例',80,141,1120,42,28);
    const chart=slide.charts.add('bar',{position:{left:80,top:215,width:720,height:365},categories:['1回','4回','9回','16回'],series:[{name:'平均の標準偏差（mm）',values:[4,2,1.3333333333333,1],fill:C.teal}],hasLegend:false,barOptions:{direction:'column',gapWidth:160},xAxis:{textStyle:{fontSize:24,fill:C.ink}},yAxis:{min:0,max:5,majorUnit:1,numberFormatCode:'0',textStyle:{fontSize:22,fill:C.gray},majorGridlines:{fill:C.line,width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00',textStyle:{fontSize:24,fill:C.ink}},chartFill:C.bg,plotAreaFill:C.bg});
    applyPresentationChartFont(chart,{fontFamily:F});chartOwners.push(i+1);
    text(slide,'標準偏差（mm）',88,190,330,30,21,C.gray);
    text(slide,'SD(x̄) = 4/√n mm',850,260,360,55,31,C.teal,true);
    text(slide,'4回で 1/2',855,350,330,50,34,C.navy,true);
    text(slide,'16回で 1/4',855,415,330,50,34,C.navy,true);
    text(slide,bs.find(b=>b.type==='take').value,80,620,1120,50,27,C.teal,true);continue;
  }
  const main=bs.filter(b=>b.type!=='take');
  let heights=main.map(b=>b.type==='table'?b.rows.length*48:b.type==='formula'?65:43);
  const total=heights.reduce((a,b)=>a+b,0)+(main.length-1)*10;
  const scale=Math.min(1,455/total);let y=150;
  for(let j=0;j<main.length;j++){
    const b=main[j],h=heights[j]*scale;
    if(b.type==='table'){table(slide,b.rows,y,h);tableOwners.push(i+1);}
    else text(slide,b.value,b.type==='formula'?95:80,y,b.type==='formula'?1090:1120,h,b.type==='formula'?(b.value.length>57?29:b.value.length>43?32:37):27,b.type==='formula'?C.navy:C.ink,b.type==='formula');
    y+=h+10*scale;
  }
  const take=bs.find(b=>b.type==='take');if(take)text(slide,take.value,80,620,1120,49,take.value.length>43?25:27,C.teal,true);
}
await fs.mkdir(path.join(out,'build'),{recursive:true});await fs.mkdir(path.join(out,'preview'),{recursive:true});
const candidate=path.join(out,'build/candidate.pptx');
if(!process.argv.includes('--finalize-only')) {
await(await PresentationFile.exportPptx(ppt)).save(candidate);
console.log(`PPTX候補を保存：${pages.length}枚`);
// 数値例の独立な検算。
const values=[30,30.002,30.004,30.006,30.008],mean=values.reduce((a,b)=>a+b,0)/values.length;
const ss=values.reduce((s,x)=>s+((x-mean)*1000)**2,0),sigma=Math.sqrt(ss/4),sem=sigma/Math.sqrt(5);
if(Math.abs(mean-30.004)>1e-10||Math.abs(ss-40)>1e-7||Math.abs(sem-Math.sqrt(2))>1e-8)throw new Error('数値例の検算不一致');
const fieldScenarios=[3,2,1].map(target=>{const n=Math.ceil((6/target)**2);return {target_mm:target,n,seconds:n*30,sem_mm:6/Math.sqrt(n)};});
if(JSON.stringify(fieldScenarios.map(v=>v.n))!=='[4,9,36]'||6/Math.sqrt(8)<=2||Math.ceil((6/2.5)**2)!==6)throw new Error('現場例の必要回数が不一致');
await fs.writeFile(path.join(out,'build/numerical_check.json'),JSON.stringify({mean,sumSquares_mm2:ss,sigma_mm:sigma,sem_mm:sem,quiz:[6/Math.sqrt(9),(6/1)**2],fieldScenarios},null,2));
for(let i=0;i<ppt.slides.items.length;i++){
  const blob=await ppt.export({slide:ppt.slides.items[i],format:'png',scale:1.5});
  await fs.writeFile(path.join(out,`preview/slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
  console.log(`描画 ${i+1}/${pages.length}`);
}
// 俯瞰用画像。個別PNGも確認対象として保存する。
const thumbs=[];for(let i=0;i<pages.length;i++){thumbs.push({input:await sharp(path.join(out,`preview/slide-${String(i+1).padStart(2,'0')}.png`)).resize(384,216).png().toBuffer(),left:(i%4)*384,top:Math.floor(i/4)*216});}
await sharp({create:{width:1536,height:Math.ceil(pages.length/4)*216,channels:3,background:C.bg}}).composite(thumbs).png().toFile(path.join(out,'preview/overview.png'));
// この環境ではartifact-toolのPDF用標準フォント別名が未解決のため、
// 確認済みの高解像度スライドPNGをPDFに埋め込む。PPTXは編集可能のまま。
const {PDFDocument}=runtimeRequire('pdf-lib');
const pdf=await PDFDocument.create();
pdf.setTitle('平均の誤差伝播：測量学 第2回 補足');pdf.setCreator('Surveying teaching materials');
for(let i=0;i<pages.length;i++){
  const im=await pdf.embedPng(await fs.readFile(path.join(out,`preview/slide-${String(i+1).padStart(2,'0')}.png`)));
  const p=pdf.addPage([960,540]);p.drawImage(im,{x:0,y:0,width:960,height:540});
}
await fs.writeFile(path.join(out,`${outputStem}.pdf`),await pdf.save());
}
const final=path.join(out,`${outputStem}.pptx`);
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[F,'Arial']},verifyArtifactToolImport:true,receiptPath:path.join(root,'notes/.mean_error_validation.json')});
// オフライン閲覧用。矢印キー、クリック、印刷に対応。
const html=`<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>平均の誤差伝播</title><style>body{margin:0;background:#183e50;color:white;font:18px sans-serif}main{max-width:1280px;margin:auto}img{display:block;width:100%;margin:30px 0}nav{position:fixed;bottom:12px;right:16px;background:#183e50;padding:10px}a{color:white}@media print{body{background:white}img{margin:0;break-after:page}nav{display:none}@page{size:landscape;margin:0}}</style><main>${pages.map((_,i)=>`<img id="s${i+1}" src="preview/slide-${String(i+1).padStart(2,'0')}.png" alt="スライド${i+1}">`).join('')}</main><nav><a href="平均の誤差伝播_補足スライド.pptx">PowerPoint</a> / <a href="平均の誤差伝播_補足スライド.pdf">PDF</a></nav><script>let i=1;document.onkeydown=e=>{if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){i=Math.min(${pages.length},i+1);e.preventDefault()}if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){i=Math.max(1,i-1);e.preventDefault()}document.getElementById('s'+i).scrollIntoView()};</script></html>`;
await fs.writeFile(path.join(out,'slides.html'),html.replaceAll('平均の誤差伝播_補足スライド',outputStem));
console.log('完了：PPTX / PDF / HTML');
