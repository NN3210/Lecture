#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""codex/merged/*.md（Sonnet のバッチ圧縮）を No. 順に連結して <root>/02_各資料の構成抽出.md を作り、落ちた資料が無いか検算する。

使い方（科目のプロジェクト直下で実行）:
    python -I $SK/lecture-order-guideline/scripts/concat_merged.py --root <root> --codes <段階コード表.md> [--out <path>] [--date YYYY-MM-DD]
検算：codex/results/資料NNN.md にあるのに一覧に無い No. を標準出力に出す（Sonnet が落とした件。そのバッチをやり直す）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROW = re.compile(r"^\|\s*(\d{3})\s*\|")
SEC = re.compile(r"^### 資料(\d{3})")
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


def read_codes(path: Path) -> list[tuple[str, str]]:
    codes = [(m.group(1), m.group(2)) for ln in path.read_text(encoding="utf-8").splitlines() if (m := CODE_ROW.match(ln))]
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


def legend(codes: list[tuple[str, str]]) -> str:
    short = [f"{c} {re.split(r'[（(]', d)[0].strip()}" for c, d in codes]
    return "段階コード：" + "／".join(short) + "。\n導入型：問い／例／歴史／定義／目次／不明。"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--codes")
    ap.add_argument("--out")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    root = Path(a.root)
    merged = root / "codex" / "merged"
    out_path = Path(a.out) if a.out else root / "02_各資料の構成抽出.md"
    codes = read_codes(resolve_codes_path(root, a.codes))
    files = sorted(merged.glob("*.md"))
    if not files:
        sys.exit(f"merged ファイルがありません: {merged}")

    rows: dict[str, str] = {}
    secs: dict[str, list[str]] = {}
    header_line = ""
    for f in files:
        cur: str | None = None
        for ln in f.read_text(encoding="utf-8").splitlines():
            if ln.startswith("| No |") and not header_line:
                header_line = ln
            if ROW.match(ln) and cur is None:
                rows[ROW.match(ln).group(1)] = ln
                continue
            m = SEC.match(ln)
            if m:
                cur = m.group(1)
                secs[cur] = [ln]
                continue
            if cur is not None:
                if ln.startswith("## ") or ln.startswith("# "):
                    cur = None
                    continue
                secs[cur].append(ln)

    ok = sum(1 for r in rows.values() if "| OK |" in r or "| OK（" in r)
    ng = sum(1 for r in rows.values() if "| NG" in r)
    out = ["# 02 各資料の構成抽出（Codex の結果を Sonnet が圧縮し、No. 順に連結）", "",
           f"作成：{a.date}。元ファイル：`codex/results/資料NNN.md`（Codex の構成抽出）。圧縮：`codex/merged/*.md`（Sonnet、指示書 `codex/merge_instructions.md`）。",
           f"件数：{len(rows)}（実在確認 OK {ok}、NG {ng}）。NG の資料は一覧の行のみ。", "", legend(codes), "",
           "## 一覧（No. 順）", "",
           header_line or "| No | 題 | 種別・言語・長さ | 機関 | レベル | 実在 | 段階数 | 導入型 | 段階コード列 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    out += [rows[k] for k in sorted(rows)]
    out += ["", "## 各資料", ""]
    for k in sorted(secs):
        body = list(secs[k])
        while body and not body[-1].strip():
            body.pop()
        out += body + [""]
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{out_path}: 一覧 {len(rows)} 行、節 {len(secs)}、OK {ok}、NG {ng}、元 {len(files)} ファイル")

    # 検算：results にあるのに一覧に無い No.
    results = sorted(p.stem.replace("資料", "") for p in (root / "codex" / "results").glob("資料*.md"))
    missing = [n for n in results if n not in rows]
    extra = [n for n in rows if n not in results]
    print(f"results {len(results)} 件、一覧に無い No.: {missing if missing else 'なし'}")
    if extra:
        print(f"一覧にあるが results に無い No.: {extra}")
    # 段階数と段階コード列の個数の不一致
    bad = []
    for k, ln in rows.items():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) >= 9 and c[6].isdigit():
            seq = [s for s in re.split(r"→|->|＞|>", c[8]) if s.strip()]
            if seq and int(c[6]) != len(seq):
                bad.append(f"{k}({c[6]}/{len(seq)})")
    if bad:
        print(f"段階数と段階コード列の個数が違う行 {len(bad)} 件（Sonnet の省略。多ければやり直す）: {' '.join(bad[:20])}")


if __name__ == "__main__":
    main()
