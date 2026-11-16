const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const http=require('http');
const root=path.dirname('/workspace/Lecture/Surveying/materials/slides/第05回_トラバース測量I/改3/slides.html');
const server=http.createServer((req,res)=>{const p=path.join(root,decodeURIComponent(req.url.split('?')[0]));try{const b=fs.readFileSync(p);res.setHeader('Content-Type',p.endsWith('.html')?'text/html':p.endsWith('.woff')?'font/woff':p.endsWith('.png')?'image/png':'application/octet-stream');res.end(b)}catch(e){res.statusCode=404;res.end()}});
const out=process.env.REVIEW_OUT || __dirname;
fs.mkdirSync(out,{recursive:true});
const target='/workspace/Lecture/Surveying/materials/slides/第05回_トラバース測量I/改3/slides.html';
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const result={target,checkedAt:new Date().toISOString(),viewports:[]};
 for(const viewport of [{width:1280,height:720},{width:1920,height:1080}]){
 const ctx=await browser.newContext({viewport});
 const page=await ctx.newPage();const errors=[],failed=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});page.on('request',r=>requests.push(r.url()));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));
 await ctx.route('**/*',route=>new URL(route.request().url()).hostname==='127.0.0.1'?route.continue():route.abort());
 await page.goto('http://127.0.0.1:'+server.address().port+'/slides.html');await page.evaluate(()=>document.fonts.ready);
 const snap=()=>page.evaluate(()=>({hash:location.hash,active:[...document.querySelectorAll('.slide.active')].map(e=>e.id),count:document.querySelector('#count').textContent,page:document.querySelector('.slide.active [data-label="page"]').textContent}));
 const steps=[];steps.push({op:'initial',...await snap()});
 for(const key of ['ArrowRight','ArrowLeft','Home','ArrowLeft','End','ArrowRight','Home','PageDown','PageUp','Space']){await page.keyboard.press(key);steps.push({op:key,...await snap()})}
 await page.click('#next');steps.push({op:'next button',...await snap()});await page.click('#prev');steps.push({op:'prev button',...await snap()});
 const before=await snap();await page.click('#count');steps.push({op:'count button',before,after:await snap()});
 let note='';page.once('dialog',async d=>{note=d.message();await d.accept()});await page.click('#notes');await page.waitForTimeout(100);steps.push({op:'speaker notes',note,expected:await page.locator('.slide.active .speaker-notes').textContent()});
 const pageNumbers=await page.evaluate(()=>[...document.querySelectorAll('.slide')].map((s,i)=>({id:s.id,number:s.querySelector('[data-label=page]').textContent,expected:String(i+1).padStart(2,'0')+' / 44'})));
 await page.mouse.wheel(0,400);await page.waitForTimeout(100);const scrollAfterWheel=await page.evaluate(()=>({x:scrollX,y:scrollY}));await page.keyboard.press('ArrowRight');const scrollAfterArrow=await page.evaluate(()=>({x:scrollX,y:scrollY}));await page.screenshot({path:path.join(out,`${viewport.width}x${viewport.height}_after_wheel_arrow.png`)});await page.keyboard.press('Home');await page.waitForTimeout(500);const scrollAfterHome=await page.evaluate(()=>({x:scrollX,y:scrollY}));await page.screenshot({path:path.join(out,`${viewport.width}x${viewport.height}_after_wheel_home.png`)});await page.evaluate(()=>scrollTo(0,0));
 const assets=await page.evaluate(()=>({images:[...document.images].map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0})),fonts:[...document.fonts].map(f=>({family:f.family,status:f.status,weight:f.weight})),external:[...document.querySelectorAll('[src],[href]')].map(e=>e.src||e.href).filter(u=>/^https?:/.test(u))}));
 const frames=[];
 for(const n of [1,20,33,44]){await page.evaluate(n=>window.deckShow(n-1),n);await page.screenshot({path:path.join(out,`${viewport.width}x${viewport.height}_slide${String(n).padStart(2,'0')}.png`)});frames.push(await page.evaluate(()=>{const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};return {slide:document.querySelector('.slide.active').id,slideBox:rect(document.querySelector('.slide.active')),pageBox:rect(document.querySelector('.slide.active [data-label="page"]')),navBox:rect(document.querySelector('#nav')),doc:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},viewport:{width:innerWidth,height:innerHeight}}}));}
 result.viewports.push({viewport,steps,pageNumbers,scrollAfterWheel,scrollAfterArrow,scrollAfterHome,assets,frames,errors,failed,requestCount:requests.length,networkRequests:requests.filter(u=>/^https?:/.test(u))});await ctx.close();
 }
 await browser.close();server.close();fs.writeFileSync(path.join(out,'browser_results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result.viewports.map(v=>({viewport:v.viewport,steps:v.steps.map(s=>({op:s.op,count:s.count,notesMatch:s.note?s.note===s.expected:undefined})),images:v.assets.images.length,badImages:v.assets.images.filter(i=>!i.ok),fonts:v.assets.fonts,errors:v.errors,failed:v.failed,network:v.networkRequests,frames:v.frames})),null,2));
})();
