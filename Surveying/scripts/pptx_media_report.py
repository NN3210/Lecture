#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PPTX の中のメディア（画像など）の大きさを一覧し、どの枚がどの画像を使っているかを出す。

使い方:
    python -I scripts/pptx_media_report.py <pptx> [上位件数]
"""
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
path = Path(sys.argv[1])
top = int(sys.argv[2]) if len(sys.argv) > 2 else 25

with zipfile.ZipFile(path) as z:
    infos = {i.filename: i for i in z.infolist()}
    media = [(i.file_size, i.filename) for i in z.infolist() if i.filename.startswith("ppt/media/")]
    media.sort(reverse=True)
    total = sum(s for s, _ in media)
    print(f"file: {path.name}  zip size: {path.stat().st_size/1e6:.1f} MB  media: {len(media)} files, {total/1e6:.1f} MB uncompressed")
    # 画像 → 使っている枚
    users = defaultdict(set)
    for name in infos:
        if name.startswith("ppt/slides/_rels/slide") and name.endswith(".rels"):
            sld = name.split("/")[-1].replace(".rels", "")
            xml = z.read(name).decode("utf-8", "ignore")
            for s, m in media:
                if m.split("/")[-1] in xml:
                    users[m].add(sld)
    by_ext = defaultdict(lambda: [0, 0])
    for s, m in media:
        ext = m.rsplit(".", 1)[-1].lower()
        by_ext[ext][0] += 1
        by_ext[ext][1] += s
    for ext, (n, s) in sorted(by_ext.items(), key=lambda kv: -kv[1][1]):
        print(f"  .{ext}: {n} files, {s/1e6:.1f} MB")
    print()
    print("| 順 | ファイル | MB | 使っている枚 |")
    print("|---|---|---|---|")
    for k, (s, m) in enumerate(media[:top], 1):
        print(f"| {k} | {m.split('/')[-1]} | {s/1e6:.2f} | {', '.join(sorted(users[m], key=lambda x: int(x.replace('slide','').replace('.xml','')) if x.replace('slide','').replace('.xml','').isdigit() else 0)) or '（未使用）'} |")
    unused = [m for s, m in media if not users[m]]
    print(f"\n未使用メディア: {len(unused)} 件, {sum(s for s, m in media if not users[m])/1e6:.1f} MB")
