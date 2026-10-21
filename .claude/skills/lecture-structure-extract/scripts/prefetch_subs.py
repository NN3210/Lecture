#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""動画資料の情報（info.json）と字幕（vtt）を yt-dlp で先取りし、<root>/codex/cache/資料NNN/ に置く。

使い方（科目のプロジェクト直下で実行）:
    python -I .claude/skills/lecture-structure-extract/scripts/prefetch_subs.py --root notes/session05_traverse_20261101 v01 v02
    python -I .../prefetch_subs.py --root <root> --all        （codex/batches/batch_v*.md 全部）
done.txt がある資料は飛ばす（取り直すときは done.txt を消す）。
Codex のバッチと同時に走らせない（メモリ）。yt-dlp は player_client=ios 必須（他は 429 か PO Token 要求）。
キャッシュは著作物なので commit しない（codex/.gitignore で除外）。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CLIENT = "youtube:player_client=ios"
PER_ITEM_TIMEOUT = 420
YTDLP = shutil.which("yt-dlp") or "yt-dlp"
MANUAL_PREF = ("ja", "en")


def rows(batch_file: Path):
    for line in batch_file.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) < 5:
            continue
        yield int(cells[0]), cells[1], cells[2], cells[4]


def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def run(cmd: list[str], log: Path, capture: bool = False) -> tuple[int, str]:
    with log.open("a", encoding="utf-8") as f:
        f.write("$ " + " ".join(cmd) + "\n")
        f.flush()
        try:
            if capture:
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=f, timeout=PER_ITEM_TIMEOUT)
                out = p.stdout.decode("utf-8", errors="replace")
            else:
                p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=PER_ITEM_TIMEOUT)
                out = ""
            f.write(f"[exit {p.returncode}]\n")
            return p.returncode, out
        except subprocess.TimeoutExpired:
            f.write("[timeout]\n")
            return 124, ""


def choose_langs(info: dict) -> list[str]:
    """原語の自動字幕（-orig）を優先し、手動字幕は ja・en を最大 2 つ。"""
    ac = info.get("automatic_captions") or {}
    subs = info.get("subtitles") or {}
    origs = [k for k in ac if k.endswith("-orig")]
    lang = (info.get("language") or "").lower()
    want: list[str] = []
    if lang:
        want += [k for k in origs if k.lower().startswith(lang)]
    if not want:
        if len(origs) <= 2:
            want += origs
        else:
            en = [k for k in origs if k.lower().startswith("en")]
            want += en[:1] or origs[:1]
    for k in subs:
        kl = k.lower()
        if (lang and kl.startswith(lang)) or kl.startswith(MANUAL_PREF):
            if k not in want and len([w for w in want if not w.endswith("-orig")]) < 2:
                want.append(k)
    return want


def fetch(cache: Path, no: int, url: str) -> str:
    out = cache / f"資料{no:03d}"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "done.txt"
    if done.exists():
        return "skip: " + done.read_text(encoding="utf-8").strip()
    log = out / "yt-dlp.log"
    base = [YTDLP, "--no-update", "--no-warnings"]
    playlist = ("list=" in url and "v=" not in url) or "/playlist" in url
    if playlist:
        rc, js = run(base + ["--flat-playlist", "-J", url], log, capture=True)
        status = f"playlist-ng rc={rc}"
        try:
            data = json.loads(js)
            entries = [{"index": i + 1, "title": e.get("title"), "url": e.get("url"), "duration": e.get("duration")}
                       for i, e in enumerate(data.get("entries") or [])]
            (out / "playlist.json").write_text(
                json.dumps({"title": data.get("title"), "count": len(entries), "entries": entries}, ensure_ascii=False, indent=1),
                encoding="utf-8")
            status = f"playlist {len(entries)} entries"
        except json.JSONDecodeError:
            pass
    else:
        rc, js = run(base + ["--no-playlist", "--skip-download", "--ignore-no-formats-error", "-J",
                             "--extractor-args", CLIENT, url], log, capture=True)
        try:
            info = json.loads(js)
        except json.JSONDecodeError:
            done.write_text(f"info-ng rc={rc}\n", encoding="utf-8")
            return f"info-ng rc={rc}"
        slim = {k: info.get(k) for k in ("id", "title", "channel", "uploader", "duration", "duration_string",
                                         "upload_date", "language", "description", "chapters", "categories", "tags")}
        slim["caption_langs"] = {"automatic": sorted(info.get("automatic_captions") or {}),
                                 "manual": sorted(info.get("subtitles") or {})}
        (out / "v.info.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
        langs = choose_langs(info)
        if not langs:
            status = "info=ok subs=none(no captions on video)"
        else:
            rc2, _ = run(base + ["--no-playlist", "--skip-download", "--ignore-no-formats-error",
                                 "--write-sub", "--write-auto-sub", "--sub-langs", ",".join(langs),
                                 "--sub-format", "vtt/srv3/best", "--extractor-args", CLIENT, "--sleep-subtitles", "2",
                                 "-o", str(out / "v.%(ext)s"), url], log)
            vtts = sorted(p.name for p in out.glob("v.*.vtt"))
            status = f"info=ok subs={','.join(vtts) if vtts else 'none'} want={','.join(langs)} rc={rc2}"
    done.write_text(status + "\n", encoding="utf-8")
    return status


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="作業ディレクトリ（codex/ の親）")
    ap.add_argument("--all", action="store_true", help="batch_v*.md を全部")
    ap.add_argument("ids", nargs="*", help="バッチ ID（v01 など）")
    a = ap.parse_args()
    codex = Path(a.root) / "codex"
    cache = codex / "cache"
    if a.all:
        files = sorted((codex / "batches").glob("batch_v*.md"))
    elif a.ids:
        files = [codex / "batches" / f"batch_{i}.md" for i in a.ids]
    else:
        sys.exit("バッチ ID か --all を指定する")
    for bf in files:
        if not bf.exists():
            print(f"無い: {bf}")
            continue
        print(f"== {bf.name}", flush=True)
        for no, kind, title, url in rows(bf):
            if not is_youtube(url):
                print(f"  資料{no:03d}: not youtube, skip ({url})", flush=True)
                continue
            t0 = time.time()
            st = fetch(cache, no, url)
            print(f"  資料{no:03d}: {st} ({time.time() - t0:.0f}s)", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
