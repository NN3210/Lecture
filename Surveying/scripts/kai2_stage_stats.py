#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""02_各資料の構成抽出.md の「段階コード列」を集計し、順序の傾向を数で出す。

使い方:
    python -I scripts/kai2_stage_stats.py            （Surveying/ で実行）
出力:
    notes/session03_kai2_20261021/codex/stage_stats.md

集計するもの:
- 段階コードごとの出現資料数と、列の中での平均相対位置（0=最初、1=最後）
- 最初の段階・2 番目の段階の分布、導入型の分布
- 隣接ペア（A→B）の出現回数（上位）
- 2 つのコードが同じ資料に出たとき、どちらが先に出るかの勝率（主要ペア）
- 種別（動画／スライド等）別・言語別の件数
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021")
SRC = ROOT / "02_各資料の構成抽出.md"
OUT = ROOT / "codex" / "stage_stats.md"
CODES = ["WHY", "COORD", "SHAPE", "GEOID", "HEIGHT", "LATLON", "ECEF", "DATUM", "TRANSFORM",
         "PROJ", "MAPPROJ", "TMUTM", "PLANE", "SCALE", "AXIS", "CALC", "GNSS", "LAW", "EX", "OTHER"]


def main() -> None:
    rows = []
    for ln in SRC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{3})\s*\|", ln)
        if not m:
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 9:
            continue
        no, title, kind, org, level, ok, nstage, intro, seq = c[:9]
        if not ok.startswith("OK"):
            continue
        codes = [s.strip() for s in re.split(r"→|->|＞|>", seq) if s.strip()]
        codes = [s for s in codes if s in CODES]
        if not codes:
            continue
        rows.append(dict(no=no, title=title, kind=kind, lang=kind, level=level, intro=intro, codes=codes))

    n = len(rows)
    occ = Counter()
    pos = defaultdict(list)
    first = Counter()
    second = Counter()
    intro = Counter()
    bigram = Counter()
    before = Counter()
    pair_n = Counter()
    kinds = Counter()
    langs = Counter()
    for r in rows:
        cs = r["codes"]
        dedup = []
        for c in cs:
            if c not in dedup:
                dedup.append(c)
        L = max(len(dedup) - 1, 1)
        for i, c in enumerate(dedup):
            occ[c] += 1
            pos[c].append(i / L)
        first[dedup[0]] += 1
        if len(dedup) > 1:
            second[dedup[1]] += 1
        intro[r["intro"]] += 1
        for a, b in zip(cs, cs[1:]):
            if a != b:
                bigram[(a, b)] += 1
        for i, a in enumerate(dedup):
            for b in dedup[i + 1:]:
                before[(a, b)] += 1
                pair_n[tuple(sorted((a, b)))] += 1
        k = r["kind"].split("・")[0]
        kinds[k] += 1
        parts = r["kind"].split("・")
        langs[parts[1] if len(parts) > 1 else "不明"] += 1

    out = [f"# 段階コードの集計（実在 OK で段階列のある {n} 件）", "",
           "元：`02_各資料の構成抽出.md` の一覧表。生成：`scripts/kai2_stage_stats.py`。", "",
           "## 1. 段階コードごとの出現数と平均位置（0=資料の最初、1=最後。同じコードの重複は 1 回に数える）", "",
           "| コード | 出現資料数 | 割合 | 平均位置 | 最初に来る件数 |", "| --- | --- | --- | --- | --- |"]
    for c in sorted(CODES, key=lambda c: (sum(pos[c]) / len(pos[c])) if pos[c] else 9):
        if occ[c]:
            out.append(f"| {c} | {occ[c]} | {occ[c] / n:.0%} | {sum(pos[c]) / len(pos[c]):.2f} | {first[c]} |")
    out += ["", "## 2. 最初の段階・2 番目の段階・導入型", "",
            "| 最初の段階 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in first.most_common()]
    out += ["", "| 2 番目の段階 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in second.most_common()]
    out += ["", "| 導入型 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in intro.most_common()]
    out += ["", "## 3. 隣接ペア A→B の出現回数（上位 40）", "", "| A→B | 回数 |", "| --- | --- |"]
    out += [f"| {a}→{b} | {k} |" for (a, b), k in bigram.most_common(40)]
    out += ["", "## 4. 同じ資料に両方出たとき、どちらが先か（主要ペア、件数 8 以上）", "",
            "| A | B | A が先 | B が先 | A が先の割合 |", "| --- | --- | --- | --- | --- |"]
    seen = set()
    rows4 = []
    for (a, b), k in pair_n.items():
        if k < 8 or (a, b) in seen:
            continue
        seen.add((a, b))
        ab, ba = before[(a, b)], before[(b, a)]
        rows4.append((max(ab, ba) / k, a if ab >= ba else b, b if ab >= ba else a, max(ab, ba), min(ab, ba)))
    for ratio, a, b, x, y in sorted(rows4, reverse=True):
        out.append(f"| {a} | {b} | {x} | {y} | {ratio:.0%} |")
    out += ["", "## 5. 種別・言語", "", "| 種別 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in kinds.most_common()]
    out += ["", "| 言語 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in langs.most_common()]
    out += ["", "## 6. 各資料の段階列（OK のみ、No. 順）", "", "| No | 段階列 |", "| --- | --- |"]
    out += [f"| {r['no']} | {'→'.join(r['codes'])} |" for r in rows]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT}: {n} 件")


if __name__ == "__main__":
    main()
