#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""動画の概要欄に貼る章立て（00:00 表紙 / 01:20 到達目標 …）を、台本と timings.json から作る（指南書 7 章）。

台本（narration.md）の各枚は

    ## 12
    <!-- 5-2 内角の和と測角誤差 -->
    本文…

の形で、`## N` の直後のコメントを枚の題名として使う。timings.json は build_video.py が
mp4 の隣に書く [{"slide": N, "start": 秒, "end": 秒, "speech": 秒}, ...]。

既定では題名の先頭の節番号（5-0、5-1 …）が変わる枚だけを章にする（番号の無い枚は単独の章）。
--per-slide で 64 枚すべてを出す。

使い方:
  python scripts/ondemand/make_chapters.py --narration <narration.md> --timings <out>.timings.json > chapters.md
  python scripts/ondemand/make_chapters.py --narration ... --timings ... --per-slide
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTION_RE = re.compile(r"^(\d+-\d+)\s*(.*)$")


def read_titles(narration: Path) -> dict[int, str]:
    """`## N` の直後の `<!-- 題名 -->` を枚番号 → 題名の辞書にする。コメントが無い枚は「スライド N」。"""
    titles: dict[int, str] = {}
    cur: int | None = None
    for line in narration.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(\d+)\s*$", line)
        if m:
            cur = int(m.group(1))
            titles.setdefault(cur, f"スライド {cur}")
            continue
        if cur is not None:
            m = re.match(r"^\s*<!--\s*(.*?)\s*-->\s*$", line)
            if m and titles.get(cur) == f"スライド {cur}":
                titles[cur] = m.group(1)
            elif line.strip():
                cur = None  # 本文に入ったらこの枚の題名は確定
    return titles


def fmt(sec: float, hours: bool) -> str:
    s = int(round(sec))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if hours else f"{m:02d}:{s:02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--timings", required=True, help="build_video.py が書いた <out>.timings.json")
    ap.add_argument("--per-slide", action="store_true", help="節ごとでなく全枚を出す")
    ap.add_argument("--keep-number", action="store_true", help="題名の節番号（5-1 等）を残す")
    args = ap.parse_args()

    titles = read_titles(Path(args.narration))
    timings = json.loads(Path(args.timings).read_text(encoding="utf-8"))
    total = max(t["end"] for t in timings)
    hours = total >= 3600

    rows: list[tuple[float, str]] = []
    prev_sec: str | None = None
    for t in timings:
        n = t["slide"]
        title = titles.get(n, f"スライド {n}")
        m = SECTION_RE.match(title)
        sec, name = (m.group(1), m.group(2) or title) if m else (None, title)
        if args.per_slide or sec is None or sec != prev_sec:
            label = title if args.keep_number or m is None else name
            rows.append((t["start"], label))
        prev_sec = sec

    for start, label in rows:
        print(f"{fmt(start, hours)} {label}")
    print(f"\n（全体 {fmt(total, hours)}、{len(timings)} 枚、{len(rows)} 章）", file=sys.stderr)


if __name__ == "__main__":
    main()
