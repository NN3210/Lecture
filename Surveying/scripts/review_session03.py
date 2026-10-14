"""PowerPoint出力PDFを全ページ画像化し、文字の範囲を点検する。"""
from pathlib import Path
import sys,json,fitz
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
pdf=Path(sys.argv[1]) if len(sys.argv)>1 else root/'materials/slides/第03回_測量の座標/slides.pdf'
dest=root/'notes/session03_redesign/preview'
dest.mkdir(parents=True,exist_ok=True)
doc=fitz.open(pdf)
issues=[]
for i,page in enumerate(doc,1):
    pix=page.get_pixmap(matrix=fitz.Matrix(4/3,4/3))
    pix.save(dest/f'slide-{i:02}.png')
    for block in page.get_text('dict')['blocks']:
        if block['type']!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+1 or y1>page.rect.height+1:
                    issues.append({'slide':i,'type':'outside','text':span['text'],'bbox':span['bbox']})
    if 'EQM' in page.get_text():issues.append({'slide':i,'type':'math-placeholder'})
    if '$' in page.get_text():issues.append({'slide':i,'type':'unconverted-math-delimiter'})
for start in range(0,len(doc),12):
    sheet=Image.new('RGB',(1440,1192),'#dce4e2')
    draw=ImageDraw.Draw(sheet)
    for i in range(start,min(start+12,len(doc))):
        im=Image.open(dest/f'slide-{i+1:02}.png');im.thumbnail((480,270))
        x=(i-start)%3*480;y=(i-start)//3*298
        sheet.paste(im,(x,y));draw.text((x+8,y+274),str(i+1),fill='#173c4d')
    sheet.save(dest/f'contact-{start//12+1}.jpg',quality=90)
(dest.parent/'pdf-audit.json').write_text(json.dumps({'pages':len(doc),'issues':issues},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(doc),'issues':issues},ensure_ascii=False))
