#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""2 つ以上の音声ファイルの話者類似度（コサイン類似度）を表にする。

用途
  - 合成した音声（XTTS / ElevenLabs）が本人の声（enroll）にどれだけ近いかを数値で見る
  - 切り出した区間や参照音声に他人の声が混ざっていないかを確かめる

使い方（仮想環境の python で）:
  python scripts/ondemand/voice_similarity.py ondemand/voice/enroll/enroll.wav out_xtts.wav out_eleven.wav
  python scripts/ondemand/voice_similarity.py --ref ondemand/voice/enroll/enroll.wav ondemand/voice/segments/2026-10-01/seg_*.wav

目安（speechbrain ECAPA, VoxCeleb 学習）: 同一人物の実録音どうしで 0.5〜0.9、別人で 0.3 未満が普通。
合成音声と本人の録音は 0.5 以上なら「似ている」、0.7 以上なら「かなり似ている」と判断する。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ref", help="基準の音声。指定すると基準との類似度だけを一覧にする（総当たりにしない）")
    args = ap.parse_args()

    from extract_speaker import Embedder  # noqa: E402

    emb = Embedder()
    paths = [Path(p) for p in args.files]
    if args.ref:
        ref = emb.embed_file(Path(args.ref))
        print(f"基準: {args.ref}")
        for p in paths:
            e = emb.embed_file(p)
            print(f"  {float((e * ref).sum()):6.3f}  {p}")
        return
    embs = [emb.embed_file(p) for p in paths]
    names = [p.name for p in paths]
    w = max(len(n) for n in names)
    print(" " * (w + 2) + "  ".join(f"{n[:8]:>8s}" for n in names))
    for i, a in enumerate(embs):
        row = "  ".join(f"{float((a * b).sum()):8.3f}" for b in embs)
        print(f"{names[i]:{w}s}  {row}")


if __name__ == "__main__":
    main()
