"""方向角の補足資料を検査し、配布用PDFを全ページ描画する。"""
from pathlib import Path
import json, re, zipfile
from xml.etree import ElementTree as E
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials/slides/第03回_測量の座標/補足_方向角と象限_20261015'
RECORDS = ROOT / 'notes/direction_angle_20261015'
PPTX = OUT / '方向角と象限_補足スライド.pptx'
PDF = OUT / '方向角と象限_補足スライド.pdf'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}

with zipfile.ZipFile(PPTX) as z:
    slides = sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)],
                    key=lambda s: int(re.search(r'(\d+)\.xml', s)[1]))
    assert len(slides) == 8
    charts = [n for n in z.namelist() if re.fullmatch(r'ppt/(?:slides/)?charts/chart\d+\.xml', n)]
    assert len(charts) == 3
    tables = sum(len(E.fromstring(z.read(n)).findall('.//a:tbl', NS)) for n in slides)
    assert tables == 4
    notes = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
    assert len(notes) == 8
    for n in slides:
        xml = E.fromstring(z.read(n))
        text = ''.join(el.text or '' for el in xml.findall('.//a:t', NS))
        assert not re.search(r'EQM\d{5}|Click to|クリックして', text)
    for n in charts:
        xml = E.fromstring(z.read(n))
        # 散布図の横・縦の縮尺をそろえ、座標図の角度を保つ。
        mins = [float(e.attrib['val']) for e in xml.findall('.//c:valAx/c:scaling/c:min', NS)]
        maxs = [float(e.attrib['val']) for e in xml.findall('.//c:valAx/c:scaling/c:max', NS)]
        assert len(mins) == len(maxs) == 2 and mins[0] == mins[1] and maxs[0] == maxs[1]
    core = E.fromstring(z.read('docProps/core.xml'))
    # 個人名を含む作成者情報を公開成果物へ持ち込まない。
    for el in core.iter():
        if el.tag.endswith(('creator', 'lastModifiedBy')):
            assert not el.text or el.text in ('Codex', 'OpenAI', 'Artifact Tool', 'Walnut Exporter')

reader = PdfReader(PDF)
assert len(reader.pages) == 8
for p in reader.pages:
    assert abs(float(p.mediabox.width)/float(p.mediabox.height)-16/9) < 1e-5
    assert len(p.extract_text()) > 100
assert not reader.metadata.author or reader.metadata.author in ('Walnut Exporter', 'Artifact Tool')

# PDFの実ファイルをレンダリングし、PowerPointのPNGとは独立に確認できるようにする。
preview = OUT / 'build/pdf_preview'
preview.mkdir(parents=True, exist_ok=True)
doc = pdfium.PdfDocument(str(PDF))
for i in range(len(doc)):
    page = doc[i]
    bitmap = page.render(scale=1.5)
    bitmap.to_pil().save(preview / f'page-{i+1:02d}.png')
    bitmap.close()
    page.close()
doc.close()

# 古い初稿の検証記録も含め、プロファイルの絶対パスを匿名化する。
profile = str(Path.home())
for record in RECORDS.glob('*.json'):
    text = record.read_text(encoding='utf-8')
    for source, dest in ((str(ROOT), '.'), (str(ROOT).replace('\\', '/'), '.'),
                         (profile, '<user-profile>'), (profile.replace('\\', '/'), '<user-profile>')):
        text = text.replace(json.dumps(source)[1:-1], dest)
    record.write_text(text, encoding='utf-8')

summary = {'スライド数': 8, '編集可能な表': tables, '編集可能な座標図': len(charts),
           '発表者ノート': len(notes), 'PDFページ数': len(reader.pages),
           'PDF全ページ描画': True, 'PPTX': str(PPTX.relative_to(ROOT)), 'PDF': str(PDF.relative_to(ROOT))}
(RECORDS / 'delivery_check.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print('8枚のPPTX・PDF、表4件、座標図3件、発表者ノート8件を確認しました。')
