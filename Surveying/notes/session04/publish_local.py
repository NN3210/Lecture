"""検証済みPowerPoint出力を第4回教材フォルダーへまとめる。"""
from pathlib import Path
import json
import shutil
import html

root=Path(__file__).resolve().parents[2]
dest=root/'materials/slides/第04回_角測量'
native=dest/'build/native_final'
assert (native/'slides.pdf').is_file()
files=sorted((native/'png').glob('slide-*.png'))
assert len(files)==60
preview=dest/'preview'
preview.mkdir(exist_ok=True)
for f in files:
    shutil.copy2(f,preview/f.name)
shutil.copy2(native/'slides.pdf',dest/'slides.pdf')
data=[]
for i in (1,2,3):
    data+=json.loads((root/f'notes/session04/slides_part{i}.json').read_text(encoding='utf-8-sig'))
header='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>測量学 第4回 角測量 スライド</title><style>body{margin:0;color:#182b33;background:#f2f5f5;font-family:"Yu Gothic",Meiryo,sans-serif}header,main{max-width:1100px;margin:auto;padding:24px}header p{line-height:1.8}a{color:#166b68}article{margin:0 0 36px}h2{font-size:18px;font-weight:500}img{width:100%;height:auto;display:block;background:white}a:focus-visible{outline:3px solid #166b68;outline-offset:4px}@media print{header,h2{display:none}main{padding:0}article{margin:0;break-after:page}body{background:white}}</style><header><h1>測量学 第4回 角測量</h1><p>本編54枚と復習用解答6枚。<a href="explanation.html">高校生向けの解説を読む</a> ／ <a href="slides.pptx">PowerPoint</a> ／ <a href="slides.pdf">PDF</a> ／ <a href="lesson_plan.md">授業計画</a></p><p>55枚目以降は解答です。授業では演習を終えてから参照してください。</p></header><main>'''
parts=[header]
for d in data:
    title=html.escape(d['title'])
    parts.append(f'<article id="slide-{d["id"]}"><h2>{d["id"]:02d}　{title}</h2><img src="preview/slide-{d["id"]:02d}.png" alt="{title}" loading="lazy" width="1280" height="720"></article>')
parts.append('</main></html>')
(dest/'slides.html').write_text('\n'.join(parts),encoding='utf-8')
print('PDF、60枚のPowerPoint実出力画像、閲覧HTMLを保存')
