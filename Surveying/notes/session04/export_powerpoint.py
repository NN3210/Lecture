"""指定PPTXだけを読取専用で開き、PowerPointのPDFと確認画像を作る。"""
from pathlib import Path
import argparse
import json
import sys
import fitz
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')
ap=argparse.ArgumentParser()
ap.add_argument('pptx')
ap.add_argument('--out',required=True)
a=ap.parse_args()
src=Path(a.pptx).resolve()
dest=Path(a.out).resolve()
dest.mkdir(parents=True,exist_ok=True)
pdf=dest/'slides.pdf'
app=win32com.client.Dispatch('PowerPoint.Application')
initial_count=app.Presentations.Count
pres=None
try:
    pres=app.Presentations.Open(str(src),True,False,False)
    count=pres.Slides.Count
    pres.SaveAs(str(pdf),32)
finally:
    if pres is not None:
        pres.Close()
    # 他のプレゼンテーションや利用者のアプリは終了しない。

png=dest/'png'
png.mkdir(exist_ok=True)
with fitz.open(pdf) as doc:
    assert len(doc)==count
    for i,page in enumerate(doc):
        scale=1280/page.rect.width
        page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(png/f'slide-{i+1:02d}.png')
report={'engine':'Microsoft PowerPoint PDF export','slide_count':count,'existing_presentations_preserved':initial_count,'pdf':'slides.pdf','preview_directory':'png'}
(dest/'export_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
