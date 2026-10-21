#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""codex/results/資料NNN.md の形を点検する（中身は読まない）。

使い方: python -I .claude/skills/lecture-structure-extract/scripts/check_results.py --root <root> [--min-stages 5 --max-stages 15]
報告すること:
  - 雛形の見出し 5 つ（扱う話題の順番／導入のしかた／段階どうしのつなぎ／分かりやすさの工夫／無い段階）と「実在確認」行の有無
  - 実在確認 OK / NG の件数
  - OK なのに「扱う話題の順番」の段階数が範囲外の件
  - 個人名らしき語（「教授」「先生」「Prof.」「Dr.」の直後に固有名詞）の疑い
見出しが欠ける件は、その No. だけ再実行バッチで取り直す（手で直さない）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HEADINGS = ["扱う話題の順番", "導入のしかた", "段階どうしのつなぎ", "分かりやすさの工夫", "無い段階"]
NAME_HINT = re.compile(r"(教授|先生|講師|Prof\.|Professor|Dr\.)\s*[A-Z][a-z]+|[一-龥]{1,2}\s*(教授|先生|講師)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--min-stages", type=int, default=5)
    ap.add_argument("--max-stages", type=int, default=15)
    a = ap.parse_args()
    rdir = Path(a.root) / "codex" / "results"
    files = sorted(rdir.glob("資料*.md"))
    if not files:
        sys.exit(f"結果ファイルが無い: {rdir}")
    ok = ng = unknown = 0
    bad_head: list[str] = []
    bad_stage: list[str] = []
    names: list[str] = []
    for f in files:
        t = f.read_text(encoding="utf-8")
        m = re.search(r"実在確認[：:]\s*(OK|NG)", t)
        if not m:
            unknown += 1
            bad_head.append(f"{f.stem}: 実在確認の行が無い")
            continue
        if m.group(1) == "NG":
            ng += 1
            continue
        ok += 1
        lack = [h for h in HEADINGS if not re.search(r"^##\s*.*" + re.escape(h), t, re.M)]
        if lack:
            bad_head.append(f"{f.stem}: 見出し欠け {lack}")
        sec = re.search(r"^##\s*.*扱う話題の順番\s*\n(.*?)(?=^##\s|\Z)", t, re.M | re.S)
        n = len(re.findall(r"^\s*\d+[.．)]\s", sec.group(1), re.M)) if sec else 0
        if n < a.min_stages or n > a.max_stages:
            bad_stage.append(f"{f.stem}: 段階数 {n}")
        if NAME_HINT.search(t):
            names.append(f.stem)
    print(f"結果 {len(files)} 件：OK {ok}、NG {ng}、実在確認なし {unknown}")
    print(f"見出し欠け {len(bad_head)} 件" + ("：" if bad_head else ""))
    for b in bad_head:
        print("  ", b)
    print(f"段階数が {a.min_stages}〜{a.max_stages} の外 {len(bad_stage)} 件" + ("：" if bad_stage else ""))
    for b in bad_stage:
        print("  ", b)
    if names:
        print(f"個人名の疑い {len(names)} 件（目で確認し、機関名に置き換える）: {', '.join(names)}")


if __name__ == "__main__":
    main()
