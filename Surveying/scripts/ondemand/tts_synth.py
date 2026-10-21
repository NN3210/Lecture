#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""テキスト 1 本を音声 1 本にする（動作確認・短い案内文向け）。

使い方:
  python scripts/ondemand/tts_synth.py --engine edge --text "こんにちは" --out out.wav
  python scripts/ondemand/tts_synth.py --engine edge --text-file in.txt --out out.wav --voice ja-JP-NanamiNeural --rate -5%
  python scripts/ondemand/tts_synth.py --engine xtts --ref ondemand/voice/reference/xtts_ref_01.wav --text-file in.txt --out out.wav
  python scripts/ondemand/tts_synth.py --engine elevenlabs --voice <voice_id> --text-file in.txt --out out.wav

xtts は仮想環境 C:/Users/<user>/.venvs/ondemand-tts の python で実行する（ondemand/README.md 参照）。
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tts_backends import synthesize, wav_duration  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", default="edge", choices=["edge", "xtts", "elevenlabs"])
    ap.add_argument("--text", help="読み上げる文字列")
    ap.add_argument("--text-file", help="読み上げるテキストファイル（UTF-8）")
    ap.add_argument("--out", required=True, help="出力 WAV")
    ap.add_argument("--voice", help="edge: 音声名（既定 ja-JP-KeitaNeural）/ elevenlabs: voice_id")
    ap.add_argument("--rate", default="+0%", help="edge: 話速（例 -10%%, +5%%）")
    ap.add_argument("--pitch", default="+0Hz", help="edge: 高さ（例 -20Hz）")
    ap.add_argument("--ref", action="append", help="xtts: 参照音声 WAV（複数可）")
    ap.add_argument("--language", default="ja")
    ap.add_argument("--model-id", default="eleven_multilingual_v2", help="elevenlabs: モデル ID")
    ap.add_argument("--sr", type=int, default=24000)
    args = ap.parse_args()

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        ap.error("--text か --text-file を指定してください")
    text = text.strip()

    opts = dict(sr=args.sr, rate=args.rate, pitch=args.pitch, ref=args.ref, language=args.language,
                model_id=args.model_id)
    if args.voice:
        opts["voice"] = args.voice
    t0 = time.time()
    synthesize(args.engine, text, args.out, **opts)
    dur = wav_duration(args.out)
    el = time.time() - t0
    print(f"wrote {args.out}  audio {dur:.1f}s  elapsed {el:.1f}s  (x{el / max(dur, 0.01):.2f} realtime)")


if __name__ == "__main__":
    main()
