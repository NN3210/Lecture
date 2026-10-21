#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""切り出した本人の発話区間（extract_speaker.py の出力）から、声の複製に使う参照音声を作る。

目的別の出力
  --target xtts   ローカル XTTS v2 用。類似度が高く 6〜20 秒の区間を上位 --n 本（既定 3）選び、
                  22.05 kHz モノラル WAV に整音して xtts_ref_01.wav … を書く
  --target ivc    ElevenLabs Instant Voice Clone 用。良い区間を --minutes 分（既定 2.5）まで連結し、
                  音量を整えて ivc_reference.mp3（192 kbps）を書く。3 分を超えないこと
  --target pvc    ElevenLabs Professional Voice Clone 用。良い区間を全部連結し、--chunk 分（既定 10）ごとの
                  pvc_part_01.mp3 … を書く（合計 30 分以上、できれば 1〜3 時間）

整音: ハイパス 80 Hz → （--denoise で afftdn の軽い雑音低減）→ loudnorm（I=-19 LUFS, TP=-3 dB）。
      区間間に 0.4 秒の無音を挟む。整音は控えめにし、雑音の多い区間は --min-sim で落とすほうが効く。

使い方（複数の録音日の segments フォルダーをまとめて渡せる）:
  python scripts/ondemand/prepare_reference.py --in ondemand/voice/segments/2026-10-01 ondemand/voice/segments/2026-10-03 \
      --out ondemand/voice/reference --target ivc --min-sim 0.55
"""
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

FFMPEG = "ffmpeg"


def read_index(folder: Path) -> list[dict]:
    rows = []
    with (folder / "index.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            r["path"] = folder / r["file"]
            r["dur_f"] = float(r["dur"])
            r["sim_f"] = float(r["sim"]) if r.get("sim") else None
            rows.append(r)
    return rows


def filt(x: str, denoise: bool) -> str:
    chain = ["highpass=f=80"]
    if denoise:
        chain.append("afftdn=nf=-25:nr=10")
    chain.append("loudnorm=I=-19:TP=-3:LRA=11")
    return ",".join(chain)


def concat_rows(rows: list[dict], out: Path, denoise: bool, mp3: bool, sr: int, gap: float = 0.4) -> None:
    lst = out.with_suffix(".txt")
    sil = out.parent / f"_silence_{int(gap * 1000)}ms.wav"
    if not sil.exists():
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono",
                        "-t", f"{gap:.2f}", str(sil)], check=True)
    tmp_dir = out.parent / "_tmp"
    tmp_dir.mkdir(exist_ok=True)
    lines = []
    for i, r in enumerate(rows):
        t = tmp_dir / f"{out.stem}_{i:04d}.wav"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(r["path"]), "-ac", "1", "-ar", str(sr), str(t)],
                       check=True)
        lines.append(f"file '{t.resolve().as_posix()}'")
        lines.append(f"file '{sil.resolve().as_posix()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
           "-af", filt("", denoise), "-ac", "1", "-ar", str(sr)]
    if mp3:
        cmd += ["-c:a", "libmp3lame", "-b:a", "192k"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True)
    for t in tmp_dir.glob(f"{out.stem}_*.wav"):
        t.unlink()
    lst.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inputs", nargs="+", required=True, help="extract_speaker.py の出力フォルダー")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", required=True, choices=["xtts", "ivc", "pvc"])
    ap.add_argument("--min-sim", type=float, default=None, help="この類似度未満の区間は使わない（sim 列がある場合）")
    ap.add_argument("--min-dur", type=float, default=3.0)
    ap.add_argument("--n", type=int, default=3, help="xtts: 参照本数")
    ap.add_argument("--minutes", type=float, default=2.5, help="ivc: 合計分")
    ap.add_argument("--chunk", type=float, default=10.0, help="pvc: 1 ファイルの分")
    ap.add_argument("--denoise", action="store_true")
    args = ap.parse_args()

    rows = []
    for d in args.inputs:
        rows += read_index(Path(d))
    n0 = len(rows)
    rows = [r for r in rows if r["dur_f"] >= args.min_dur]
    if args.min_sim is not None:
        rows = [r for r in rows if r["sim_f"] is None or r["sim_f"] >= args.min_sim]
    rows.sort(key=lambda r: (-(r["sim_f"] or 0.0), -r["dur_f"]))
    total = sum(r["dur_f"] for r in rows)
    print(f"区間 {n0} → {len(rows)} 本、合計 {total / 60:.1f} 分")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.target == "xtts":
        cand = [r for r in rows if 6.0 <= r["dur_f"] <= 20.0] or rows
        for i, r in enumerate(cand[: args.n], 1):
            dst = out / f"xtts_ref_{i:02d}.wav"
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(r["path"]), "-af", filt("", args.denoise),
                            "-ac", "1", "-ar", "22050", str(dst)], check=True)
            print(f"  {dst.name}  {r['dur_f']:.1f}s  sim={r['sim']}  {r['text'][:40]}")
        return

    if args.target == "ivc":
        sel, acc = [], 0.0
        for r in rows:
            if acc + r["dur_f"] > args.minutes * 60:
                continue
            sel.append(r)
            acc += r["dur_f"]
        sel.sort(key=lambda r: float(r["start"]))
        dst = out / "ivc_reference.mp3"
        concat_rows(sel, dst, args.denoise, mp3=True, sr=44100)
        print(f"  {dst}  {len(sel)} 本 {acc / 60:.1f} 分（IVC は 1〜3 分が目安）")
        return

    # pvc
    rows.sort(key=lambda r: (r["path"].parent.name, float(r["start"])))
    part, acc, k = [], 0.0, 0
    for r in rows + [None]:
        if r is None or acc + r["dur_f"] > args.chunk * 60:
            if part:
                k += 1
                dst = out / f"pvc_part_{k:02d}.mp3"
                concat_rows(part, dst, args.denoise, mp3=True, sr=44100)
                print(f"  {dst.name}  {len(part)} 本 {acc / 60:.1f} 分")
            part, acc = [], 0.0
        if r is not None:
            part.append(r)
            acc += r["dur_f"]
    print(f"  合計 {total / 60:.1f} 分（PVC は 30 分以上、できれば 1〜3 時間）")


if __name__ == "__main__":
    main()
