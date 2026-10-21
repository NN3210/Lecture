"""KaTeX の MathML を Office の編集可能な数式（OMML）に変換し、PPTX の仮文字列 EQM##### と置き換える。

patch_session03_math.py の処理を関数にしたもの。第5回以降のビルドスクリプトから import して使う。
    from omml_equations import patch_pptx
    patch_pptx(candidate_pptx, output_pptx, maths)   # maths = {id: {'tex','mathml','display'}}
変換には Office 同梱の MML2OMML.XSL を使う（Windows + Microsoft 365）。
"""
from copy import deepcopy
from pathlib import Path
import json
import re
import zipfile

from lxml import etree as E

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
      'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a14': 'http://schemas.microsoft.com/office/drawing/2010/main',
      'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
ML = '{http://www.w3.org/1998/Math/MathML}'
XSL_CANDIDATES = [Path(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'),
                  Path(r'C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL')]
PLACEHOLDER = re.compile(r'EQM\d{5}')
_transform = None


def q(name):
    prefix, local = name.split(':')
    return '{' + NS[prefix] + '}' + local


def transform():
    global _transform
    if _transform is None:
        xsl = next((p for p in XSL_CANDIDATES if p.exists()), None)
        if xsl is None:
            raise RuntimeError('MML2OMML.XSL が見つかりません（Microsoft Office が必要です）。')
        _transform = E.XSLT(E.parse(str(xsl)))
    return _transform


def equation(record, rpr):
    """1 つの数式レコード {'tex','mathml','display'} を a14:m 要素（OMML 入り）にする。rpr は元の a:rPr。"""
    src = E.fromstring(record['mathml'].encode())
    # KaTeX のフェンス（括弧）を、Office の伸縮する区切り文字へ変換する。
    for row in list(src.iter(ML + 'mrow')):
        cs = list(row)
        if (len(cs) >= 3 and cs[0].tag == ML + 'mo' and cs[-1].tag == ML + 'mo'
                and cs[0].get('fence') == 'true' and cs[-1].get('fence') == 'true'):
            fenced = E.Element(ML + 'mfenced', open=cs[0].text or '', close=cs[-1].text or '', separators='')
            inside = E.SubElement(fenced, ML + 'mrow')
            for c in cs[1:-1]:
                inside.append(c)
            row.getparent().replace(row, fenced)
    for space in list(src.iter(ML + 'mspace')):
        # \quad / \qquad が Office 変換で消えるのを防ぐ。
        width = space.get('width', '0em')
        if width in ('1em', '2em'):
            space.tag = ML + 'mtext'
            space.text = '\u2003' * (2 if width == '2em' else 1)
    for el in src.xpath('//*[local-name()="annotation"]'):
        el.getparent().remove(el)
    converted = transform()(src).getroot()
    if r'\begin{aligned}' in record['tex']:
        # 行列（m:m）として変換された aligned を、Office の「配置された式」（m:eqArr）にする。
        for mat in list(converted.iter(q('m:m'))):
            arr = E.Element(q('m:eqArr'))
            for row in mat.findall('m:mr', NS):
                dest = E.SubElement(arr, q('m:e'))
                for col, cell in enumerate(row.findall('m:e', NS)):
                    if col:
                        mark = E.SubElement(dest, q('m:r'))
                        E.SubElement(mark, q('m:t')).text = '&'
                    for c in list(cell):
                        dest.append(c)
            mat.getparent().replace(mat, arr)
    for nary in list(converted.iter(q('m:nary'))):
        operand = nary.find('m:e', NS)
        nxt = nary.getnext()
        if operand is not None and len(operand) == 0 and nxt is not None:
            operand.append(nxt)
    # PowerPoint 数式の書式は DrawingML の run properties で指定する。
    for el in converted.xpath('.//w:rPr', namespaces=NS):
        el.getparent().remove(el)
    # Office 同梱 XSL には古い scrLvl 出力が残る。OOXML の argSz へ正規化する。
    for el in converted.xpath('.//m:scrLvl', namespaces=NS):
        el.tag = q('m:argSz')
    for tag in ('cGp', 'cGpRule', 'cSp', 'rSp', 'rSpRule', 'mcJc'):
        for el in converted.xpath('.//m:' + tag, namespaces=NS):
            el.getparent().remove(el)
    for r in converted.xpath('.//m:r', namespaces=NS):
        pr = deepcopy(rpr) if rpr is not None else E.Element(q('a:rPr'))
        pr.set('lang', 'en-US')
        pr.set('b', '0')
        for c in list(pr):
            if E.QName(c).localname in ('latin', 'ea', 'cs'):
                pr.remove(c)
        E.SubElement(pr, q('a:latin'), typeface='Cambria Math')
        E.SubElement(pr, q('a:ea'), typeface='Meiryo')
        r.insert(1 if len(r) and r[0].tag == q('m:rPr') else 0, pr)
    for cp in converted.xpath('.//m:ctrlPr', namespaces=NS):
        pr = deepcopy(rpr) if rpr is not None else E.Element(q('a:rPr'))
        for c in list(pr):
            if E.QName(c).localname in ('latin', 'ea', 'cs'):
                pr.remove(c)
        E.SubElement(pr, q('a:latin'), typeface='Cambria Math')
        cp.append(pr)
    if converted.tag == q('m:oMathPara') and not record['display']:
        converted = converted.find('m:oMath', NS)
    elif record['display'] and converted.tag == q('m:oMath'):
        para = E.Element(q('m:oMathPara'))
        pr = E.SubElement(para, q('m:oMathParaPr'))
        E.SubElement(pr, q('m:jc'), {q('m:val'): 'centerGroup'})
        para.append(converted)
        converted = para
    mat = E.Element(q('a14:m'), nsmap={'a14': NS['a14'], 'm': NS['m']})
    mat.append(converted)
    return mat


def patch_slide_xml(payload, data):
    """スライド XML（bytes）の仮文字列を数式に置き換える。置換した数式の数を返す。"""
    xml = E.fromstring(payload)
    count = 0
    originals = {el: deepcopy(el) for el in xml.findall('.//p:spTree/*', NS)}
    for run in list(xml.xpath('//a:r', namespaces=NS)):
        t = run.find('a:t', NS)
        if t is None or not t.text or not PLACEHOLDER.search(t.text):
            continue
        text = t.text
        parent = run.getparent()
        idx = parent.index(run)
        rpr = run.find('a:rPr', NS)
        for part in re.split(r'(EQM\d{5})', text):
            if not part:
                continue
            if part in data:
                child = equation(data[part], rpr)
                count += 1
            else:
                child = E.Element(q('a:r'))
                if rpr is not None:
                    child.append(deepcopy(rpr))
                E.SubElement(child, q('a:t')).text = part
            parent.insert(idx, child)
            idx += 1
        parent.remove(run)
    for el, original in originals.items():
        if not el.xpath('.//a14:m', namespaces=NS):
            continue
        # 数式に対応しない旧ビューア向けに、TeX 原文を入れた代替表現を添える。
        ac = E.Element(q('mc:AlternateContent'), nsmap={'mc': NS['mc'], 'a14': NS['a14']})
        choice = E.SubElement(ac, q('mc:Choice'), Requires='a14')
        for t in original.xpath('.//a:t', namespaces=NS):
            if t.text:
                t.text = PLACEHOLDER.sub(lambda mt: data[mt[0]]['tex'], t.text)
        fallback = E.SubElement(ac, q('mc:Fallback'))
        fallback.append(original)
        parent = el.getparent()
        parent.replace(el, ac)
        choice.append(el)
    return E.tostring(xml, xml_declaration=True, encoding='UTF-8', standalone=True), count


def patch_pptx(src, dst, data, validation=None):
    """src の PPTX の仮文字列を Office 数式にして dst に書く。docProps の作成者名は空にする。"""
    src, dst = Path(src), Path(dst)
    count = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            payload = zin.read(item.filename)
            if re.fullmatch(r'ppt/slides/slide\d+\.xml', item.filename):
                payload, n = patch_slide_xml(payload, data)
                count += n
            elif item.filename == 'docProps/core.xml':
                xml = E.fromstring(payload)
                for el in xml:
                    if E.QName(el).localname in ('creator', 'lastModifiedBy'):
                        el.text = ''
                payload = E.tostring(xml, xml_declaration=True, encoding='UTF-8', standalone=True)
            zout.writestr(item, payload)
    if count != len(data):
        raise RuntimeError(f'数式の置換数が合いません: {count} / {len(data)}')
    if validation is not None:
        Path(validation).write_text(json.dumps({'equations': count, 'format': 'Office Math (OMML)',
                                                'source': 'KaTeX MathML + Microsoft MML2OMML.XSL'},
                                               ensure_ascii=False, indent=2), encoding='utf-8')
    return count
