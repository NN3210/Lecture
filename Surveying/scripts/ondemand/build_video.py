#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ナレーション台本（narration.md）とスライド画像（PNG）から、音声付きの講義動画（mp4）と字幕（srt）を作る。

使い方:
  python scripts/ondemand/build_video.py --narration narration.md --png-dir preview --out work/lecture05.mp4 \
      [--engine edge|xtts|elevenlabs] [--voice ...] [--ref ref.wav ...] [--pad 0.8] [--size 1280x720] [--fps 10]
      [--work work/lecture05] [--only 3,5] [--dry-run]

入力:
  narration.md   '## N'（N はスライド番号、1 始まり）の下にそのスライドで話す文章。空の TODO 行は無視せず
                 「TODO」を含む段落があるスライドは警告して空音声（2 秒）にする。
  png-dir        PowerPoint の「スライド1.PNG」… か、連番を含む任意の PNG。名前中の数字で並べる。

出力:
  <out>.mp4      H.264 + AAC。各スライドはそのナレーションの長さ + pad 秒だけ表示される。
  <out>.srt      文単位の字幕（スライド内で文字数に比例して時刻を割り当てる近似）。
  <out>.timings.json  スライドごとの開始・終了秒（章立て・点検用）。
  work/          スライドごとの音声（slideNN.wav）。台本・エンジン・声が同じなら再利用し、変えた分だけ作り直す。

必要なもの: ffmpeg/ffprobe が PATH にあること。xtts は仮想環境の python で実行すること（ondemand/README.md）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tts_backends import FFMPEG, synthesize, wav_duration  # noqa: E402

HEADER_RE = re.compile(r"^##\s*(?:スライド\s*)?(\d+)\b.*$")
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?])\s*")


def parse_narration(path: Path) -> dict[int, str]:
    """'## N' 区切りで本文を取り出す。HTML コメントは除く。"""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    slides: dict[int, list[str]] = {}
    cur: int | None = None
    for line in text.splitlines():
        m = HEADER_RE.match(line.strip())
        if m:
            cur = int(m.group(1))
            slides.setdefault(cur, [])
            continue
        if line.startswith("# "):
            continue
        if cur is not None:
            slides[cur].append(line.rstrip())
    out: dict[int, str] = {}
    for n, lines in slides.items():
        body = "\n".join(lines).strip()
        body = re.sub(r"\n{3,}", "\n\n", body)
        out[n] = body
    return out


def list_pngs(png_dir: Path) -> dict[int, Path]:
    files = [p for p in png_dir.iterdir() if p.suffix.lower() == ".png"]
    mapped: dict[int, Path] = {}
    for p in files:
        nums = re.findall(r"\d+", p.stem)
        if not nums:
            continue
        mapped[int(nums[-1])] = p
    if not mapped:
        raise SystemExit(f"PNG が見つかりません: {png_dir}")
    return dict(sorted(mapped.items()))


def split_sentences(text: str) -> list[str]:
    parts = [s.strip() for s in SENT_SPLIT_RE.split(text.replace("\n", "")) if s.strip()]
    return parts or [text.strip()]


def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--png-dir", required=True)
    ap.add_argument("--out", required=True, help="出力 mp4")
    ap.add_argument("--engine", default="edge", choices=["edge", "xtts", "elevenlabs"])
    ap.add_argument("--voice", help="edge: 音声名 / elevenlabs: voice_id")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--pitch", default="+0Hz")
    ap.add_argument("--ref", action="append", help="xtts: 参照音声 WAV（複数可）")
    ap.add_argument("--model-id", default="eleven_multilingual_v2")
    ap.add_argument("--pad", type=float, default=0.8, help="各スライド末尾の無音（秒）")
    ap.add_argument("--lead", type=float, default=0.3, help="各スライド冒頭の無音（秒）")
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--work", help="作業フォルダー（既定: <out> と同じ場所の work_<名前>/）")
    ap.add_argument("--only", help="作り直すスライド番号（例 3,5）。他は再利用")
    ap.add_argument("--empty-sec", type=float, default=2.0, help="台本が無い/TODO のスライドの表示秒")
    ap.add_argument("--dry-run", action="store_true", help="台本と画像の対応だけ表示する")
    args = ap.parse_args()

    narration = parse_narration(Path(args.narration))
    pngs = list_pngs(Path(args.png_dir))
    out = Path(args.out)
    work = Path(args.work) if args.work else out.parent / f"work_{out.stem}"
    (work / "audio").mkdir(parents=True, exist_ok=True)
    w, h = (int(v) for v in args.size.lower().split("x"))

    missing = [n for n in pngs if n not in narration or not narration[n].strip()]
    todo = [n for n, t in narration.items() if "TODO" in t]
    extra = [n for n in narration if n not in pngs]
    print(f"slides(png)={len(pngs)} narration={len(narration)} 台本なし={missing} TODO={todo} 画像なし={extra}")
    if args.dry_run:
        for n, p in pngs.items():
            t = narration.get(n, "")
            print(f"  {n:3d} {p.name:24s} {len(t):4d}字  {t[:40].replace(chr(10), ' ')}")
        return

    only = {int(v) for v in args.only.split(",")} if args.only else None
    manifest_path = work / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    opts = dict(rate=args.rate, pitch=args.pitch, ref=args.ref, model_id=args.model_id)
    if args.voice:
        opts["voice"] = args.voice
    key_base = json.dumps({"engine": args.engine, "voice": args.voice, "rate": args.rate, "pitch": args.pitch,
                           "ref": args.ref, "model_id": args.model_id}, ensure_ascii=False, sort_keys=True)

    # 1. スライドごとの音声
    seg_files: list[tuple[int, Path, Path, float]] = []  # (n, png, padded_wav, speech_dur)
    for n, png in pngs.items():
        text = narration.get(n, "").strip()
        raw = work / "audio" / f"slide{n:02d}.wav"
        padded = work / "audio" / f"slide{n:02d}_padded.wav"
        if not text or "TODO" in text:
            speech = 0.0
            if not padded.exists() or (only and n in only):
                run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                     "-t", f"{args.empty_sec:.2f}", str(padded)])
            seg_files.append((n, png, padded, speech))
            continue
        key = hashlib.sha256((key_base + "\n" + text).encode("utf-8")).hexdigest()[:16]
        need = (manifest.get(str(n)) != key) or (not raw.exists()) or (only is not None and n in only)
        if need:
            print(f"[tts] slide {n} ({len(text)} 字) ...", flush=True)
            synthesize(args.engine, text, raw, **opts)
            manifest[str(n)] = key
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
            padded.unlink(missing_ok=True)
        speech = wav_duration(raw)
        if need or not padded.exists():
            total = args.lead + speech + args.pad
            run([FFMPEG, "-y", "-loglevel", "error", "-i", str(raw),
                 "-af", f"adelay={int(args.lead * 1000)}|{int(args.lead * 1000)},apad=whole_dur={total:.3f}",
                 "-ac", "1", "-ar", "24000", str(padded)])
        seg_files.append((n, png, padded, speech))

    # 2. 音声の連結と画像の表示時間
    audio_list = work / "audio_list.txt"
    image_list = work / "image_list.txt"
    timings = []
    t = 0.0
    a_lines, i_lines = [], []
    for n, png, padded, speech in seg_files:
        d = wav_duration(padded)
        a_lines.append(f"file '{padded.resolve().as_posix()}'")
        i_lines.append(f"file '{png.resolve().as_posix()}'")
        i_lines.append(f"duration {d:.3f}")
        timings.append({"slide": n, "start": round(t, 3), "end": round(t + d, 3), "speech": round(speech, 3)})
        t += d
    i_lines.append(f"file '{seg_files[-1][1].resolve().as_posix()}'")  # concat demuxer の仕様で最後をもう一度
    audio_list.write_text("\n".join(a_lines) + "\n", encoding="utf-8")
    image_list.write_text("\n".join(i_lines) + "\n", encoding="utf-8")
    all_wav = work / "all.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(audio_list), "-c", "copy", str(all_wav)])

    # 3. 動画
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=white,format=yuv420p")
    run([FFMPEG, "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(image_list),
         "-i", str(all_wav),
         "-vf", vf, "-r", str(args.fps), "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-crf", "20",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-t", f"{t:.3f}", str(out)])

    # 4. 字幕（文ごと、スライド内の文字数比で配分）と時刻表
    srt_lines = []
    idx = 1
    for (n, _png, _padded, speech), tm in zip(seg_files, timings):
        text = narration.get(n, "").strip()
        if not text or "TODO" in text or speech <= 0:
            continue
        sents = split_sentences(text)
        total_chars = sum(len(s) for s in sents) or 1
        cur = tm["start"] + args.lead
        for s in sents:
            d = speech * len(s) / total_chars
            srt_lines += [str(idx), f"{srt_time(cur)} --> {srt_time(cur + d)}", s, ""]
            idx += 1
            cur += d
    out.with_suffix(".srt").write_text("\n".join(srt_lines), encoding="utf-8")
    out.with_suffix(".timings.json").write_text(json.dumps(timings, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}  ({t / 60:.1f} 分, {len(seg_files)} slides)")
    print(f"wrote {out.with_suffix('.srt')}  {out.with_suffix('.timings.json')}")


if __name__ == "__main__":
    main()
