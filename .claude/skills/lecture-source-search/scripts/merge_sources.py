#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""収集結果（Markdown 表、複数ファイル）を統合して通し番号を振り、01_資料一覧.md と Codex 用のバッチ一覧を作る。

使い方（科目のプロジェクト直下、例 Surveying/ で実行）:
    python -I .claude/skills/lecture-source-search/scripts/merge_sources.py --root notes/session05_traverse_20261101
    python -I .../merge_sources.py --root <root> --check        # 統合せず、各ファイルの行数・列不足・未確認・重複だけ報告
    オプション:
      --files A=collect/資料収集_A_英語スライド.md B=collect/資料収集_B_英語動画.md ...   （省略時は A〜D の既定 4 ファイル。無いものは飛ばす）
      --title "世界の測量学「トラバース測量」講義資料・動画"   （省略時は 00_設定.md の SUBJECT・TOPIC から作る）
      --batch-size 10
      --date 2026-11-01
出力:
    <root>/01_資料一覧.md
    <root>/codex/batches/batch_vNN.md（動画）、batch_pNN.md（文書）。既存の batch_v*/p* は作り直す（再実行バッチ batch_*r*.md は残す）
通し番号は以後の全段階で使うので、統合後は振り直さない。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

COLS = ["No.", "種別", "タイトル", "作成者（機関・チャンネル）", "言語", "年", "URL", "扱う話題", "長さ", "備考"]
DEFAULT_FILES = [("A", "collect/資料収集_A_英語スライド.md"), ("B", "collect/資料収集_B_英語動画.md"),
                 ("C", "collect/資料収集_C_日本語.md"), ("D", "collect/資料収集_D_他言語.md")]
LANG_MAP = {"ja": "日本語", "jp": "日本語", "日": "日本語", "en": "英語", "英": "英語",
            "de": "ドイツ語", "独": "ドイツ語", "es": "スペイン語", "西": "スペイン語", "fr": "フランス語", "仏": "フランス語",
            "pt": "ポルトガル語", "葡": "ポルトガル語", "id": "インドネシア語", "尼": "インドネシア語", "ru": "ロシア語", "露": "ロシア語",
            "uk": "ウクライナ語", "烏": "ウクライナ語", "tr": "トルコ語", "土": "トルコ語", "zh": "中国語", "中": "中国語",
            "ko": "韓国語", "韓": "韓国語", "it": "イタリア語", "伊": "イタリア語", "hi": "ヒンディー語", "ar": "アラビア語",
            "vi": "ベトナム語", "th": "タイ語", "pl": "ポーランド語", "nl": "オランダ語"}
KIND_MAP = {"動画(再生リスト)": "動画", "動画（再生リスト）": "動画", "動画/講義ページ（講義リスト）": "動画", "再生リスト": "動画"}
KEY_RE = re.compile(r"[（(]\s*([A-Z_]{3,})\b")


def read_config(root: Path) -> dict[str, str]:
    cfg = root / "00_設定.md"
    out: dict[str, str] = {}
    if not cfg.exists():
        return out
    for ln in cfg.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = KEY_RE.search(cells[0]) if len(cells) >= 2 else None
        if m:
            out[m.group(1)] = cells[1]
    return out


def split_row(line: str) -> list[str]:
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def parse_table(path: Path) -> tuple[list[list[str]], list[str]]:
    """10 列以上の本文行を返す。短い行は問題として別に返す。"""
    rows, problems = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if not cells or cells[0] in ("No.", "No", "") or set(cells[0]) <= set("-: "):
            continue
        if len(cells) < 10:
            problems.append(f"列不足（{len(cells)} 列）: {line[:80]}")
            continue
        rows.append(cells[:10])
    return rows, problems


def norm_url(u: str) -> str:
    u = re.sub(r"[<>]", "", u.strip())
    u = re.sub(r"&?(utm_[a-z]+|feature)=[^&]*", "", u)
    return u.rstrip("/").lower()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--files", nargs="*", help="TAG=path の並び（root からの相対）")
    ap.add_argument("--title")
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    root = Path(a.root)
    cfg = read_config(root)
    files = [(f.split("=", 1)[0], f.split("=", 1)[1]) for f in a.files] if a.files else DEFAULT_FILES
    title = a.title or f"世界の{cfg.get('SUBJECT', '')}「{cfg.get('TOPIC', '')}」講義資料・動画"

    merged: list[dict] = []
    seen: dict[str, int] = {}
    dup = 0
    for tag, rel in files:
        path = root / rel
        if not path.exists():
            print(f"skip (missing): {path}")
            continue
        rows, problems = parse_table(path)
        unconfirmed = sum(1 for r in rows if "未確認" in r[9])
        print(f"{tag}: {path.name} 行 {len(rows)}、列不足 {len(problems)}、未確認 {unconfirmed}")
        for p in problems[:5]:
            print("   ", p)
        for cells in rows:
            key = norm_url(cells[6])
            if key in seen:
                dup += 1
                print(f"    重複: {tag}-{cells[0]} は No.{seen[key]:03d} と同じ URL")
                continue
            seen[key] = len(merged) + 1
            cells[1] = KIND_MAP.get(cells[1], cells[1])
            cells[4] = LANG_MAP.get(cells[4].strip().lower(), LANG_MAP.get(cells[4].strip(), cells[4]))
            merged.append({"src": f"{tag}-{cells[0]}", "cells": cells})
    print(f"合計 {len(merged)} 件（重複 {dup} 件を除外）")
    if a.check:
        return

    kinds = Counter(r["cells"][1] for r in merged)
    langs = Counter(r["cells"][4] for r in merged)
    lines = [f"# 01 資料一覧（{title}）", ""]
    lines.append(f"作成日：{a.date}。収集方法は lecture-source-search スキル（共通指示は `collect/_収集指示.md`）。")
    lines.append(f"件数：{len(merged)} 件（URL 重複 {dup} 件を除外）。元の {len(files)} ファイルは `collect/` にある。")
    lines.append("各件の「順番の抽出結果」は `codex/results/資料NNN.md`、統合は [02_各資料の構成抽出.md](02_各資料の構成抽出.md)。")
    lines.append("")
    lines += ["| 種別 | 件数 |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in kinds.most_common()] + [""]
    lines += ["| 言語 | 件数 |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in langs.most_common()] + [""]
    lines.append("| " + " | ".join(["No.", "元"] + COLS[1:]) + " |")
    lines.append("|" + "---|" * (len(COLS) + 1))
    for i, r in enumerate(merged, 1):
        c = r["cells"]
        lines.append("| " + " | ".join([f"{i:03d}", r["src"]] + [x.replace("|", "\\|") for x in c[1:]]) + " |")
    out = root / "01_資料一覧.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    bdir = root / "codex" / "batches"
    bdir.mkdir(parents=True, exist_ok=True)
    for old in bdir.glob("batch_[vp][0-9][0-9].md"):
        old.unlink()
    groups = {"v": [(i, r) for i, r in enumerate(merged, 1) if r["cells"][1] == "動画"],
              "p": [(i, r) for i, r in enumerate(merged, 1) if r["cells"][1] != "動画"]}
    nb = 0
    for g, items in groups.items():
        for b in range(0, len(items), a.batch_size):
            chunk = items[b: b + a.batch_size]
            n = b // a.batch_size + 1
            rows = ["| No. | 種別 | タイトル | 言語 | URL | 備考 |", "|---|---|---|---|---|---|"]
            for i, r in chunk:
                c = r["cells"]
                rows.append(f"| {i} | {c[1]} | {c[2]} | {c[4]} | {c[6]} | {c[9]} |")
            (bdir / f"batch_{g}{n:02d}.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
            nb += 1
    print(f"書いた: {out}（{len(merged)} 件）、{bdir}/ にバッチ {nb} 本（動画 {len(groups['v'])} 件、文書 {len(groups['p'])} 件）")
    for k, v in kinds.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
