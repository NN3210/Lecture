from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib
from lxml import etree
import fitz
ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'materials/slides/第04回_角測量'
OUT=ROOT/'notes/session04/kai2'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
checks=[]
def check(name,ok,detail=''):checks.append(dict(name=name,pass_=bool(ok),detail=detail))
with ZipFile(FOLDER/'slides_回2.pptx') as z:
    names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
    check('全63枚',len(names)==63)
    texts={};hidden=[];tables=[];pictures=[]
    for i in range(1,64):
        xml=etree.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        texts[i]=''.join(xml.xpath('//a:t/text()',namespaces=NS))
        if xml.get('show')=='0':hidden.append(i)
        if xml.xpath('//a:tbl',namespaces=NS):tables.append(i)
        if xml.xpath('//p:pic',namespaces=NS):pictures.append(i)
    check('51–63枚だけ非表示',hidden==list(range(51,64)),hidden)
    expected_tables=[20,25,29,30,31,36,45,46,51,52,53,56]
    check('12ページに編集可能なネイティブ表',tables==expected_tables,tables)
    check('図を全面画像にしていない',not pictures,pictures)
    notes=[]
    for i in range(1,64):
        xml=etree.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        text=''.join(xml.xpath('//a:t/text()',namespaces=NS));notes.append(text)
    check('全63枚に実質的な発表者ノート',all(len(t)>55 for t in notes))
    check('ノート5の位置案内が実際のページと一致','各ページ上部' in notes[4] and '右上' not in notes[4])
    checks_text={26:['73°25′15″','73°25′11″'],27:['146°50′26″','＋4″'],31:['73°25′11.5″','10″以下','8″以下'],35:['24″','78°12′30″','11°47′30″'],49:['220°','320°','A→C'],51:['128°32′28″'],52:['257°04′36″','257°04′52″'],53:['16″','8″','再測','62°14′15.5″'],54:['89°25′37.4″'],55:['100.0050 m','＋0.0050 m']}
    for i,values in checks_text.items():check(f'ページ{i}の検算値を保持',all(v in texts[i] for v in values),values)
    check('較差を生読定r/lの差に戻していない','D＝p＋q' in texts[48] and 'C＝p−q' in texts[48])
    check('演習で360度またぎの箇所を題で先に明かさない','Cは360°' not in texts[46])
for name,count in [('slides_回2.pdf',50),('slides_回2_付録付き.pdf',63)]:
    with fitz.open(FOLDER/name) as doc:check(name+'のページ数',len(doc)==count,len(doc))
preview=FOLDER/'preview_回2'
check('最終PPTXをPowerPointで全63枚レンダー',len(list(preview.glob('slide-*.png')))==63)
changed=[]
for i in range(1,64):
    a=OUT/'render/png'/f'slide-{i:02d}.png';b=preview/a.name
    if a.read_bytes()!=b.read_bytes():changed.append(i)
report={'checks':checks,'changed_visual_pages':changed,'pptx_sha256':hashlib.sha256((FOLDER/'slides_回2.pptx').read_bytes()).hexdigest()}
(OUT/'deck_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
failed=[x for x in checks if not x['pass_']]
print(json.dumps({'checks':len(checks),'failed':failed,'changed_visual_pages':changed},ensure_ascii=False))
assert not failed
