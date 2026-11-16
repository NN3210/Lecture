"""検証済み第5回教材を相対リンクを保ってZIPへまとめる。"""
from pathlib import Path
import zipfile, json, hashlib

N = Path(__file__).resolve().parent
root = N.parents[1]
slides = root / 'materials/slides/第05回_トラバース測量I'
target = slides / '第05回_教員用一式_改3.zip'
folders = [slides / '改3', root / 'materials/exercises/第05回_トラバース測量I/改3', N]
files = sorted(p for f in folders for p in f.rglob('*') if p.is_file()
    and '__pycache__' not in p.parts and p.suffix not in {'.aux', '.log', '.out', '.pyc'}
    and not (p.is_relative_to(N) and p.suffix.lower() in {'.png', '.jpg', '.jpeg'})
    and not (p.parent.name == 'preview' and p.name != 'contact_sheet.jpg')
    and p.name != 'package_validation.json')
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr('はじめに.txt', '第5回 トラバース測量・トラバース計算（改3）\n\n'
        '展開後、Surveying/materials/slides/第05回_トラバース測量I/改3/README.md を開いてください。\n'
        '投影：slides.pptx または slides.pdf。\n'
        '学生用配布：slides.pdf と 学生用演習.pdf。\n'
        'PPTX・補足付きPDF・HTML・Excelは解答を含む教員用です。\n'
        'HTMLはassetsフォルダーと一緒に保存してください。\n'
        'PDF/HTML表示とPPTX構造を点検済み。PowerPoint本体描画は未確認です。\n'
        '点検記録は同梱しています。全頁確認画像と操作検証スクリーンショットはリポジトリ側に保存しています。\n')
    for p in files:
        z.write(p, p.relative_to(root.parent))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for p in files:
        assert z.read(str(p.relative_to(root.parent))) == p.read_bytes()
assert target.stat().st_size < 50 * 1024 * 1024
report = dict(file=str(target.relative_to(root)), bytes=target.stat().st_size,
    source_files=len(files), zip_integrity=True, all_file_bytes_match=True,
    sha256=hashlib.sha256(target.read_bytes()).hexdigest())
(N / 'package_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
