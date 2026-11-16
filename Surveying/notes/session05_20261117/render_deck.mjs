import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const { chromium }=require('playwright');
import { readFile,writeFile,mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath,pathToFileURL } from 'node:url';
const N=path.dirname(fileURLToPath(import.meta.url));
const O=path.resolve(N,'../../materials/slides/第05回_トラバース測量I/改3');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
const page=await browser.newPage({viewport:{width:1600,height:900},deviceScaleFactor:1});
// Managed Chromium blocks file:// navigation; embed only local assets for rendering.
let content=await readFile(path.join(O,'slides.html'),'utf8');
const refs=[...content.matchAll(/(?:src="|url\(')(assets\/[^"')]+)/g)].map(m=>m[1]);
for(const ref of new Set(refs)){
 const bytes=await readFile(path.join(O,ref));
 const mime=ref.endsWith('.woff')?'font/woff':ref.endsWith('.svg')?'image/svg+xml':'image/png';
 content=content.split(ref).join('data:'+mime+';base64,'+bytes.toString('base64'));
}
await page.setContent(content,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
await mkdir(path.join(O,'preview'),{recursive:true});

const validation=JSON.parse(await readFile(path.join(N,'build_validation.json'),'utf8'));
validation.browser_issues=[];
validation.responsive_browser=[];
for(const [width,height] of [[1280,720],[1920,1080]]){
 await page.setViewportSize({width,height});
 await page.evaluate(()=>window.deckShow(32));
 await page.mouse.wheel(0,720);await page.waitForTimeout(100);
 await page.keyboard.press('ArrowRight');
 const result=await page.evaluate(()=>{
   const nav=document.querySelector('#nav').getBoundingClientRect();
   const page=document.querySelector('.slide.active [data-label="page"]').getBoundingClientRect();
   const overlaps=(a,b)=>Math.min(a.right,b.right)>Math.max(a.left,b.left)&&Math.min(a.bottom,b.bottom)>Math.max(a.top,b.top);
   const textOverlap=[...document.querySelectorAll('.slide.active .text')].filter(e=>{const r=document.createRange();r.selectNodeContents(e);return overlaps(nav,r.getBoundingClientRect())}).map(e=>e.dataset.label);
   return {scrollY:window.scrollY,active:document.querySelector('.slide.active').dataset.id,nav_page_overlap:overlaps(nav,page),nav_text_overlap:textOverlap};
 });
 result.width=width;result.height=height;result.pass=result.scrollY===0&&result.active==='34'&&!result.nav_page_overlap&&result.nav_text_overlap.length===0;
 validation.responsive_browser.push(result);
 await page.screenshot({path:path.join(N,`final_browser_${width}.png`)});
}
await page.setViewportSize({width:1600,height:900});
await page.addStyleTag({content:'#nav {display:none !important}'});

await page.evaluate(()=>window.deckShow(0));
await page.keyboard.press('ArrowRight');
const right=await page.locator('.slide.active').getAttribute('data-id');
await page.keyboard.press('End');
const end=await page.locator('.slide.active').getAttribute('data-id');
await page.keyboard.press('ArrowLeft');
const left=await page.locator('.slide.active').getAttribute('data-id');
await page.keyboard.press('Home');
const home=await page.locator('.slide.active').getAttribute('data-id');
validation.keyboard_navigation={right,end,left,home,pass:right==='2'&&end==='44'&&left==='43'&&home==='1'};
validation.missing_images=await page.evaluate(()=>[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.alt));
validation.embedded_font_loaded=await page.evaluate(()=>document.fonts.check('30px DeckJP'));

for(let id=1;id<=44;id++){
  await page.evaluate(n=>window.deckShow(n-1),id);
  const checks=await page.locator(`#slide-${id}`).evaluate(slide=>{
    let out=[];const shapes=[...slide.querySelectorAll('.shape')];
    for(const e of shapes){if(e.dataset.label&&((e.scrollHeight>e.clientHeight+3)||(e.scrollWidth>e.clientWidth+3))){out.push({type:'text_overflow',label:e.dataset.label,scroll:[e.scrollWidth,e.scrollHeight],box:[e.clientWidth,e.clientHeight]})}}
    const main=shapes.filter(e=>['bullet','formula','table','diagram'].includes(e.dataset.label));
    for(let i=0;i<main.length;i++)for(let j=i+1;j<main.length;j++){
      const a=main[i].getBoundingClientRect(),b=main[j].getBoundingClientRect();
      const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left),oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
      if(ox>3&&oy>3)out.push({type:'overlap',labels:[main[i].dataset.label,main[j].dataset.label],area:ox*oy});
    }return out;
  });
  validation.browser_issues.push(...checks.map(c=>({slide:id,...c})));
  await page.locator(`#slide-${id}`).screenshot({path:path.join(O,'preview',`slide-${String(id).padStart(2,'0')}.png`)});
}
await page.evaluate(()=>{document.body.classList.add('print');document.body.classList.remove('main-only')});
await page.pdf({path:path.join(O,'slides_with_appendix.pdf'),width:'1600px',height:'900px',printBackground:true,preferCSSPageSize:true});
await page.evaluate(()=>document.body.classList.add('main-only'));
await page.pdf({path:path.join(O,'slides.pdf'),width:'1600px',height:'900px',printBackground:true,preferCSSPageSize:true});
validation.browser_checked_slides=44;
validation.offline_external_requests=await page.evaluate(()=>[...document.querySelectorAll('[src],[href]')].map(e=>e.src||e.href).filter(u=>/^https?:/.test(u)));
validation.browser_status=validation.browser_issues.length?'要修正':'44枚の文字はみ出し・主内容重なりなし';
await writeFile(path.join(N,'build_validation.json'),JSON.stringify(validation,null,2));
await browser.close();console.log(`PDF/PNG 44枚生成、browser issues=${validation.browser_issues.length}`);
