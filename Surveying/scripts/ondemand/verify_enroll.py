#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""find_self.py が選んだ enroll 用の区間を音声認識で読み直し、Circleback の文字起こしと合うか確かめる。

目的: auto_enroll.wav が「本当に人の発話」で、「文字起こしどおりの内容」かを、人が聞かなくても判定する。
2026-10-12 の録音のように、雑音を Circleback が英語の無意味な文に起こしていた場合、話者埋め込みは雑音どうしで
高い類似度を出してしまう。音声認識で読み直して文字起こしと一致すれば、その区間は発話であり切り出し位置も正しい。

使い方（仮想環境の python で）:
  python scripts/ondemand/verify_enroll.py --self-search ondemand/voice/self_search [--model small] [--whole]

読むもの: <self-search>/enroll_segments.json（find_self.py が書く。音声、区間、類似度、文字起こし）
         <self-search>/cache/<id>.16k.wav（find_self.py の 16 kHz キャッシュ。無ければ元の録音から ffmpeg で切る）
書くもの: <self-search>/enroll_check.md（区間ごとの一致率と認識結果。commit しない）
判定: 区間は Circleback 区間の一部（VAD で割ったもの）なので、CER ではなく「認識結果のローマ字のうち、文字起こしと
  3 文字以上つながって一致する割合（一致率）」で見る。0.5 以上なら「文字起こしどおりの発話」。
  --whole を付けると auto_enroll.wav 全体も認識して、文章になっているかを表示する。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HEX32 = re.compile(r"[0-9a-f]{32}")


def read_span(cache_dir: Path, audio: str, start: float, end: float, td: Path):
    """16 kHz キャッシュがあれば区間だけ読む。無ければ ffmpeg で切って読む。float32 の 1 次元配列を返す。"""
    import numpy as np
    import soundfile as sf

    m = HEX32.search(Path(audio).name)
    w16 = cache_dir / f"{m.group(0)}.16k.wav" if m else None
    if w16 and w16.exists():
        a, b = int(start * 16000), int(end * 16000)
        data, sr = sf.read(str(w16), start=a, stop=b, dtype="float32", always_2d=True)
        return data.mean(axis=1), sr
    cut = td / f"cut_{int(start)}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", audio,
                    "-ac", "1", "-ar", "16000", str(cut)], check=True)
    data, sr = sf.read(str(cut), dtype="float32", always_2d=True)
    return data.mean(axis=1), sr


def coverage(ref: str, hyp: str) -> float:
    """認識結果（hyp）のローマ字のうち、文字起こし（ref）と 3 文字以上つながって一致する割合（0〜1）。"""
    import difflib

    from check_asr import NORM

    r, h = NORM(ref), NORM(hyp)
    if not h:
        return 0.0
    sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks() if b.size >= 3) / len(h)


def transcribe(model, audio, sr: int) -> str:
    segs, _ = model.transcribe(audio, language="ja", beam_size=3, vad_filter=True, condition_on_previous_text=False)
    return "".join(s.text for s in segs).strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-search", default="ondemand/voice/self_search", help="find_self.py の出力フォルダー")
    ap.add_argument("--model", default="small", help="faster-whisper のモデル（small で約 470 MB）")
    ap.add_argument("--whole", action="store_true", help="auto_enroll.wav 全体も認識する")
    ap.add_argument("--min-cov", type=float, default=0.5, help="この一致率以上を「文字起こしどおり」と判定")
    args = ap.parse_args()

    from faster_whisper import WhisperModel

    ss = Path(args.self_search)
    segs = json.loads((ss / "enroll_segments.json").read_text(encoding="utf-8"))
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    lines = ["# enroll 区間の検証（音声認識で読み直し）", "",
             f"区間 {len(segs)}、モデル {args.model}、判定 一致率 ≥ {args.min_cov}", "",
             "| # | 録音 | 区間 | 類似度 | 一致率 | 判定 | Circleback | 認識結果 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        for k, s in enumerate(segs, 1):
            audio, sr = read_span(ss / "cache", s["audio"], s["start"], s["end"], Path(td))
            hyp = transcribe(model, audio, sr)
            c = coverage(s["text"], hyp)
            good = c >= args.min_cov and len(hyp) >= 5
            ok += good
            m = HEX32.search(Path(s["audio"]).name)
            pid = m.group(0)[:8] if m else Path(s["audio"]).stem[:8]
            lines.append(f"| {k} | {pid} | {s['start']:.1f}–{s['end']:.1f} | {s['sim']:.2f} | {c:.2f} | {'○' if good else '×'} "
                         f"| {s['text'][:60].replace('|', '／')} | {hyp[:60].replace('|', '／')} |")
            print(f"[{k}/{len(segs)}] {pid} {s['start']:.1f}-{s['end']:.1f} 一致率 {c:.2f} {'○' if good else '×'}  {hyp[:50]}", flush=True)
        lines += ["", f"文字起こしどおりの区間: {ok}/{len(segs)}", ""]
        if args.whole and (ss / "auto_enroll.wav").exists():
            import soundfile as sf

            data, sr = sf.read(str(ss / "auto_enroll.wav"), dtype="float32", always_2d=True)
            hyp = transcribe(model, data.mean(axis=1), sr)
            lines += ["## auto_enroll.wav 全体の認識結果", "", hyp, ""]
            print("auto_enroll.wav:", hyp[:200], flush=True)
    (ss / "enroll_check.md").write_text("\n".join(lines), encoding="utf-8")
    verdict = "合格" if ok >= max(1, round(0.7 * len(segs))) else "不合格（find_self.py の区間選びを見直す）"
    print(f"文字起こしどおりの区間 {ok}/{len(segs)} → {verdict}  （{ss / 'enroll_check.md'}）")


if __name__ == "__main__":
    main()
