"""KaTeXのMathMLをOfficeの編集可能な数式に変換してPPTXへ挿入する。"""
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import json,re,zipfile,sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'materials/slides/第03回_測量の座標'
BUILD=OUT/'build'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm':'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a14':'http://schemas.microsoft.com/office/drawing/2010/main',
    'mc':'http://schemas.openxmlformats.org/markup-compatibility/2006'}
def q(n):
    p,k=n.split(':');return '{'+NS[p]+'}'+k
transform=E.XSLT(E.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))
data=json.loads((BUILD/'maths.json').read_text(encoding='utf-8'))
count=0

def equation(record,rpr):
    src=E.fromstring(record['mathml'].encode())
    ml='{http://www.w3.org/1998/Math/MathML}'
    # KaTeXのフェンスを、Officeの伸縮する区切り文字へ変換する。
    for row in list(src.iter(ml+'mrow')):
        cs=list(row)
        if len(cs)>=3 and cs[0].tag==ml+'mo' and cs[-1].tag==ml+'mo' and cs[0].get('fence')=='true' and cs[-1].get('fence')=='true':
            fenced=E.Element(ml+'mfenced',open=cs[0].text or '',close=cs[-1].text or '',separators='')
            inside=E.SubElement(fenced,ml+'mrow')
            for c in cs[1:-1]:inside.append(c)
            row.getparent().replace(row,fenced)
    for space in list(src.iter(ml+'mspace')):
        # \quad/\qquadがOffice変換で消えるのを防ぐ。
        width=space.get('width','0em')
        if width in ('1em','2em'):
            space.tag=ml+'mtext';space.text='\u2003'*(2 if width=='2em' else 1)
    for el in src.xpath('//*[local-name()="annotation"]'):el.getparent().remove(el)
    converted=transform(src).getroot()
    if r'\begin{aligned}' in record['tex']:
        for mat in list(converted.iter(q('m:m'))):
            arr=E.Element(q('m:eqArr'))
            for row in mat.findall('m:mr',NS):
                dest=E.SubElement(arr,q('m:e'))
                for col,cell in enumerate(row.findall('m:e',NS)):
                    if col:
                        mark=E.SubElement(dest,q('m:r'))
                        E.SubElement(mark,q('m:t')).text='&'
                    for c in list(cell):dest.append(c)
            mat.getparent().replace(mat,arr)
    for nary in list(converted.iter(q('m:nary'))):
        operand=nary.find('m:e',NS)
        nxt=nary.getnext()
        if operand is not None and len(operand)==0 and nxt is not None:
            operand.append(nxt)
    # PowerPoint数式の書式はDrawingMLのrun propertiesで指定する。
    for el in converted.xpath('.//w:rPr',namespaces=NS):el.getparent().remove(el)
    # Office同梱XSLには古いscrLvl出力が残る。OOXMLのargSzへ正規化する。
    for el in converted.xpath('.//m:scrLvl',namespaces=NS):el.tag=q('m:argSz')
    for tag in ('cGp','cGpRule','cSp','rSp','rSpRule','mcJc'):
        for el in converted.xpath('.//m:'+tag,namespaces=NS):el.getparent().remove(el)
    for r in converted.xpath('.//m:r',namespaces=NS):
        pr=deepcopy(rpr) if rpr is not None else E.Element(q('a:rPr'))
        pr.set('lang','en-US');pr.set('b','0')
        for c in list(pr):
            if E.QName(c).localname in ('latin','ea','cs'):pr.remove(c)
        E.SubElement(pr,q('a:latin'),typeface='Cambria Math')
        E.SubElement(pr,q('a:ea'),typeface='Meiryo')
        r.insert(1 if len(r) and r[0].tag==q('m:rPr') else 0,pr)
    for cp in converted.xpath('.//m:ctrlPr',namespaces=NS):
        pr=deepcopy(rpr) if rpr is not None else E.Element(q('a:rPr'))
        E.SubElement(pr,q('a:latin'),typeface='Cambria Math');cp.append(pr)
    if converted.tag==q('m:oMathPara') and not record['display']:
        converted=converted.find('m:oMath',NS)
    elif record['display'] and converted.tag==q('m:oMath'):
        para=E.Element(q('m:oMathPara'));pr=E.SubElement(para,q('m:oMathParaPr'));E.SubElement(pr,q('m:jc'),{q('m:val'):'centerGroup'});para.append(converted);converted=para
    mat=E.Element(q('a14:m'),nsmap={'a14':NS['a14'],'m':NS['m']});mat.append(converted)
    return mat

target=BUILD/(sys.argv[1] if len(sys.argv)>1 else 'native-math.pptx')
with zipfile.ZipFile(BUILD/'candidate.pptx') as zin,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        payload=zin.read(item.filename)
        if re.fullmatch(r'ppt/slides/slide\d+\.xml',item.filename):
            xml=E.fromstring(payload)
            originals={el:deepcopy(el) for el in xml.findall('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spTree/*')}
            for run in list(xml.xpath('//a:r',namespaces=NS)):
                t=run.find('a:t',NS)
                if t is None or not t.text or not re.search(r'EQM\d{5}',t.text):continue
                text=t.text;parent=run.getparent();idx=parent.index(run);rpr=run.find('a:rPr',NS)
                for part in re.split(r'(EQM\d{5})',text):
                    if not part:continue
                    if part in data:child=equation(data[part],rpr);count+=1
                    else:
                        child=E.Element(q('a:r'))
                        if rpr is not None:child.append(deepcopy(rpr))
                        E.SubElement(child,q('a:t')).text=part
                    parent.insert(idx,child);idx+=1
                parent.remove(run)
            for el,original in originals.items():
                if not el.xpath('.//a14:m',namespaces=NS):continue
                ac=E.Element(q('mc:AlternateContent'),nsmap={'mc':NS['mc'],'a14':NS['a14']})
                choice=E.SubElement(ac,q('mc:Choice'),Requires='a14')
                # 旧ビューア用にはプレースホルダーを残さず数式の原文を入れる。
                for t in original.xpath('.//a:t',namespaces=NS):
                    if t.text:t.text=re.sub(r'EQM\d{5}',lambda m:data[m[0]]['tex'],t.text)
                fallback=E.SubElement(ac,q('mc:Fallback'));fallback.append(original)
                parent=el.getparent();parent.replace(el,ac);choice.append(el)
            payload=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
        # 作成者などの個人情報を埋め込まない。
        elif item.filename=='docProps/core.xml':
            xml=E.fromstring(payload)
            for el in xml:
                if E.QName(el).localname in ('creator','lastModifiedBy'):el.text=''
            payload=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
        zout.writestr(item,payload)
assert count==len(data),(count,len(data))
(BUILD/'math-validation.json').write_text(json.dumps({'equations':count,'format':'Office Math (OMML)','source':'KaTeX MathML + Microsoft MML2OMML.XSL'},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Office Math: {count}')
