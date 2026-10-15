"""公開用成果物の枚数・Office数式・作成者情報・容量を確認する。"""
from pathlib import Path
import hashlib
import json
import zipfile
import fitz
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'materials/slides/第03回_測量の座標/補足_点と座標軸の回転_20261015'
pptx = OUT / '点の回転と座標軸の回転_図解.pptx'
pdf = OUT / '点の回転と座標軸の回転_図解.pdf'
with fitz.open(pdf) as doc:
    assert len(doc) == 2
    assert not doc.metadata.get('author')
with zipfile.ZipFile(pptx) as package:
    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    slides = [n for n in package.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
    assert len(slides) == 2
    count = sum(len(E.fromstring(package.read(n)).findall('.//m:oMath', ns)) for n in slides)
    assert count == 8
    for el in E.fromstring(package.read('docProps/core.xml')):
        if E.QName(el).localname in ('creator', 'lastModifiedBy'):
            assert not el.text
assert all(p.stat().st_size < 50 * 1024 * 1024 for p in OUT.rglob('*') if p.is_file())
receipt = json.loads((Path(__file__).parent / 'validation_図解.json').read_text(encoding='utf-8'))
assert hashlib.sha256(pptx.read_bytes()).hexdigest() == receipt['finalSha256']
print('2枚、Office数式8件、作成者情報なし、容量制限内、検証済みPPTXとの一致を確認。')
