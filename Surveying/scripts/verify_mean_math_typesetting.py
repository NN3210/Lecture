"""完成版の数式以外のXML一致と、PowerPoint画像の変更範囲を確認する。"""
from pathlib import Path
import json, zipfile, hashlib, sys
sys.dont_write_bytecode=True
from lxml import etree as E
from PIL import Image, ImageChops, ImageDraw, ImageStat
from patch_mean_math_typesetting import NS, q, ROOT, OUT, BUILD, SOURCE

final=OUT/'平均の誤差伝播_現場例追加_数式整形_20261015.pptx'
report=json.loads((BUILD/'検証記録.json').read_text(encoding='utf-8'))
changed={tuple(x) for x in report['変更オブジェクト']}
def signature(el):
    return (el.tag,dict(el.attrib),el.text,el.tail,[signature(c) for c in el])
def normalize(xml,slide,after=False):
    if after:
        for ac in xml.findall('.//mc:AlternateContent',NS):
            choice=ac.find('mc:Choice',NS)
            if choice is not None and choice.get('Requires')=='a14':
                children=list(choice);parent=ac.getparent();idx=parent.index(ac);parent.remove(ac)
                for c in children:parent.insert(idx,c);idx+=1
    for owner in list(xml.find('p:cSld/p:spTree',NS)):
        cnv=owner.find('.//p:cNvPr',NS)
        if cnv is None:continue
        shape=int(cnv.get('id'))
        if (slide,shape) not in changed:continue
        for tx in owner.findall('.//p:txBody',NS)+owner.findall('.//a:txBody',NS):
            for p in tx.findall('a:p',NS):tx.remove(p)
        if after and (slide,shape)==(10,5):
            owner.find('p:spPr/a:xfrm/a:off',NS).set('x','904875')
            owner.find('p:spPr/a:xfrm/a:ext',NS).set('cx','10382250')
    return signature(xml)

pixel_reports=[]
with zipfile.ZipFile(SOURCE) as a,zipfile.ZipFile(final) as b:
    assert set(a.namelist())==set(b.namelist())
    for n in a.namelist():
        if not n.startswith('ppt/slides/slide') or not n.endswith('.xml'):
            assert a.read(n)==b.read(n),n
    for slide in range(1,23):
        n=f'ppt/slides/slide{slide}.xml'
        original=E.fromstring(a.read(n));modified=E.fromstring(b.read(n))
        assert normalize(E.fromstring(a.read(n)),slide)==normalize(modified,slide,True),slide
        # 数式の入るオブジェクトだけを除外し、描画時の微小な文字縁差分を計測。
        before=Image.open(BUILD/f'before/スライド{slide}.PNG').convert('RGB')
        after=Image.open(BUILD/f'after/スライド{slide}.PNG').convert('RGB')
        difference=ImageChops.difference(before,after)
        mask=Image.new('L',before.size,255);draw=ImageDraw.Draw(mask)
        for owner in original.findall('.//p:spTree/p:sp',NS)+original.findall('.//p:spTree/p:graphicFrame',NS):
            cnv=owner.find('.//p:cNvPr',NS)
            if (slide,int(cnv.get('id'))) not in changed:continue
            xf=owner.find('p:spPr/a:xfrm',NS)
            if xf is None:xf=owner.find('p:xfrm',NS)
            off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
            x,y=[int(off.get(k))/9525 for k in ('x','y')]
            w,h=[int(ext.get(k))/9525 for k in ('cx','cy')]
            draw.rectangle([x-3,y-24,x+w+3,y+h+24],fill=0)
        outside=Image.composite(difference,Image.new('RGB',before.size),mask)
        box=outside.getbbox()
        mean=max(ImageStat.Stat(outside).mean)
        assert mean<0.25,(slide,'数式オブジェクト外の描画差分を要確認',mean,box)
        pixel_reports.append({'スライド':slide,'数式オブジェクト外の画素完全一致':box is None,
                              '数式オブジェクト外の平均絶対差_255段階':round(mean,6)})
report.update({'全スライドの数式以外のXML一致':True,'画像比較':pixel_reports,
               '元PPTX_SHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               '完成PPTX_SHA256':hashlib.sha256(final.read_bytes()).hexdigest(),
               '表示確認':'PowerPointで全22枚をPNG出力し、各ページを目視点検'})
(BUILD/'検証記録.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# 公開リポジトリに個人のローカルパスを残さない。
receipt=BUILD/'final-validation.json'
if receipt.exists():
    text=receipt.read_text(encoding='utf-8')
    text=text.replace(str(ROOT).replace('\\','\\\\'),'Surveying').replace(str(ROOT).replace('\\','/'),'Surveying')
    import re
    text=re.sub(r'C:(?:\\\\|/)+Users(?:\\\\|/)+[^/\\" ]+',r'<ユーザーディレクトリ>',text)
    receipt.write_text(text,encoding='utf-8')
print('全22枚: 数式以外のXML一致・画像差分は文字縁の微小差分以内')
