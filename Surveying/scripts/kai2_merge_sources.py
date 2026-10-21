#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第3回・改2 用：4 本の収集結果（Markdown 表）を統合し、通し番号を振り、
Codex に渡すバッチ一覧を作る。

使い方（Surveying/ で実行）:
    python scripts/kai2_merge_sources.py
出力:
    notes/session03_kai2_20261021/01_資料一覧.md
    notes/session03_kai2_20261021/codex/batches/batch_NN.md
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021")
FILES = [
    ("A", ROOT / "collect/資料収集_A_英語スライド.md"),
    ("B", ROOT / "collect/資料収集_B_英語動画.md"),
    ("C", ROOT / "collect/資料収集_C_日本語.md"),
    ("D", ROOT / "collect/資料収集_D_他言語.md"),
]
COLS = ["No.", "種別", "タイトル", "作成者（機関・チャンネル）", "言語", "年", "URL", "扱う話題", "長さ", "備考"]
BATCH_SIZE = 10


def parse_table(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        # `\|`（表内のエスケープされた縦棒）では区切らない
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) < 10 or cells[0] in ("No.", "") or set(cells[0]) <= set("-: "):
            continue
        rows.append(cells[:10])
    return rows


LANG_MAP = {
    "ja": "日本語", "jp": "日本語", "日": "日本語", "en": "英語", "英": "英語",
    "de": "ドイツ語", "独": "ドイツ語", "es": "スペイン語", "西": "スペイン語",
    "fr": "フランス語", "仏": "フランス語", "pt": "ポルトガル語", "葡": "ポルトガル語",
    "id": "インドネシア語", "尼": "インドネシア語", "ru": "ロシア語", "露": "ロシア語",
    "uk": "ウクライナ語", "烏": "ウクライナ語", "tr": "トルコ語", "土": "トルコ語",
    "zh": "中国語", "中": "中国語", "ko": "韓国語", "韓": "韓国語",
}
KIND_MAP = {"動画(再生リスト)": "動画", "動画/講義ページ（講義リスト）": "動画"}


def norm_url(u: str) -> str:
    u = re.sub(r"[<>]", "", u.strip())
    u = re.sub(r"&?(utm_[a-z]+|feature)=[^&]*", "", u)
    return u.rstrip("/").lower()


def main() -> None:
    merged: list[dict] = []
    seen: dict[str, int] = {}
    dup = 0
    for tag, path in FILES:
        if not path.exists():
            print(f"skip (missing): {path}")
            continue
        for cells in parse_table(path):
            key = norm_url(cells[6])
            if key in seen:
                dup += 1
                continue
            seen[key] = len(merged) + 1
            cells[1] = KIND_MAP.get(cells[1], cells[1])
            cells[4] = LANG_MAP.get(cells[4].strip().lower(), LANG_MAP.get(cells[4].strip(), cells[4]))
            merged.append({"src": f"{tag}-{cells[0]}", "cells": cells})

    lines = ["# 01 資料一覧（世界の測量学「座標系」講義資料・動画）", ""]
    lines.append(f"作成日：2026-10-21。収集方法は [手順書_01_資料収集.md](手順書/手順書_01_資料収集.md)。")
    lines.append(f"件数：{len(merged)} 件（URL 重複 {dup} 件を除外）。元の 4 ファイルは `collect/` にある。")
    lines.append("各件の「順番の抽出結果」は `codex/results/資料NNN.md`、統合は [02_各資料の構成抽出.md](02_各資料の構成抽出.md)。")
    lines.append("")
    kinds = Counter(r["cells"][1] for r in merged)
    langs = Counter(r["cells"][4] for r in merged)
    lines.append("| 種別 | 件数 |")
    lines.append("| --- | ---: |")
    for k, v in kinds.most_common():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("| 言語 | 件数 |")
    lines.append("| --- | ---: |")
    for k, v in langs.most_common():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("| " + " | ".join(["No.", "元"] + COLS[1:]) + " |")
    lines.append("|" + "---|" * (len(COLS) + 1))
    for i, r in enumerate(merged, 1):
        c = r["cells"]
        lines.append("| " + " | ".join([str(i), r["src"]] + c[1:]) + " |")
    (ROOT / "01_資料一覧.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    bdir = ROOT / "codex/batches"
    bdir.mkdir(parents=True, exist_ok=True)
    for old in bdir.glob("batch_*.md"):
        old.unlink()
    # 動画（字幕は yt-dlp＝シェル中心）と、それ以外（ブラウザー中心）に分けてバッチを作る。
    # 2 系統を並列に走らせても Chrome の取り合いが起きにくいようにするため。
    groups = {
        "v": [(i, r) for i, r in enumerate(merged, 1) if r["cells"][1] == "動画"],
        "p": [(i, r) for i, r in enumerate(merged, 1) if r["cells"][1] != "動画"],
    }
    nb = 0
    for g, items in groups.items():
        for b in range(0, len(items), BATCH_SIZE):
            chunk = items[b : b + BATCH_SIZE]
            n = b // BATCH_SIZE + 1
            out = ["| No. | 種別 | タイトル | 言語 | URL | 備考 |", "|---|---|---|---|---|---|"]
            for i, r in chunk:
                c = r["cells"]
                out.append(f"| {i} | {c[1]} | {c[2]} | {c[4]} | {c[6]} | {c[9]} |")
            (bdir / f"batch_{g}{n:02d}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
            nb += 1
    print(f"merged={len(merged)} dup={dup} batches={nb}")
    for k, v in kinds.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
