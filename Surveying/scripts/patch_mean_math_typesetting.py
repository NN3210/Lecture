"""平均の誤差伝播の数式のみをOffice数式へ置換し、他の要素の保持を検証する。"""
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import json, re, zipfile, sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'notes/mean_math_typesetting'
OUT = ROOT / 'materials/slides/第02回_測量の基礎と誤差論/補足_平均の誤差伝播_20261014'
SOURCE = OUT / '平均の誤差伝播_現場例追加_20261015.pptx'
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'm':'http://schemas.openxmlformats.org/officeDocument/2006/math',
      'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a14':'http://schemas.microsoft.com/office/drawing/2010/main',
      'mc':'http://schemas.openxmlformats.org/markup-compatibility/2006'}
def q(n):
    prefix, key = n.split(':'); return '{'+NS[prefix]+'}'+key

# 元の記号・数値・式の意味を維持する、表示形式だけの対応表。
RULES = []
def add(slide, shape, old, tex, size=None):
    RULES.append(dict(slide=slide, shape=shape, old=old, tex=tex, size=size))

add(1,5,'√n',r'\sqrt{n}')
add(2,5,'x̄ = (30.000 + 30.004 + 30.002 + 30.006) / 4',r'\bar{x}=\frac{30.000+30.004+30.002+30.006}{4}')
add(2,6,'x̄ = 30.003 m',r'\bar{x}=30.003\,\mathrm{m}')
add(4,3,'xᵢ = X + eᵢ',r'x_i=X+e_i')
add(4,4,'X',r'X'); add(4,4,'xᵢ',r'x_i'); add(4,4,'i',r'i')
add(4,5,'eᵢ',r'e_i')
add(4,6,'n',r'n'); add(4,6,'x̄',r'\bar{x}')
add(4,7,'x̄ = (x₁ + ⋯ + xₙ) / n = X + (e₁ + ⋯ + eₙ) / n',r'\bar{x}=\frac{x_1+\cdots+x_n}{n}=X+\frac{e_1+\cdots+e_n}{n}')
add(5,4,'x̄ = (x₁ + x₂ + x₃ + x₄) / 4',r'\bar{x}=\frac{x_1+x_2+x_3+x_4}{4}')
add(5,5,'4 mm / 4 = 1 mm',r'\frac{4\,\mathrm{mm}}{4}=1\,\mathrm{mm}')
add(5,6,'1/4',r'\frac{1}{4}')
add(5,8,'1/4',r'\frac{1}{4}')
add(6,3,'E[ ]',r'\mathrm{E}[\;]')
add(6,5,'E[eᵢ] = 0',r'\mathrm{E}[e_i]=0')
add(6,6,'τ² = E[eᵢ²]',r'\tau^2=\mathrm{E}[e_i^2]')
add(6,6,'τ = √E[eᵢ²]',r'\tau=\sqrt{\mathrm{E}[e_i^2]}',24)
add(7,3,'e₁',r'e_1'); add(7,3,'e₂',r'e_2')
add(7,5,'E[e₁e₂] = (1 − 1 − 1 + 1) / 4 = 0',r'\mathrm{E}[e_1e_2]=\frac{1-1-1+1}{4}=0')
add(7,None,'e₁＋e₂',r'e_1+e_2'); add(7,None,'e₁e₂',r'e_1e_2')
add(7,None,'e₁',r'e_1'); add(7,None,'e₂',r'e_2')
add(8,3,'Var',r'\operatorname{Var}')
add(8,4,'(e₁ + e₂)² = e₁² + 2e₁e₂ + e₂²',r'(e_1+e_2)^2=e_1^2+2e_1e_2+e_2^2')
add(8,5,'E[(e₁ + e₂)²] = E[e₁²] + 2E[e₁e₂] + E[e₂²]',r'\mathrm{E}[(e_1+e_2)^2]=\mathrm{E}[e_1^2]+2\mathrm{E}[e_1e_2]+\mathrm{E}[e_2^2]')
add(8,6,'E[e₁e₂] = 0',r'\mathrm{E}[e_1e_2]=0')
add(8,7,'Var(e₁ + e₂) = Var(e₁) + Var(e₂)',r'\operatorname{Var}(e_1+e_2)=\operatorname{Var}(e_1)+\operatorname{Var}(e_2)')
add(9,8,'1/n²',r'1/n^2'); add(9,8,'1/n',r'1/n')
add(9,3,'eᵢ/n',r'e_i/n'); add(9,3,'eᵢ',r'e_i')
add(9,4,'(eᵢ / n)² = eᵢ² / n²',r'\left(\frac{e_i}{n}\right)^2=\frac{e_i^2}{n^2}')
add(9,5,'Var(eᵢ / n) = τ² / n²',r'\operatorname{Var}\left(\frac{e_i}{n}\right)=\frac{\tau^2}{n^2}')
add(9,6,'τ²/16',r'\tau^2/16')
add(9,7,'1/n²',r'1/n^2')
add(10,9,'n',r'n'); add(10,3,'n',r'n')
add(10,4,'Var(x̄) = τ²/n² + ⋯ + τ²/n²',r'\operatorname{Var}(\bar{x})=\frac{\tau^2}{n^2}+\cdots+\frac{\tau^2}{n^2}',22.5)
add(10,5,'　　　 = n × τ²/n² = τ²/n',r'=n\times\frac{\tau^2}{n^2}=\frac{\tau^2}{n}',22.5)
add(10,6,'SD(x̄) = √(τ²/n) = τ/√n',r'\operatorname{SD}(\bar{x})=\sqrt{\frac{\tau^2}{n}}=\frac{\tau}{\sqrt{n}}',20.25)
add(10,7,'SD',r'\operatorname{SD}'); add(10,7,'X',r'X')
add(10,8,'1/n²',r'1/n^2'); add(10,8,'1/n',r'1/n'); add(10,8,'1/√n',r'1/\sqrt{n}'); add(10,8,'n',r'n')
add(11,3,'τ = 4 mm',r'\tau=4\,\mathrm{mm}')
# 表内の数式。数字だけのデータセル・表の書式はそのまま保持。
add(11,None,'4 / 4',r'\frac{4}{4}',18.75)
add(11,None,'1²',r'1^2')
add(11,None,'1＋1＋1＋1',r'1+1+1+1')
add(11,None,'√4',r'\sqrt{4}')
add(12,9,'τ',r'\tau')
add(12,3,'vᵢ = xᵢ − x̄',r'v_i=x_i-\bar{x}')
add(12,4,'σ = √[ (v₁² + ⋯ + vₙ²) / (n − 1) ]',r'\sigma=\sqrt{\frac{v_1^2+\cdots+v_n^2}{n-1}}',20.25)
add(12,5,'σ(x̄) = σ / √n',r'\sigma(\bar{x})=\frac{\sigma}{\sqrt{n}}',24)
add(12,6,'σ(x̄)',r'\sigma(\bar{x})'); add(12,6,'σ',r'\sigma')
add(12,7,'σ(x̄)',r'\sigma(\bar{x})')
add(12,8,'n−1',r'n-1'); add(12,8,'√n',r'\sqrt{n}')
add(13,3,'x̄ = 30.004 m',r'\bar{x}=30.004\,\mathrm{m}'); add(13,3,'Σ',r'\sum')
add(13,None,'xᵢ',r'x_i'); add(13,None,'vᵢ²',r'v_i^2'); add(13,None,'vᵢ',r'v_i')
add(13,5,'Σvᵢ² = 40 mm²',r'\sum v_i^2=40\,\mathrm{mm}^2')
add(13,5,'σ = √(40/4) = √10 ≈ 3.16 mm',r'\sigma=\sqrt{\frac{40}{4}}=\sqrt{10}\approx3.16\,\mathrm{mm}',23)
add(13,6,'σ(x̄) = √10/√5 = √2 ≈ 1.41 mm',r'\sigma(\bar{x})=\frac{\sqrt{10}}{\sqrt{5}}=\sqrt{2}\approx1.41\,\mathrm{mm}',23)
add(14,3,'τ = 4 mm',r'\tau=4\,\mathrm{mm}')
add(14,6,'SD(x̄) = 4/√n mm',r'\operatorname{SD}(\bar{x})=\frac{4}{\sqrt{n}}\,\mathrm{mm}',22.5)
add(14,7,'1/2',r'\frac{1}{2}',24)
add(14,8,'1/4',r'\frac{1}{4}',24)
add(15,4,'σ = 6 mm',r'\sigma=6\,\mathrm{mm}'); add(15,4,'t = 2 mm',r't=2\,\mathrm{mm}')
add(15,7,'n',r'n')
add(15,8,'σ/√n ≤ t',r'\frac{\sigma}{\sqrt{n}}\le t',20)
add(15,9,'n ≥ (σ/t)²',r'n\ge\left(\frac{\sigma}{t}\right)^2',19.5)
add(15,10,'n ≥ (6/2)² = 9',r'n\ge\left(\frac{6}{2}\right)^2=9',19.5)
add(16,None,'(6/3)² = 4',r'\left(\frac{6}{3}\right)^2=4',18.75)
add(16,None,'(6/2)² = 9',r'\left(\frac{6}{2}\right)^2=9',18.75)
add(16,None,'(6/1)² = 36',r'\left(\frac{6}{1}\right)^2=36',18.75)
add(17,3,'b = ＋2 mm',r'b=+2\,\mathrm{mm}')
add(17,4,'xᵢ = X + b + eᵢ',r'x_i=X+b+e_i')
add(17,5,'x̄ = X + b + (e₁ + ⋯ + eₙ) / n',r'\bar{x}=X+b+\frac{e_1+\cdots+e_n}{n}')
add(17,6,'X＋2 mm',r'X+2\,\mathrm{mm}')
add(18,4,'e',r'e')
add(18,5,'(e + e + e + e) / 4 = e',r'\frac{e+e+e+e}{4}=e')
add(18,8,'σ/√n',r'\sigma/\sqrt{n}')
add(20,3,'6/√9 = 2 mm',r'\frac{6}{\sqrt{9}}=2\,\mathrm{mm}')
add(20,4,'6/√n = 1',r'\frac{6}{\sqrt{n}}=1')
add(20,4,'√n = 6',r'\sqrt{n}=6'); add(20,4,'n = 36',r'n=36')
add(20,6,'1回の標準偏差 / √観測回数',r'\frac{\text{1回の標準偏差}}{\sqrt{\text{観測回数}}}',23.25)
add(21,3,'y = f(x₁, …, xₙ)',r'y=f(x_1,\ldots,x_n)')
add(21,3,'cᵢ = ∂f/∂xᵢ',r'c_i=\partial f/\partial x_i')
add(21,4,'cᵢ',r'c_i'); add(21,4,'xᵢ',r'x_i')
add(21,5,'Var(y) ≈ Σ cᵢ² Var(xᵢ)',r'\operatorname{Var}(y)\approx\sum c_i^2\operatorname{Var}(x_i)')
add(21,6,'cᵢ = 1/n',r'c_i=\frac{1}{n}')
add(21,6,'Var(x̄) = Σ τ²/n² = τ²/n',r'\operatorname{Var}(\bar{x})=\sum\frac{\tau^2}{n^2}=\frac{\tau^2}{n}')
add(22,7,'τ',r'\tau'); add(22,7,'σ',r'\sigma'); add(22,7,'s',r's')
add(22,8,'σ(x̄)',r'\sigma(\bar{x})')

def prepare():
    BUILD.mkdir(parents=True,exist_ok=True)
    (BUILD/'rules.json').write_text(json.dumps(RULES,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    records=json.loads((BUILD/'mathml.json').read_text(encoding='utf-8'))
    transform=E.XSLT(E.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))
    counts={}; changed=[]; paragraph_log=[]
    def equation(record, pr, size, standalone, in_table):
        src=E.fromstring(record['mathml'].encode()); ml='{http://www.w3.org/1998/Math/MathML}'
        for el in src.xpath('//*[local-name()="annotation"]'):el.getparent().remove(el)
        for row in list(src.iter(ml+'mrow')):
            cs=list(row)
            if len(cs)>=3 and cs[0].tag==ml+'mo' and cs[-1].tag==ml+'mo' and cs[0].get('fence')=='true' and cs[-1].get('fence')=='true':
                fenced=E.Element(ml+'mfenced',open=cs[0].text or '',close=cs[-1].text or '',separators='')
                inside=E.SubElement(fenced,ml+'mrow')
                for c in cs[1:-1]:inside.append(c)
                row.getparent().replace(row,fenced)
        converted=transform(src).getroot()
        for el in converted.xpath('.//w:rPr',namespaces=NS):el.getparent().remove(el)
        for el in converted.xpath('.//m:scrLvl',namespaces=NS):el.tag=q('m:argSz')
        if converted.tag==q('m:oMathPara'):converted=converted.find('m:oMath',NS)
        if in_table:
            # 表の行高を変えないよう、表中だけは教科書の行内式と同じ斜線分数。
            for f in converted.findall('.//m:f',NS):
                fp=f.find('m:fPr',NS)
                if fp is None:fp=E.Element(q('m:fPr'));f.insert(0,fp)
                typ=fp.find('m:type',NS)
                if typ is None:typ=E.SubElement(fp,q('m:type'))
                typ.set(q('m:val'),'lin')
        for r in converted.xpath('.//m:r',namespaces=NS):
            rp=deepcopy(pr);rp.set('lang','en-US');rp.set('b','0');rp.set('i','0');rp.set('sz',str(round(size*100)))
            for c in list(rp):
                if E.QName(c).localname in ('latin','ea','cs'):rp.remove(c)
            E.SubElement(rp,q('a:latin'),typeface='Cambria Math')
            E.SubElement(rp,q('a:ea'),typeface='Meiryo')
            r.insert(1 if len(r) and r[0].tag==q('m:rPr') else 0,rp)
        for cp in converted.xpath('.//m:ctrlPr',namespaces=NS):
            rp=deepcopy(pr);rp.set('b','0');rp.set('sz',str(round(size*100)))
            E.SubElement(rp,q('a:latin'),typeface='Cambria Math');cp.append(rp)
        if standalone and not in_table:
            # Officeの暗黙の中央揃えを抑え、元資料の左揃えを維持する。
            para=E.Element(q('m:oMathPara'));pp=E.SubElement(para,q('m:oMathParaPr'))
            E.SubElement(pp,q('m:jc'),{q('m:val'):'left'});para.append(converted);converted=para
        mat=E.Element(q('a14:m'),nsmap={'a14':NS['a14'],'m':NS['m']});mat.append(converted)
        return mat
    with zipfile.ZipFile(SOURCE) as zin,zipfile.ZipFile(BUILD/'candidate.pptx','w',zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            payload=zin.read(item.filename)
            match=re.fullmatch(r'ppt/slides/slide(\d+)\.xml',item.filename)
            if match:
                slide=int(match[1]);xml=E.fromstring(payload)
                # sp単位で処理。表内も同じ段落構造を持つ。
                owners=xml.findall('.//p:spTree/p:sp',NS)+xml.findall('.//p:spTree/p:graphicFrame',NS)
                for owner in owners:
                    cnv=owner.find('.//p:cNvPr',NS);shape=int(cnv.get('id'))
                    relevant=[(i,r) for i,r in enumerate(records) if r['slide']==slide and (r['shape']==shape or r['shape'] is None)]
                    if not relevant:continue
                    original=deepcopy(owner);owner_changed=False
                    for paragraph in owner.findall('.//a:p',NS):
                        runs=paragraph.findall('a:r',NS)
                        if not runs:continue
                        text=''.join(r.findtext('a:t','',NS) for r in runs)
                        intervals=[]
                        for i,rec in sorted(relevant,key=lambda pair:-len(pair[1]['old'])):
                            for m in re.finditer(re.escape(rec['old']),text):
                                if any(m.start()<b and m.end()>a for a,b,*_ in intervals):continue
                                intervals.append((m.start(),m.end(),i,rec))
                        if not intervals:continue
                        intervals.sort();owner_changed=True
                        standalone=len(intervals)==1 and intervals[0][0]==0 and intervals[0][1]==len(text)
                        defpr=paragraph.find('a:pPr/a:defRPr',NS)
                        if defpr is None:defpr=owner.find('.//a:lstStyle/a:defPPr/a:defRPr',NS)
                        if defpr is None:defpr=E.Element(q('a:rPr'),sz='2100')
                        bounds=[];pos=0
                        for run in runs:
                            t=run.findtext('a:t','',NS);bounds.append((pos,pos+len(t),run));pos+=len(t)
                        def effective(at):
                            pr=deepcopy(defpr);pr.tag=q('a:rPr')
                            run=next(r for a,b,r in bounds if a<=at<b)
                            rp=run.find('a:rPr',NS)
                            if rp is not None:
                                pr.attrib.update(rp.attrib)
                                for ch in rp:
                                    for existing in list(pr):
                                        if existing.tag==ch.tag:pr.remove(existing)
                                    pr.append(deepcopy(ch))
                            return pr
                        def plain(a,b):
                            result=[]
                            for start,end,run in bounds:
                                lo,hi=max(a,start),min(b,end)
                                if lo<hi:
                                    cp=deepcopy(run);cp.find('a:t',NS).text=text[lo:hi];result.append(cp)
                            return result
                        parts=[];last=0;spans=[]
                        for a,b,i,rec in intervals:
                            parts.extend(plain(last,a));pr=effective(a)
                            # 独立した式は元の文字サイズを基本に、横線分数の高さに合わせる。
                            base=int(pr.get('sz','2100'))/100
                            fraction='\\frac' in rec['tex']
                            size=rec['size'] or (min(base,25.5) if fraction else base)
                            parts.append(equation(rec,pr,size,standalone,owner.tag==q('p:graphicFrame')));last=b
                            counts[i]=counts.get(i,0)+1;spans.append([a,b])
                        parts.extend(plain(last,len(text)))
                        insert=paragraph.index(runs[0])
                        for run in runs:paragraph.remove(run)
                        for child in parts:paragraph.insert(insert,child);insert+=1
                        # 数式以外の文字列は1文字も変更しない。
                        expected=''.join(text[a:b] for a,b in zip([0]+[b for a,b in spans],[a for a,b in spans]+[len(text)]))
                        actual=''.join(t.text or '' for r in paragraph.findall('a:r',NS) for t in r.findall('a:t',NS))
                        assert actual==expected,(slide,shape,text,actual,expected)
                        paragraph_log.append(dict(slide=slide,shape=shape,before=text,math_spans=spans))
                    if owner_changed:
                        if (slide,shape)==(10,5):
                            # 式の2行目だけ等号位置を揃える。本文等の位置は触らない。
                            owner.find('p:spPr/a:xfrm/a:off',NS).set('x',str(round(152*9525)))
                            owner.find('p:spPr/a:xfrm/a:ext',NS).set('cx',str(round(1033*9525)))
                        # 旧版ビューア向けの元テキストをFallbackに保持する。
                        ac=E.Element(q('mc:AlternateContent'),nsmap={'mc':NS['mc'],'a14':NS['a14']})
                        choice=E.SubElement(ac,q('mc:Choice'),Requires='a14')
                        fallback=E.SubElement(ac,q('mc:Fallback'));fallback.append(original)
                        parent=owner.getparent();parent.replace(owner,ac);choice.append(owner)
                        # 文字以外のオブジェクト構造・位置・書式は同一。
                        clean=deepcopy(owner);old=deepcopy(original)
                        if (slide,shape)==(10,5):
                            clean.find('p:spPr/a:xfrm/a:off',NS).set('x',old.find('p:spPr/a:xfrm/a:off',NS).get('x'))
                            clean.find('p:spPr/a:xfrm/a:ext',NS).set('cx',old.find('p:spPr/a:xfrm/a:ext',NS).get('cx'))
                        for el in (clean,old):
                            for tx in el.findall('.//p:txBody',NS)+el.findall('.//a:txBody',NS):
                                for p in tx.findall('a:p',NS):tx.remove(p)
                            E.cleanup_namespaces(el)
                        assert E.tostring(clean)==E.tostring(old),(slide,shape,'書式・配置が変化')
                        changed.append([slide,shape])
                if any(s==slide for s,sh in changed):
                    payload=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
            zout.writestr(item,payload)
    assert len(counts)==len(records),[(r['slide'],r['shape'],r['old']) for i,r in enumerate(records) if i not in counts]
    # ZIP内では対象スライドXML以外のすべてをバイト単位で保持する。
    with zipfile.ZipFile(SOURCE) as a,zipfile.ZipFile(BUILD/'candidate.pptx') as b:
        modified=[n for n in a.namelist() if a.read(n)!=b.read(n)]
        assert all(re.fullmatch(r'ppt/slides/slide\d+\.xml',n) for n in modified)
    report={'数式数':sum(counts.values()),'変更オブジェクト':changed,'変更ZIP項目':modified,
            '数式以外の文字列保持':True,'数式以外の配置・図・グラフ・発表者ノート保持':True,
            '数式のみの位置調整':{'slide':10,'shape':5,'内容':'継続行の等号位置を揃えた'},'段落の数式範囲':paragraph_log}
    (BUILD/'検証記録.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Office数式 {sum(counts.values())}件、変更オブジェクト {len(changed)}件')

if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    else:main()
