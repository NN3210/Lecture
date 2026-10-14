#!/usr/bin/env python3
"""第3回「測量の座標」のスライド（slides.md）から PPTX を生成する。

図は `materials/slides/第03回_測量の座標/diagrams/*.png`（`scripts/draw_session03_figures.py` で生成）を、
Markdown の `![代替文](diagrams/名前.svg)` 行の位置に埋め込む。第2回改訂版の build_session02_revised.py と同じ流儀。

使い方（Surveying/ を作業ディレクトリとして）:
    python scripts/build_session03.py
"""
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image
from pptx.util import Inches
from pptx.enum.text import MSO_ANCHOR
from pptx.dml.color import RGBColor
import md2pptx as m

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials/slides/第03回_測量の座標'
FIG = OUT / 'diagrams'
PPTX = OUT / 'slides.pptx'


class FigureBuilder(m.Builder):
    """`![alt](diagrams/x.svg)` を含むスライドは、本文を上段 2.1 インチに収め、下段に PNG を置く。"""

    def _write_runs(self, par, runs, size, color=None, bold=False):
        for text, fmt in runs:
            pos = 0
            for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
                super()._write_runs(par, [(text[pos:match.start()], fmt)], size, color, bold)
                before = len(par.runs)
                super()._write_runs(par, [(match[1], fmt)], size, RGBColor(0x13, 0x87, 0x7b), bold)
                for run in list(par.runs)[before:]:
                    run.hyperlink.address = match[2]
                pos = match.end()
            before = len(par.runs)
            super()._write_runs(par, [(text[pos:], fmt)], size, color, bold)
            if fmt.get('math'):
                for run in list(par.runs)[before:]:
                    run.font.name = 'DejaVu Sans'

    def add_slide(self, blocks, notes, directives, paginate):
        pics = [b for b in blocks if b['type'] == 'para' and re.fullmatch(r'!\[.*?\]\(.*?\.svg\)', b['text'])]
        if not pics:
            super().add_slide(blocks, notes, directives, paginate)
            return
        self.page += 1
        slide = self.prs.slides.add_slide(self.blank)
        title = next(b for b in blocks if b['type'] == 'heading')
        _, tf = self._textbox(slide, m.MARGIN, Inches(.35), m.SLIDE_W - 2 * m.MARGIN, m.TITLE_H)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        self._write_runs(tf.paragraphs[0], m.inline_to_runs(title['text']), 30, m.ACCENT, True)
        ln = slide.shapes.add_shape(1, m.MARGIN, Inches(1.3), m.SLIDE_W - 2 * m.MARGIN, Inches(.02))
        ln.fill.solid()
        ln.fill.fore_color.rgb = m.ACCENT
        ln.line.fill.background()
        body = [b for b in blocks if b is not title and b not in pics]
        n_lines = self._estimate_lines(body)
        size = 20 if n_lines <= 4 else 18
        self._place_body(slide, body, m.MARGIN, Inches(1.5), m.SLIDE_W - 2 * m.MARGIN, Inches(2.2), size)
        png = OUT / re.search(r'\((.*?)\)', pics[0]['text'])[1].replace('.svg', '.png')
        if not png.exists():
            raise FileNotFoundError(f'図がありません: {png}（scripts/draw_session03_figures.py を先に実行）')
        with Image.open(png) as im:
            w, h = im.size
        maxw, maxh = 12.0, 2.85
        scale = min(maxw / w, maxh / h)
        pw, ph = w * scale, h * scale
        pic = slide.shapes.add_picture(str(png), Inches((13.333 - pw) / 2), Inches(3.75 + (maxh - ph) / 2), Inches(pw), Inches(ph))
        pic._element.nvPicPr.cNvPr.set('descr', re.search(r'!\[(.*?)\]', pics[0]['text'])[1])
        self._footer(slide, paginate)
        self._notes(slide, notes)


def build():
    with tempfile.TemporaryDirectory(prefix='.build_session03_', dir=OUT) as scratch:
        tempfile.tempdir = scratch
        text = (OUT / 'slides.md').read_text(encoding='utf-8')
        meta, body = m.split_frontmatter(text)
        b = FigureBuilder('Noto Sans CJK JP', '測量学 第3回｜測量の座標')
        n_fig = 0
        for s in m.split_slides(body):
            md, notes, directives = m.extract_notes(s)
            blocks = m.parse_blocks(md)
            if not blocks and not notes:
                continue
            n_fig += any(b['type'] == 'para' and b['text'].startswith('![') for b in blocks)
            b.add_slide(blocks, notes, directives, True)
        b.save(str(PPTX))
        print(f'生成：{PPTX.name} {b.page} slides（図入り {n_fig} 枚）')


if __name__ == '__main__':
    build()
