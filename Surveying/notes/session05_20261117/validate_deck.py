#!/usr/bin/env python3
"""PDF全頁描画・PPTX構造/形状境界の納品検査。build_deck.pyから呼ぶ。"""
import json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import fitz
from PIL import Image
N=Path(__file__).resolve().parent
O=N.parents[1]/'materials/slides/第05回_トラバース測量I/改3'
v=json.loads((N/'build_validation.json').read_text())
v['pdf_pages']={}
for name,count in [('slides.pdf',36),('slides_with_appendix.pdf',44)]:
 doc=fitz.open(O/name);assert len(doc)==count
 v['pdf_pages'][name]=len(doc)
 assert all(abs(p.rect.width-1200)<1 and abs(p.rect.height-675)<1 for p in doc)
 if count==44:
  for i,page in enumerate(doc):
   page.get_pixmap(matrix=fitz.Matrix(4/3,4/3),alpha=False).save(O/'preview'/f'slide-{i+1:02}.png')
v['pdf_rasterized_pages']=44
v['pdf_missing_replacement_glyph']=any('\ufffd' in p.get_text() for p in fitz.open(O/'slides_with_appendix.pdf'))
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
v['pptx_xml_issues']=[]
with zipfile.ZipFile(O/'slides.pptx') as z:
 files=z.namelist(); slides=[p for p in files if __import__('re').fullmatch(r'ppt/slides/slide\d+.xml',p)]
 assert len(slides)==44
 notes=[p for p in files if __import__('re').fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',p)]
 assert len(notes)==44
 hidden=[];shapes=0;tables=0;textframes=0
 for i in range(1,45):
  s=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
  if s.attrib.get('show')=='0':hidden.append(i)
  for shape in s.find('p:cSld/p:spTree',ns):
   off=shape.find('.//a:off',ns);ext=shape.find('.//a:ext',ns)
   if off is None or ext is None:continue
   x,y=int(off.attrib['x']),int(off.attrib['y']);w,h=int(ext.attrib['cx']),int(ext.attrib['cy']);shapes+=1
   if x<0 or y<0 or x+w>12192002 or y+h>6858002:v['pptx_xml_issues'].append({'slide':i,'bounds_emu':[x,y,w,h]})
  tables+=len(s.findall('.//a:tbl',ns));textframes+=len(s.findall('.//p:txBody',ns))
 assert hidden==list(range(37,45))
 v['pptx_xml']={'slides':44,'notes':len(notes),'hidden_slide_ids':hidden,'checked_shapes':shapes,'editable_tables':tables,'editable_text_frames':textframes}
thumb=Image.new('RGB',(1600,2475),'#DAE2E6')
for i in range(44):
 im=Image.open(O/'preview'/f'slide-{i+1:02}.png');im.thumbnail((400,225));thumb.paste(im,((i%4)*400,(i//4)*225))
thumb.save(O/'preview/contact_sheet.jpg',quality=92)
v['status']='pass' if not any([v['python_layout_issues'],v['browser_issues'],v['pptx_xml_issues'],v['pdf_missing_replacement_glyph'],v['missing_images'],not v['keyboard_navigation']['pass'],not v['embedded_font_loaded'],not all(x['pass'] for x in v['responsive_browser'])]) else '要修正'
(N/'build_validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
print('PDF44枚全頁描画 / PPTX44枚XML検査:',v['status'])
