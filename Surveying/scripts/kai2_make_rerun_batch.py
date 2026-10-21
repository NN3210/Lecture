#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""途中で止まったバッチから、結果ファイルがまだ無い No. だけを集めた再実行バッチを作る。

使い方:
    python -I scripts/kai2_make_rerun_batch.py <元バッチID> <新バッチID>     例: p02 p02r
    python -I scripts/kai2_make_rerun_batch.py --status                     全バッチの欠け一覧
元バッチの表の見出し行はそのまま写し、結果 `codex/results/資料NNN.md` が無い行だけ残す。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021/codex")
ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def missing(batch_id: str) -> tuple[list[str], list[int], list[int]]:
    src = ROOT / "batches" / f"batch_{batch_id}.md"
    lines = src.read_text(encoding="utf-8").splitlines()
    keep, have, lack = [], [], []
    for ln in lines:
        m = ROW.match(ln)
        if not m:
            keep.append(ln)
            continue
        no = int(m.group(1))
        if (ROOT / "results" / f"資料{no:03d}.md").exists():
            have.append(no)
        else:
            lack.append(no)
            keep.append(ln)
    return keep, have, lack


def main() -> None:
    a = sys.argv[1:]
    if a == ["--status"]:
        for f in sorted((ROOT / "batches").glob("batch_*.md")):
            bid = f.stem.replace("batch_", "")
            _, have, lack = missing(bid)
            print(f"{bid}: 済 {len(have)} 欠 {len(lack)} {lack if lack else ''}")
        return
    if len(a) != 2:
        sys.exit(__doc__)
    src_id, new_id = a
    keep, have, lack = missing(src_id)
    if not lack:
        print(f"{src_id}: 欠けなし")
        return
    out = ROOT / "batches" / f"batch_{new_id}.md"
    text = "\n".join(keep).replace(f"batch_{src_id}", f"batch_{new_id}")
    out.write_text(text + "\n", encoding="utf-8")
    print(f"{out}: {len(lack)} 件 {lack}")


if __name__ == "__main__":
    main()
