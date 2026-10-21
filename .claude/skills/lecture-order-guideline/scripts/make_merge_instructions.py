#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""段階コード表を埋めた「結果統合の指示（Sonnet 用）」を <root>/codex/merge_instructions.md に作る。

使い方（科目のプロジェクト直下で実行）:
    python -I $SK/lecture-order-guideline/scripts/make_merge_instructions.py --root <root> --codes <段階コード表.md> [--force]
    python -I .../make_merge_instructions.py --root <root> --list-batches     Sonnet 起動プロンプト用に、バッチごとの No. 列を出す
段階コード表は `| コード | 内容 |` の表（references/stage_codes_*.md）。--codes を省くと 00_設定.md の CODES を使う。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "references" / "merge_instructions_template.md"
KEY_RE = re.compile(r"[（(]\s*([A-Z_]{3,})\b")
CODE_ROW = re.compile(r"^\|\s*([A-Z][A-Z0-9_]*)\s*\|\s*(.*?)\s*\|\s*$")


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
    codes: list[tuple[str, str]] = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = CODE_ROW.match(ln)
        if m:
            codes.append((m.group(1), m.group(2)))
    if not codes:
        sys.exit(f"段階コードの行（| CODE | 内容 |）が無い: {path}")
    return codes


def resolve_codes_path(root: Path, arg: str | None) -> Path:
    if arg:
        return Path(arg)
    val = read_config(root).get("CODES", "")
    val = val.strip("`").strip()
    if not val:
        sys.exit("--codes を指定するか、00_設定.md の CODES にパスを書く")
    p = Path(val)
    if not p.exists():
        p2 = HERE.parent / "references" / Path(val).name
        if p2.exists():
            return p2
        sys.exit(f"段階コード表が見つからない: {val}")
    return p


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--codes")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list-batches", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    if a.list_batches:
        for p in sorted((root / "codex" / "batches").glob("batch_*.md")):
            nums = [m.group(1) for m in re.finditer(r"^\|\s*(\d+)\s*\|", p.read_text(encoding="utf-8"), re.M)]
            print(f"{p.stem.replace('batch_', '')}: {len(nums)} 件 {'、'.join(nums)}")
        return
    codes = read_codes(resolve_codes_path(root, a.codes))
    table = "\n".join(["| コード | 内容 |", "| --- | --- |"] + [f"| {c} | {d} |" for c, d in codes])
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("{{CODES_TABLE}}", table).replace("{{ROOT}}", a.root.replace("\\", "/").rstrip("/"))
    out = root / "codex" / "merge_instructions.md"
    if out.exists() and not a.force:
        sys.exit(f"既にある（--force で上書き）: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{out}: 段階コード {len(codes)} 個（{', '.join(c for c, _ in codes)}）")


if __name__ == "__main__":
    main()
