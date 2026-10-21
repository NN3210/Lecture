#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""途中で止まったバッチから、結果ファイルがまだ無い No. だけを集めた再実行バッチを作る。

使い方（科目のプロジェクト直下で実行）:
    python -I .claude/skills/lecture-structure-extract/scripts/make_rerun_batch.py --root <root> --status     欠けの一覧
    python -I .../make_rerun_batch.py --root <root> v03 v03r        batch_v03.md の欠けだけで batch_v03r.md を作る
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def missing(codex: Path, batch_id: str) -> tuple[list[str], list[int], list[int]]:
    src = codex / "batches" / f"batch_{batch_id}.md"
    keep, have, lack = [], [], []
    for ln in src.read_text(encoding="utf-8").splitlines():
        m = ROW.match(ln)
        if not m:
            keep.append(ln)
            continue
        no = int(m.group(1))
        if (codex / "results" / f"資料{no:03d}.md").exists():
            have.append(no)
        else:
            lack.append(no)
            keep.append(ln)
    return keep, have, lack


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("ids", nargs="*", help="<元バッチID> <新バッチID>")
    a = ap.parse_args()
    codex = Path(a.root) / "codex"
    if a.status or not a.ids:
        for f in sorted((codex / "batches").glob("batch_*.md")):
            bid = f.stem.replace("batch_", "")
            _, have, lack = missing(codex, bid)
            print(f"{bid}: 済 {len(have)} 欠 {len(lack)} {lack if lack else ''}")
        return
    if len(a.ids) != 2:
        sys.exit("<元バッチID> <新バッチID> の 2 つを指定する")
    src_id, new_id = a.ids
    keep, have, lack = missing(codex, src_id)
    if not lack:
        print(f"{src_id}: 欠けなし")
        return
    out = codex / "batches" / f"batch_{new_id}.md"
    out.write_text("\n".join(keep).replace(f"batch_{src_id}", f"batch_{new_id}") + "\n", encoding="utf-8")
    print(f"{out}: {len(lack)} 件 {lack}")


if __name__ == "__main__":
    main()
