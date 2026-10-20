"""視覚版の全ページ一覧・テキスト照合・数値確認を保存。"""
from pathlib import Path
import fitz,json,re,math
from zipfile import ZipFile
from lxml import etree as E
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parents[1]
root=base/'materials/slides/第03回_測量の座標'
review=base/'notes/session03_visual_20261020'
doc=fitz.open(root/'slides_視覚リニューアル_20261020.pdf')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
norm=lambda t:re.sub(r'\s+','',t)
missing=[];checked=0
with ZipFile(root/'slides_視覚リニューアル_20261020.pptx') as z:
    for n,page in enumerate(doc,1):
        r=E.fromstring(z.read(f'ppt/slides/slide{n}.xml'));actual=norm(page.get_text())
        for el in r.findall('.//p:spTree/p:sp',ns):
            expected=norm(''.join(el.xpath('.//a:t/text()',namespaces=ns)))
            if expected and len(expected)>4:
                checked+=1
                if expected not in actual:missing.append([n,expected])
for start in range(0,81,12):
    out=Image.new('RGB',(1280,800),'#dde5ea');draw=ImageDraw.Draw(out)
    for k in range(12):
        n=start+k
        if n>=len(doc):break
        pix=doc[n].get_pixmap(matrix=fitz.Matrix(.44,.44));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        im.thumbnail((420,177));x=k%3*426;y=k//3*200;out.paste(im,(x,y+20));draw.text((x+5,y+2),str(n+1),fill='black')
    out.save(review/f'contact_{start+1:02}.jpg')
for n in [14,16,26,36,63,66,67,68,73]:
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(review/f'slide_{n:02}.png')
assert len(doc)==81
assert not missing,missing
# 新しい模式図の方角と、元の例題で使う回転の数値。
for t,sx,sy in [(60,1,1),(120,-1,1),(198,-1,-1)]:
    assert math.copysign(1,math.cos(math.radians(t)))==sx
    assert math.copysign(1,math.sin(math.radians(t)))==sy
theta=math.pi/6
assert round(1.08*math.cos(theta)-.91*math.sin(theta),2)==.48
assert round(1.08*math.sin(theta)+.91*math.cos(theta),2)==1.33
result={'pages':len(doc),'normal_textboxes_checked':checked,'missing_text':missing,'diagram_direction_checks':'passed','rotation_example':'passed','renderer':'LibreOffice; mathematical compatibility pictures from original PDF','powerpoint_application_check':False}
(review/'pdf-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
