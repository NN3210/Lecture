#!/usr/bin/env python3
"""改3共通原稿→PPTX / 完全オフラインHTML / Chromium PDF・PNG。
実行: python notes/session05_20261117/build_deck.py
依存: python-pptx, Pillow, PyMuPDF, fontTools, XeLaTeX, Node/playwright, Chromium。
数式はXeLaTeXで組版した画像。PPTXの文字と表は編集可能。
"""
from __future__ import annotations
import os, json, math, hashlib, subprocess, html, re
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).parent/'build_cache'))
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
import fitz
from fontTools import subset
from fontTools.ttLib import TTFont

N=Path(__file__).resolve().parent
ROOT=N.parent.parent
O=ROOT/'materials/slides/第05回_トラバース測量I/改3'
A=O/'assets'
W,H=1600,900
BG='#FAF9F5'; INK='#142B43'; BLUE='#276A9D'; GREEN='#2F7860'; ORANGE='#B86828'; MUTED='#5F707C'; LINE='#D8E0E3'
FONTP='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONTB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT='Noto Sans CJK JP'
issues=[]; layouts=[]

def font(size,bold=False): return ImageFont.truetype(FONTB if bold else FONTP, int(size))
def textwidth(s,size,bold=False): return font(size,bold).getlength(s)
def wrap(s,width,size,bold=False):
    lines=[]
    for paragraph in str(s).split('\n'):
        line=''
        tokens=re.findall(r'[A-Za-z0-9_+−=.°′″%/()]+(?: [A-Za-z]+)?|.',paragraph)
        for token in tokens:
            pieces=list(token) if textwidth(token,size,bold)>width else [token]
            for c in pieces:
                if line and textwidth(line+c,size,bold)>width:
                    lines.append(line.rstrip()); line=c.lstrip()
                else:line+=c
        lines.append(line)
    return lines

def txt(items,text,x,y,w,size=32,color=INK,bold=False,lineheight=1.48,align='left',label='text'):
    lines=wrap(text,w,size,bold)
    h=max(len(lines)*size*lineheight,(len(lines)-1)*size*lineheight+size*1.4)
    item=dict(kind='text',text='\n'.join(lines),x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,lineheight=lineheight,align=align,label=label)
    items.append(item);return h

def rect(items,x,y,w,h,color,r=0,label='decoration'):
    items.append(dict(kind='rect',x=x,y=y,w=w,h=h,color=color,r=r,label=label))

def image(items,path,x,y,w,h,label='diagram'):
    im=Image.open(path); iw,ih=im.size
    factor=min(w/iw,h/ih); rw,rh=iw*factor,ih*factor
    items.append(dict(kind='image',path=str(path.relative_to(O)),x=x+(w-rw)/2,y=y+(h-rh)/2,w=rw,h=rh,label=label))

def equation(tex):
    digest=hashlib.sha256(tex.encode()).hexdigest()[:16]
    folder=A/'formulas';folder.mkdir(exist_ok=True)
    stem=folder/digest
    if not stem.with_suffix('.png').exists():
        source='''\\documentclass[border=3pt]{standalone}
\\usepackage{fontspec,amsmath,amssymb,unicode-math,xcolor}
\\setmainfont{Noto Sans CJK JP}
\\setmathfont{Latin Modern Math}
\\definecolor{ink}{HTML}{142B43}
\\begin{document}\\color{ink}\\fontsize{25}{32}\\selectfont
$\\displaystyle '''+tex+'''$\\end{document}
'''
        stem.with_suffix('.tex').write_text(source)
        proc=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(folder),str(stem.with_suffix('.tex'))],capture_output=True,text=True)
        if proc.returncode:
            raise RuntimeError(f'数式組版失敗: {tex}\n{proc.stdout[-5000:]}')
        doc=fitz.open(stem.with_suffix('.pdf'));p=doc[0]
        p.get_pixmap(matrix=fitz.Matrix(3,3),alpha=True).save(stem.with_suffix('.png'))
        stem.with_suffix('.svg').write_text(p.get_svg_image())
        for suffix in ('.aux','.log'):stem.with_suffix(suffix).unlink(missing_ok=True)
    return stem.with_suffix('.png')

def add_equations(items,formulas,x,y,w,height):
    if not formulas:return
    paths=[equation(f) for f in formulas]
    gap=22
    maxh=min(82,(height-gap*(len(paths)-1))/len(paths))
    for path in paths:
        image(items,path,x,y,w,maxh,'formula');y+=maxh+gap

def add_bullets(items,bullets,x,y,w,maxheight,size=32):
    if not bullets:return y
    def needed(sz):return sum(len(wrap(b,w-32,sz))*sz*1.48+20 for b in bullets)-20
    while size>27 and needed(size)>maxheight:size-=1
    if needed(size)>maxheight+1:issues.append({'slide':current_id,'type':'body_overflow','height':needed(size),'available':maxheight})
    for b in bullets:
        rect(items,x,y+size*.55,7,7,BLUE,3)
        h=txt(items,b,x+28,y,w-28,size,label='bullet')
        y+=h+20
    return y-20

def table(items,t,x,y,w,h):
    cols=len(t['headers']); rows=len(t['rows'])+1
    # First index column is narrow; remaining columns share space.
    weights=[.70]+[1]*(cols-1) if cols>=3 and len(t['headers'][0])<=2 else [1]*cols
    total=sum(weights); colw=[w*a/total for a in weights]; rowh=h/rows
    data=[t['headers']]+t['rows']
    fontsize=29
    while fontsize>23:
        if all(len(wrap(str(cell),colw[c]-24,fontsize,r==0))*fontsize*1.25<=rowh-10 for r,row in enumerate(data) for c,cell in enumerate(row)):break
        fontsize-=1
    if any(len(wrap(str(cell),colw[c]-24,fontsize,r==0))*fontsize*1.25>rowh-6 for r,row in enumerate(data) for c,cell in enumerate(row)):
        issues.append({'slide':current_id,'type':'table_overflow','size':fontsize})
    items.append(dict(kind='table',data=data,x=x,y=y,w=w,h=h,colw=colw,rowh=rowh,size=fontsize,label='table'))

def build_layout(s):
    global current_id
    current_id=s['id'];items=[]
    rect(items,0,0,W,H,BG)
    rect(items,0,0,12,H,BLUE if not s['appendix'] else GREEN)
    txt(items,('補足 / 教員用　' if s['appendix'] else '測量学 / 第5回　')+s['section'],80,34,1400,20,MUTED,True,1.25,label='section')
    txt(items,s['title'],80,83,1440,51,INK,True,1.25,label='title')
    txt(items,s['lead'],82,168,1436,30,MUTED,lineheight=1.4,label='lead')
    diagram=s.get('diagram'); path=A/f'{diagram}.png' if diagram else None
    if s['id']==1 and (A/'cover_ai.png').exists():path=A/'cover_ai.png'
    if path and not path.exists():
        issues.append({'slide':s['id'],'type':'missing_diagram','diagram':diagram});path=None
    bullets=s.get('bullets',[]);formulas=s.get('formulas',[]);t=s.get('table')
    top=262;bottom=735
    if s['id']==1:
        if path:image(items,path,790,252,740,472)
        if not bullets:
            txt(items,'角をつないで、\n座標へ進む。',86,300,650,57,INK,True,1.55,label='cover_message')
            txt(items,'観測角 β　→　方向角 T\n距離 S　→　座標差 ΔX・ΔY',90,540,650,30,BLUE,lineheight=1.7,label='cover_path')
        end=add_bullets(items,bullets,86,280,635,360,33)
        add_equations(items,formulas,86,end+24,635,bottom-end-24)
        txt(items,'90分  /  講義60分・演習25分・まとめ5分',86,700,700,24,MUTED,label='duration')
    elif t and path and len(t['headers'])<=4 and len(formulas)<=1:
        image(items,path,82,top,550,bottom-top)
        end=add_bullets(items,bullets,675,top,840,210,30)
        if formulas:
            add_equations(items,formulas,675,end+18,840,64)
            end+=82
        ty=end+26
        table(items,t,675,ty,840,bottom-ty)
    elif t:
        # A table stays wide. A compact visual and explanatory block occupy the upper band.
        tabh=max(210,(len(t['rows'])+1)*44)
        tabh=min(334,tabh);ty=bottom-tabh
        if path:
            image(items,path,1000,top-12,505,max(150,ty-top-18))
            bodyw=870
        else:bodyw=1435
        formh=90*len(formulas) if formulas else 0
        avail=ty-top-22
        if bullets and formulas:
            # Parallel text and equations give long formulae room without shrinking the table.
            bw=min(690,bodyw*.52)
            add_bullets(items,bullets,84,top,bw,avail,30)
            add_equations(items,formulas,110+bw,top,bodyw-bw-24,avail)
        elif bullets:add_bullets(items,bullets,84,top,bodyw,avail,30)
        elif formulas:add_equations(items,formulas,86,top,bodyw,avail)
        table(items,t,82,ty,1436,tabh)
    elif path:
        image(items,path,810,top-8,710,bottom-top+18)
        formula_space=70*len(formulas)+22
        end=add_bullets(items,bullets,84,top,665,bottom-top-formula_space-24,32)
        add_equations(items,formulas,84,end+30,665,bottom-end-26)
    else:
        if formulas:
            end=add_bullets(items,bullets,84,top,750,bottom-top,34)
            rect(items,867,top+5,2,bottom-top-10,LINE)
            add_equations(items,formulas,916,top+45,593,bottom-top-65)
        else:
            # Three large numbered statements in a generous full-width area.
            y=top+10
            for k,b in enumerate(bullets):
                txt(items,f'{k+1:02}',86,y,85,36,BLUE,True,label='bullet_number')
                h=txt(items,b,195,y,1290,36,INK,lineheight=1.5,label='bullet')
                y+=max(h+34,118)
    rect(items,80,779,1440,70,'#EAF0F1',8)
    rect(items,80,779,7,70,GREEN)
    txt(items,'要点',105,797,80,22,GREEN,True,1.3,label='takeaway_label')
    txt(items,s['takeaway'],190,793,1295,28,INK,True,1.35,label='takeaway')
    txt(items,'トラバース測量 I  ·  改3',82,870,900,16,MUTED,lineheight=1,label='footer')
    txt(items,f'{s["id"]:02d} / 44',1370,868,146,20,MUTED,lineheight=1,align='right',label='page')
    for item in items:
        if item['x']<-.01 or item['y']<-.01 or item['x']+item['w']>W+.1 or item['y']+item['h']>H+.1:
            issues.append({'slide':s['id'],'type':'shape_outside','label':item['label'],'bounds':[item[k] for k in ('x','y','w','h')]})
        if item['label'] in ('bullet','formula','table','diagram') and item['y']+item['h']>760:
            issues.append({'slide':s['id'],'type':'content_into_footer','label':item['label']})
    return dict(id=s['id'],appendix=s['appendix'],items=items)

def css_color(c):return RGBColor.from_string(c.lstrip('#'))
def pptx_output(slides):
    prs=Presentation();prs.slide_width=Inches(13.3333333);prs.slide_height=Inches(7.5)
    def inch(v):return Inches(v/120)
    for s,layout in zip(slides,layouts):
        sl=prs.slides.add_slide(prs.slide_layouts[6])
        if s['appendix']:sl._element.set('show','0')
        sl.notes_slide.notes_text_frame.text=s['notes']
        for a in layout['items']:
            x,y,w,h=[inch(a[k]) for k in ('x','y','w','h')]
            if a['kind']=='rect':
                sh=sl.shapes.add_shape(1,x,y,w,h);sh.fill.solid();sh.fill.fore_color.rgb=css_color(a['color']);sh.line.fill.background()
            elif a['kind']=='image':sl.shapes.add_picture(str(O/a['path']),x,y,w,h)
            elif a['kind']=='text':
                sh=sl.shapes.add_textbox(x,y,w,h);tf=sh.text_frame;tf.word_wrap=False
                tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
                for i,line in enumerate(a['text'].split('\n')):
                    p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
                    p.font.name=FONT;p.font.size=Pt(a['size']*.6);p.font.bold=a['bold'];p.font.color.rgb=css_color(a['color'])
                    p.line_spacing=Pt(a['size']*a['lineheight']*.6);p.space_before=p.space_after=Pt(0)
                    p.alignment=PP_ALIGN.RIGHT if a['align']=='right' else PP_ALIGN.LEFT
                    for run in p.runs:
                        rp=run._r.get_or_add_rPr();ea=OxmlElement('a:ea');ea.set('typeface',FONT);rp.append(ea)
            elif a['kind']=='table':
                tb=sl.shapes.add_table(len(a['data']),len(a['data'][0]),x,y,w,h).table
                for c,cw in enumerate(a['colw']):tb.columns[c].width=inch(cw)
                for r,row in enumerate(a['data']):
                    tb.rows[r].height=inch(a['rowh'])
                    for c,value in enumerate(row):
                        cell=tb.cell(r,c);cell.text=str(value);cell.margin_left=cell.margin_right=inch(12);cell.margin_top=cell.margin_bottom=inch(4);cell.vertical_anchor=MSO_ANCHOR.MIDDLE
                        cell.fill.solid();cell.fill.fore_color.rgb=css_color(INK if r==0 else ('#F0F3F2' if r%2 else '#FFFFFF'))
                        for p in cell.text_frame.paragraphs:
                            p.font.name=FONT;p.font.size=Pt(a['size']*.6);p.font.bold=r==0;p.font.color.rgb=css_color('#FFFFFF' if r==0 else INK)
                            p.space_before=p.space_after=Pt(0)
                            for run in p.runs:
                                rp=run._r.get_or_add_rPr();ea=OxmlElement('a:ea');ea.set('typeface',FONT);rp.append(ea)
    prs.save(O/'slides.pptx')

def html_output(slides):
    def esc(x):return html.escape(str(x),quote=True)
    pages=[]
    for s,layout in zip(slides,layouts):
        elems=[]
        for a in layout['items']:
            style=';'.join(f'{csskey}:{a[key]:.3f}px' for key,csskey in [('x','left'),('y','top'),('w','width'),('h','height')])
            if a['kind']=='rect':body=f'<div class="shape" style="{style};background:{a["color"]};border-radius:{a["r"]}px"></div>'
            elif a['kind']=='image':body=f'<img class="shape" data-label="{a["label"]}" style="{style}" src="{esc(a["path"])}" alt="{esc(a["label"])}">'
            elif a['kind']=='text':
                body=f'<div class="shape text" data-label="{a["label"]}" style="{style};font-size:{a["size"]}px;line-height:{a["lineheight"]};font-weight:{700 if a["bold"] else 400};color:{a["color"]};text-align:{a["align"]}">{esc(a["text"])}</div>'
            else:
                rows=[]
                for r,row in enumerate(a['data']):
                    cells=''.join(f'<td style="width:{a["colw"][c]}px">{esc(cell)}</td>' for c,cell in enumerate(row))
                    rows.append(f'<tr style="height:{a["rowh"]}px">{cells}</tr>')
                body=f'<table class="shape data-table" data-label="table" style="{style};font-size:{a["size"]}px"><colgroup>'+''.join(f'<col style="width:{v}px">' for v in a['colw'])+'</colgroup>'+''.join(rows)+'</table>'
            elems.append(body)
        pages.append(f'<section class="slide" id="slide-{s["id"]}" data-id="{s["id"]}" data-appendix="{str(s["appendix"]).lower()}" aria-label="{esc(s["title"])}">'+''.join(elems)+f'<aside class="speaker-notes">{esc(s["notes"])}</aside></section>')
    text=''.join(s['title']+s['lead']+''.join(s['bullets'])+s['takeaway']+s['section']+json.dumps(s.get('table'),ensure_ascii=False) for s in slides)+'測量学第回補足教員用要点トラバース改講義分演習まとめ'
    for name,source in [('regular',FONTP),('bold',FONTB)]:
        ft=TTFont(source,fontNumber=0);options=subset.Options();options.flavor='woff';sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(ft);ft.flavor='woff';ft.save(A/f'NotoSansJP-{name}.woff')
    css='''@font-face{font-family:DeckJP;src:url('assets/NotoSansJP-regular.woff')}@font-face{font-family:DeckJP;src:url('assets/NotoSansJP-bold.woff');font-weight:700}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#152B41;font-family:DeckJP,'Noto Sans CJK JP',sans-serif}#deck{width:1600px;transform-origin:top left}.slide{position:relative;width:1600px;height:900px;background:#FAF9F5;overflow:hidden;display:none}.slide.active{display:block}.shape{position:absolute}.text{white-space:pre;overflow:visible;letter-spacing:0}.data-table{border-collapse:collapse;table-layout:fixed;color:#142B43;background:white;line-height:1.25}.data-table td{padding:4px 12px;vertical-align:middle;white-space:pre-wrap;border-bottom:1px solid #D8E0E3}.data-table tr:first-child{background:#142B43;color:white;font-weight:700}.data-table tr:nth-child(even){background:#F0F3F2}.speaker-notes{display:none}#nav{position:fixed;top:8px;right:12px;z-index:8;display:flex;gap:8px}button{border:1px solid #bfcbd2;background:#fff;color:#142B43;border-radius:6px;padding:7px 12px;font:14px DeckJP;cursor:pointer}.print .slide{display:block!important}.print #deck{transform:none!important}.print #nav{display:none}@page{size:1600px 900px;margin:0}@media print{html,body{height:auto;overflow:visible;background:white}#deck{transform:none!important}.slide{display:block!important;break-after:page;page-break-after:always}.slide:last-child{break-after:auto}#nav{display:none}.main-only .slide[data-appendix=true]{display:none!important}}
'''
    js='''const all=[...document.querySelectorAll('.slide')];let current=Math.max(0,Math.min(all.length-1,Number(location.hash.slice(1))-1||0));function show(n){window.scrollTo(0,0);current=Math.max(0,Math.min(all.length-1,n));all.forEach((s,i)=>s.classList.toggle('active',i===current));document.querySelector('#count').textContent=(current+1)+' / '+all.length;history.replaceState(null,'','#'+(current+1));}function resize(){window.scrollTo(0,0);const scale=Math.min(innerWidth/1600,innerHeight/900);document.querySelector('#deck').style.transform='scale('+scale+')';}document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#notes').onclick=()=>{const note=all[current].querySelector('.speaker-notes');alert(note.textContent)};document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}if(e.key==='Home')show(0);if(e.key==='End')show(all.length-1)});window.addEventListener('resize',resize);show(current);resize();window.deckShow=show;'''
    (O/'slides.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第5回 トラバース測量I 改3</title><style>'+css+'</style><body><main id="deck">'+''.join(pages)+'</main><nav id="nav" aria-label="スライド操作"><button id="prev">←</button><button id="count"></button><button id="next">→</button><button id="notes">講師ノート</button></nav><script>'+js+'</script></body></html>')

def main():
    O.mkdir(parents=True,exist_ok=True);A.mkdir(exist_ok=True)
    slides=json.loads((N/'part1.json').read_text())+json.loads((N/'part2.json').read_text())
    assert [s['id'] for s in slides]==list(range(1,45)), '44枚・通しID必須'
    assert all(bool(s['appendix'])==(s['id']>=37) for s in slides)
    assert all(s['notes'].strip() for s in slides),'全枚ノート必須'
    for s in slides:
        for key,maxlen in [('lead',55),('takeaway',50)]:
            if len(s[key])>maxlen:issues.append({'slide':s['id'],'type':'contract_length','field':key,'length':len(s[key])})
        layouts.append(build_layout(s))
    used_formula_stems={Path(a['path']).stem for layout in layouts for a in layout['items'] if a['kind']=='image' and a['path'].startswith('assets/formulas/')}
    for cached in (A/'formulas').glob('*'):
        if cached.is_file() and cached.stem not in used_formula_stems:cached.unlink()
    (O/'slides_source.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2))
    (N/'layout.json').write_text(json.dumps(layouts,ensure_ascii=False,indent=2))
    html_output(slides);pptx_output(slides)
    report={'slides':44,'main':36,'appendix':8,'notes':44,'python_layout_issues':issues,'pptx_rendered':False,'pptx_rendering_limit':'LibreOffice/PowerPoint未導入。PPTX実描画は未実施。HTML/PDF目視と形状境界・XML検査で代替。','formula_representation':'XeLaTeX PDF/PNG/SVG。PPTX数式は画像。本文・表は編集可能。'}
    (N/'build_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'PPTX/HTML生成: {len(slides)}枚, layout issues={len(issues)}')
    subprocess.run(['node',str(N/'render_deck.mjs')],check=True)
    subprocess.run(['python',str(N/'validate_deck.py')],check=True)

if __name__=='__main__':main()
