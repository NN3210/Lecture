"""最終PPTXの非表示付録を含め、PowerPointで全ページをPDF化する。"""
from pathlib import Path
import json,shutil
import fitz,win32com.client
ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'materials/slides/第04回_角測量'
OUT=ROOT/'notes/session04/kai2/final_render'
OUT.mkdir(exist_ok=True)
app=win32com.client.Dispatch('PowerPoint.Application')
count_before=app.Presentations.Count
pres=None
try:
    pres=app.Presentations.Open(str(FOLDER/'slides_回2.pptx'),True,False,False)
    count=pres.Slides.Count
    # PDF形式2、画面品質1、枠なし、順序1、スライド出力1、非表示も出力True。
    pres.ExportAsFixedFormat(str(OUT/'all.pdf'),2,1,0,1,1,-1,None,1,'',True,True,True,True,False)
finally:
    if pres is not None:pres.Close()
preview=FOLDER/'preview_回2'
preview.mkdir(exist_ok=True)
with fitz.open(OUT/'all.pdf') as all_pages:
    assert len(all_pages)==count==63,(len(all_pages),count)
    for i,page in enumerate(all_pages):
        scale=1280/page.rect.width
        page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(preview/f'slide-{i+1:02d}.png')
    main=fitz.open();main.insert_pdf(all_pages,from_page=0,to_page=49);main.save(FOLDER/'slides_回2.pdf');main.close()
shutil.copy2(OUT/'all.pdf',FOLDER/'slides_回2_付録付き.pdf')
report=dict(engine='Microsoft PowerPoint ExportAsFixedFormat',slides=count,main_slides=50,appendix=13,print_hidden_slides=True,existing_presentations_preserved=count_before)
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
