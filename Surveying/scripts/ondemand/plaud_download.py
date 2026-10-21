#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PLAUD クラウドの録音一覧を表示し、選んだ録音（mp3）を手元に保存する。

audio2md パイプライン（C:/MyProjects/auto-tools/audio2md）の plaud_client と .env（PLAUD_TOKEN）を流用する。

使い方:
  python scripts/ondemand/plaud_download.py list [--limit 50] [--skip 0]
  python scripts/ondemand/plaud_download.py get <id> [<id> ...] --out ondemand/voice/raw

一覧の列: id  開始日時(ローカル)  長さ(分)  サイズ(MB)  ファイル名
保存名: <開始日時>_<id>.mp3（ondemand/voice/ は .gitignore 済み。本人の声は公開リポジトリに入れない）
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

AUDIO2MD = Path("C:/MyProjects/auto-tools/audio2md")


def load_token() -> str:
    sys.path.insert(0, str(AUDIO2MD))
    from pipeline.config import load_env  # type: ignore

    env = load_env(AUDIO2MD / ".env")
    tok = env.get("PLAUD_TOKEN", "")
    if tok.lower().startswith("bearer "):
        tok = tok[7:]
    if not tok:
        raise SystemExit(f"PLAUD_TOKEN が {AUDIO2MD / '.env'} にありません")
    return tok


def fmt_start(rec: dict) -> str:
    """start_time は UTC のミリ秒。timezone 欄（時間、日本なら 9）で録音地のローカル時刻に直す。"""
    ms = rec.get("start_time") or 0
    hours = rec.get("timezone")
    if not isinstance(hours, (int, float)):
        hours = 9
    t = dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone(dt.timedelta(hours=hours)))
    return t.strftime("%Y-%m-%d_%H%M")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("list")
    lp.add_argument("--limit", type=int, default=50)
    lp.add_argument("--skip", type=int, default=0)
    gp = sub.add_parser("get")
    gp.add_argument("ids", nargs="+")
    gp.add_argument("--out", default="ondemand/voice/raw")
    args = ap.parse_args()

    token = load_token()
    from pipeline import plaud_client as pc  # type: ignore

    if args.cmd == "list":
        recs = pc.list_recordings(token, limit=args.limit, skip=args.skip)
        print(f"{'id':26s} {'start':16s} {'min':>6s} {'MB':>6s}  filename")
        for r in recs:
            rid = r.get("id") or r.get("file_id") or "?"
            mins = (r.get("duration") or 0) / 60000
            mb = (r.get("filesize") or 0) / 1e6
            print(f"{str(rid):26s} {fmt_start(r):16s} {mins:6.1f} {mb:6.1f}  {r.get('filename', '')}")
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    recs = {str(r.get("id")): r for r in pc.list_recordings(token, limit=200)}
    for rid in args.ids:
        p = pc.download_recording(token, rid, out)
        rec = recs.get(rid)
        ext = sniff_ext(p)
        stem = f"{fmt_start(rec)}_{rid}" if rec else rid
        new = out / f"{stem}{ext}"
        p.replace(new)
        print(f"saved {new}  ({new.stat().st_size / 1e6:.1f} MB, {ext})")


def sniff_ext(path: Path) -> str:
    """PLAUD の『mp3』は実際には Ogg/Opus（48 kHz モノラル, 約 32 kbps）のことがある。中身で拡張子を決める。"""
    import subprocess

    try:
        fmt = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=format_name", "-of",
                              "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ".mp3"
    if "ogg" in fmt:
        return ".ogg"
    if "mp3" in fmt:
        return ".mp3"
    if "mp4" in fmt or "m4a" in fmt:
        return ".m4a"
    return ".mp3"


if __name__ == "__main__":
    main()
