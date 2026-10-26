"""本編後の付録を通常上映から外す。元の生成候補は保持。"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
import re
folder=Path(__file__).parent/'kai2/build'
with ZipFile(folder/'candidate.pptx') as src,ZipFile(folder/'candidate_hidden.pptx','w',ZIP_DEFLATED) as dst:
    for name in src.namelist():
        data=src.read(name)
        match=re.fullmatch(r'ppt/slides/slide(\d+)\.xml',name)
        if match and int(match.group(1))>50:
            xml=etree.fromstring(data);xml.set('show','0')
            data=etree.tostring(xml,encoding='UTF-8',xml_declaration=True,standalone=True)
        if name=='ppt/notesSlides/notesSlide5.xml':
            data=data.replace('各節の右上に今いる段階を示します。'.encode('utf-8'),'各ページ上部に今いる節名を示します。'.encode('utf-8'))
        dst.writestr(name,data)
print('51–63枚を通常上映で非表示に設定（別候補ファイル）')
