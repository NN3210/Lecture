#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PPTX の中の大きな画像を縮小・減色して、ファイルを 50 MB 以下に収める。

- 形式（PNG/JPEG）は変えない（rels・Content_Types を触らずに済む）。
- PNG は長辺を max_px に縮め、必要なら 256 色に減色（スクリーンショット向け）。
- JPEG は長辺を縮め、品質 quality で再保存。
- 元より大きくなる場合は置き換えない。

使い方:
    python -I scripts/pptx_compress_images.py <in.pptx> <out.pptx> [--max-px 1600] [--min-kb 300] [--quantize] [--quality 85]
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")


def shrink(data: bytes, ext: str, max_px: int, quantize: bool, quality: int) -> bytes | None:
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return None
    w, h = im.size
    scale = min(1.0, max_px / max(w, h))
    if scale < 1.0:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    if ext in ("png",):
        if quantize:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA")
            im = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        im.save(buf, format="PNG", optimize=True)
    elif ext in ("jpg", "jpeg"):
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(buf, format="JPEG", quality=quality, optimize=True)
    else:
        return None
    return buf.getvalue()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--min-kb", type=int, default=300, help="これより小さい画像は触らない")
    ap.add_argument("--quantize", action="store_true", help="PNG を 256 色に減色する")
    ap.add_argument("--quality", type=int, default=85)
    a = ap.parse_args()

    saved = 0
    n_changed = 0
    with zipfile.ZipFile(a.src) as zin, zipfile.ZipFile(a.dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("ppt/media/") and info.file_size > a.min_kb * 1024:
                ext = info.filename.rsplit(".", 1)[-1].lower()
                new = shrink(data, ext, a.max_px, a.quantize, a.quality)
                if new is not None and len(new) < len(data):
                    saved += len(data) - len(new)
                    n_changed += 1
                    print(f"  {info.filename.split('/')[-1]}: {len(data)/1e6:.2f} -> {len(new)/1e6:.2f} MB")
                    data = new
            zout.writestr(info.filename, data, compress_type=zipfile.ZIP_DEFLATED)
    import os
    print(f"changed {n_changed} images, saved {saved/1e6:.1f} MB; output {os.path.getsize(a.dst)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
