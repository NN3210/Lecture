#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""動画資料の情報（info.json）と字幕（vtt）を yt-dlp で先取りし、codex/cache/資料NNN/ に置く。

Codex のバッチ実行中に yt-dlp の字幕取得が HTTP 429 で落ちたため、Codex が読む前にこちらで取っておく。
YouTube の字幕は player_client=ios で取れる（android_vr は 429、web/mweb は PO Token 必須、tv は自動字幕が一覧に出ない）。
2 段階：(1) -J で情報を取り原語を決める → (2) 原語の自動字幕（xx-orig）と手動の ja/en だけを落とす。
取ったものは著作物なので commit しない（codex/.gitignore で cache/ を除外）。

使い方:
    python -I scripts/kai2_prefetch_subs.py v01 v02 ...   （バッチ ID。動画バッチのみ意味がある）
    python -I scripts/kai2_prefetch_subs.py --all          （batches/batch_v*.md を全部）
    done.txt がある資料は飛ばす。取り直したいときは done.txt を消す。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021/codex")
CACHE = ROOT / "cache"
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
    for k in subs:  # 手動字幕は原語・ja・en を優先して 2 つまで
        kl = k.lower()
        if (lang and kl.startswith(lang)) or kl.startswith(MANUAL_PREF):
            if k not in want and len([w for w in want if not w.endswith("-orig")]) < 2:
                want.append(k)
    return want


def fetch(no: int, url: str) -> str:
    out = CACHE / f"資料{no:03d}"
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
                json.dumps({"title": data.get("title"), "count": len(entries), "entries": entries},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            status = f"playlist {len(entries)} entries"
        except json.JSONDecodeError:
            pass
    else:
        # (1) 情報
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
        # (2) 字幕
        langs = choose_langs(info)
        if not langs:
            status = "info=ok subs=none(no captions on video)"
        else:
            rc2, _ = run(base + ["--no-playlist", "--skip-download", "--ignore-no-formats-error",
                                 "--write-sub", "--write-auto-sub", "--sub-langs", ",".join(langs),
                                 "--sub-format", "vtt/srv3/best", "--extractor-args", CLIENT,
                                 "--sleep-subtitles", "2", "-o", str(out / "v.%(ext)s"), url], log)
            vtts = sorted(p.name for p in out.glob("v.*.vtt"))
            status = f"info=ok subs={','.join(vtts) if vtts else 'none'} want={','.join(langs)} rc={rc2}"
    done.write_text(status + "\n", encoding="utf-8")
    return status


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args == ["--all"]:
        files = sorted((ROOT / "batches").glob("batch_v*.md"))
    else:
        files = [ROOT / "batches" / f"batch_{a}.md" for a in args]
    for bf in files:
        print(f"== {bf.name}", flush=True)
        for no, kind, title, url in rows(bf):
            if not is_youtube(url):
                print(f"  資料{no:03d}: not youtube, skip ({url})", flush=True)
                continue
            t0 = time.time()
            st = fetch(no, url)
            print(f"  資料{no:03d}: {st} ({time.time() - t0:.0f}s)", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
