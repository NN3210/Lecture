#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""02_各資料の構成抽出.md の「段階コード列」を集計し、順序の傾向を数で出す。

使い方（科目のプロジェクト直下で実行）:
    python -I $SK/lecture-order-guideline/scripts/stage_stats.py --root <root> --codes <段階コード表.md> [--min-pair 8] [--out <path>]
出力（既定）: <root>/codex/stage_stats.md

集計するもの:
- 段階コードごとの出現資料数と、列の中での平均相対位置（0=最初、1=最後）
- 最初の段階・2 番目の段階の分布、導入型の分布
- 隣接ペア（A→B）の出現回数（上位 40）
- 2 つのコードが同じ資料に出たとき、どちらが先に出るかの勝率（件数 --min-pair 以上）
- 種別（動画／スライド等）別・言語別の件数
- 各資料の段階列（骨格の型分けの材料）
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
CODE_ROW = re.compile(r"^\|\s*([A-Z][A-Z0-9_]*)\s*\|\s*(.*?)\s*\|\s*$")
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


def read_codes(path: Path) -> list[str]:
    codes = [m.group(1) for ln in path.read_text(encoding="utf-8").splitlines() if (m := CODE_ROW.match(ln))]
    if not codes:
        sys.exit(f"段階コードの行が無い: {path}")
    return codes


def resolve_codes_path(root: Path, arg: str | None) -> Path:
    if arg:
        return Path(arg)
    val = read_config(root).get("CODES", "").strip("`").strip()
    if not val:
        sys.exit("--codes を指定するか、00_設定.md の CODES にパスを書く")
    p = Path(val)
    if p.exists():
        return p
    p2 = HERE.parent / "references" / Path(val).name
    if p2.exists():
        return p2
    sys.exit(f"段階コード表が見つからない: {val}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--codes")
    ap.add_argument("--src", help="既定 <root>/02_各資料の構成抽出.md")
    ap.add_argument("--out", help="既定 <root>/codex/stage_stats.md")
    ap.add_argument("--min-pair", type=int, default=8)
    a = ap.parse_args()
    root = Path(a.root)
    src = Path(a.src) if a.src else root / "02_各資料の構成抽出.md"
    out_path = Path(a.out) if a.out else root / "codex" / "stage_stats.md"
    CODES = read_codes(resolve_codes_path(root, a.codes))

    rows = []
    unknown = Counter()
    for ln in src.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{3})\s*\|", ln)
        if not m:
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 9:
            continue
        no, title, kind, org, level, ok, nstage, intro, seq = c[:9]
        if not ok.startswith("OK"):
            continue
        raw = [s.strip() for s in re.split(r"→|->|＞|>", seq) if s.strip()]
        codes = [s for s in raw if s in CODES]
        for s in raw:
            if s not in CODES:
                unknown[s] += 1
        if not codes:
            continue
        rows.append(dict(no=no, title=title, kind=kind, intro=intro, codes=codes))

    n = len(rows)
    if n == 0:
        sys.exit(f"段階列のある OK 行が無い: {src}")
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
        for x, y in zip(cs, cs[1:]):
            if x != y:
                bigram[(x, y)] += 1
        for i, x in enumerate(dedup):
            for y in dedup[i + 1:]:
                before[(x, y)] += 1
                pair_n[tuple(sorted((x, y)))] += 1
        parts = r["kind"].split("・")
        kinds[parts[0]] += 1
        langs[parts[1] if len(parts) > 1 else "不明"] += 1

    out = [f"# 段階コードの集計（実在 OK で段階列のある {n} 件）", "",
           f"元：`{src.name}` の一覧表。生成：lecture-order-guideline/scripts/stage_stats.py。", "",
           "## 1. 段階コードごとの出現数と平均位置（0=資料の最初、1=最後。同じコードの重複は 1 回に数える）", "",
           "| コード | 出現資料数 | 割合 | 平均位置 | 最初に来る件数 |", "| --- | --- | --- | --- | --- |"]
    for c in sorted(CODES, key=lambda c: (sum(pos[c]) / len(pos[c])) if pos[c] else 9):
        if occ[c]:
            out.append(f"| {c} | {occ[c]} | {occ[c] / n:.0%} | {sum(pos[c]) / len(pos[c]):.2f} | {first[c]} |")
    out += ["", "## 2. 最初の段階・2 番目の段階・導入型", "", "| 最初の段階 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in first.most_common()]
    out += ["", "| 2 番目の段階 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in second.most_common()]
    out += ["", "| 導入型 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in intro.most_common()]
    out += ["", "## 3. 隣接ペア A→B の出現回数（上位 40）", "", "| A→B | 回数 |", "| --- | --- |"]
    out += [f"| {x}→{y} | {k} |" for (x, y), k in bigram.most_common(40)]
    out += ["", f"## 4. 同じ資料に両方出たとき、どちらが先か（主要ペア、件数 {a.min_pair} 以上）", "",
            "| A | B | A が先 | B が先 | A が先の割合 |", "| --- | --- | --- | --- | --- |"]
    rows4 = []
    for (x, y), k in pair_n.items():
        if k < a.min_pair:
            continue
        xy, yx = before[(x, y)], before[(y, x)]
        rows4.append((max(xy, yx) / k, x if xy >= yx else y, y if xy >= yx else x, max(xy, yx), min(xy, yx)))
    for ratio, x, y, p, q in sorted(rows4, reverse=True):
        out.append(f"| {x} | {y} | {p} | {q} | {ratio:.0%} |")
    out += ["", "## 5. 種別・言語", "", "| 種別 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in kinds.most_common()]
    out += ["", "| 言語 | 件数 |", "| --- | --- |"]
    out += [f"| {c} | {k} |" for c, k in langs.most_common()]
    out += ["", "## 6. 各資料の段階列（OK のみ、No. 順）", "", "| No | 段階列 |", "| --- | --- |"]
    out += [f"| {r['no']} | {'→'.join(r['codes'])} |" for r in rows]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{out_path}: {n} 件")
    if unknown:
        print(f"コード表に無い語（無視した）: {dict(unknown.most_common(10))}")


if __name__ == "__main__":
    main()
