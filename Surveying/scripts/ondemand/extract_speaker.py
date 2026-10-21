#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""会議録音（他の人の声が混ざる）から本人の発話区間だけを切り出す。

材料
  --audio      PLAUD からダウンロードした mp3（plaud_download.py）
  --segments   Circleback の文字起こし JSON（circleback_transcript.py fetch <linkId> --json）。
               segments[].speaker / start / end / text を使う（話者分離は Circleback 済み）
  --enroll     本人の声だけの短い WAV（30 秒〜）。あれば話者埋め込みの類似度で本人の Participant を自動判定する
  --participant  自動判定を使わず "Participant 2" のように指定する

手順
  1. 話者ごとの発話量を表にする（装着者はマイクに最も近いので通常は最多）
  2. --enroll があれば speechbrain の ECAPA 埋め込みで各話者との類似度を出し、最も近い話者を選ぶ
  3. 選んだ話者の区間を元の mp3 から切り出し（min-dur 秒以上、前後 0.1 秒の余白）、
     区間ごとの類似度（他人の声の混入・重なりの検出用）を index.csv に書く

使い方（仮想環境の python で）:
  python scripts/ondemand/extract_speaker.py --audio ondemand/voice/raw/2026-10-01_0900_xxx.mp3 \
      --segments C:/MyProjects/auto-tools/audio2md/data/transcripts/2026-10-01_12345678.json \
      --out ondemand/voice/segments/2026-10-01 --enroll ondemand/voice/enroll/enroll.wav
  python scripts/ondemand/extract_speaker.py ... --stats-only      # 表だけ見る
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = "ffmpeg"


def to_wav16k(src: Path, dst: Path) -> None:
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "16000", str(dst)], check=True)


def cut(src: Path, dst: Path, start: float, end: float, margin: float = 0.1) -> None:
    s = max(0.0, start - margin)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{s:.3f}", "-to", f"{end + margin:.3f}",
                    "-i", str(src), "-ac", "1", str(dst)], check=True)


def load_segments(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    segs = d.get("segments") if isinstance(d, dict) else d
    out = []
    for s in segs:
        try:
            out.append({"speaker": s["speaker"], "start": float(s["start"]), "end": float(s["end"]),
                        "text": s.get("text", "")})
        except (KeyError, TypeError, ValueError):
            continue
    return out


class Embedder:
    def __init__(self) -> None:
        import torch
        import torchaudio  # noqa: F401

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from audio_io import patch_torchaudio_load  # torchcodec 不要にする（audio_io.py 参照）

        patch_torchaudio_load()
        from speechbrain.inference.speaker import EncoderClassifier
        from speechbrain.utils.fetching import LocalStrategy

        self.torch = torch
        # Windows はシンボリックリンク作成に特権が要るので COPY にする（既定の SYMLINK は OSError になる）
        savedir = Path.home() / ".cache" / "speechbrain" / "spkrec-ecapa-voxceleb"
        self.model = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                                    savedir=str(savedir),
                                                    local_strategy=LocalStrategy.COPY,
                                                    run_opts={"device": "cpu"})

    def embed_file(self, wav: Path):
        import torchaudio

        sig, sr = torchaudio.load(str(wav))
        if sr != 16000:
            sig = torchaudio.functional.resample(sig, sr, 16000)
        if sig.shape[0] > 1:
            sig = sig.mean(0, keepdim=True)
        with self.torch.no_grad():
            e = self.model.encode_batch(sig).squeeze()
        return e / (e.norm() + 1e-9)

    def embed_span(self, wav16k, sr, start: float, end: float):
        a, b = int(start * sr), int(end * sr)
        sig = wav16k[:, a:b]
        if sig.shape[1] < sr // 2:
            return None
        with self.torch.no_grad():
            e = self.model.encode_batch(sig).squeeze()
        return e / (e.norm() + 1e-9)

    def embed_span_file(self, wav16k_path: Path, start: float, end: float):
        """16 kHz モノラル WAV の該当区間だけをディスクから読んで埋め込む。
        録音全体をメモリに載せない（3 時間の録音を丸ごと読むと 1 GB を超え、メモリ 16 GB の PC では他の作業を止める）。"""
        import soundfile as sf

        sr = 16000
        a, b = int(start * sr), int(end * sr)
        if b - a < sr // 2:
            return None
        data, file_sr = sf.read(str(wav16k_path), start=a, stop=b, dtype="float32", always_2d=True)
        if file_sr != sr or data.shape[0] < sr // 2:
            return None
        sig = self.torch.from_numpy(data.mean(axis=1)).unsqueeze(0)
        with self.torch.no_grad():
            e = self.model.encode_batch(sig).squeeze()
        return e / (e.norm() + 1e-9)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--segments", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--enroll", help="本人の声だけの WAV")
    ap.add_argument("--participant", help="話者ラベルを直接指定")
    ap.add_argument("--min-dur", type=float, default=2.0, help="切り出す区間の最短秒")
    ap.add_argument("--max-dur", type=float, default=20.0, help="これより長い区間は先頭 max-dur 秒だけ使う")
    ap.add_argument("--max-total", type=float, default=3600.0, help="切り出す合計秒の上限")
    ap.add_argument("--probe", type=int, default=20, help="話者判定に使う区間数（長い順）")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="文字起こしの時刻に足す秒（録音と文字起こしの時刻がずれている場合。先に数本切り出して聞いて決める）")
    ap.add_argument("--stats-only", action="store_true")
    ap.add_argument("--wav16", help="変換済みの 16 kHz モノラル WAV（find_self.py の cache/<id>.16k.wav）。あれば変換を省く")
    args = ap.parse_args()

    audio = Path(args.audio)
    segs = load_segments(Path(args.segments))
    if args.offset:
        for s in segs:
            s["start"] += args.offset
            s["end"] += args.offset
    by_spk: dict[str, list[dict]] = {}
    for s in segs:
        by_spk.setdefault(s["speaker"], []).append(s)

    print("話者        区間数   合計(分)   2秒以上(分)")
    totals = {}
    for spk, ss in sorted(by_spk.items(), key=lambda kv: -sum(x["end"] - x["start"] for x in kv[1])):
        tot = sum(x["end"] - x["start"] for x in ss)
        long = sum(x["end"] - x["start"] for x in ss if x["end"] - x["start"] >= args.min_dur)
        totals[spk] = tot
        print(f"{spk:12s} {len(ss):6d} {tot / 60:9.1f} {long / 60:11.1f}")
    if args.stats_only:
        return

    chosen = args.participant
    scores: dict[str, float] = {}
    emb = None
    wav16 = None
    td = None
    if args.enroll:
        emb = Embedder()
        ref = emb.embed_file(Path(args.enroll))
        # 16 kHz WAV はディスクに置き、区間ごとに読む（録音全体をメモリに載せない）
        if args.wav16 and Path(args.wav16).exists():
            wav16 = Path(args.wav16)
        else:
            td = tempfile.TemporaryDirectory()
            wav16 = Path(td.name) / "a16.wav"
            to_wav16k(audio, wav16)
        for spk, ss in by_spk.items():
            cand = sorted(ss, key=lambda x: -(x["end"] - x["start"]))[: args.probe]
            sims = []
            for s in cand:
                e = emb.embed_span_file(wav16, s["start"], min(s["end"], s["start"] + args.max_dur))
                if e is not None:
                    sims.append(float((e * ref).sum()))
            if sims:
                sims.sort()
                scores[spk] = sims[len(sims) // 2]  # 中央値（重なり区間の影響を抑える）
        print("\n本人（enroll）との類似度（中央値, 1 に近いほど同一人物）:")
        for spk, sc in sorted(scores.items(), key=lambda kv: -kv[1]):
            print(f"  {spk:12s} {sc:6.3f}")
        if not chosen:
            ranked = sorted(scores.items(), key=lambda kv: -kv[1])
            chosen = ranked[0][0]
            if len(ranked) > 1 and ranked[0][1] - ranked[1][1] < 0.1:
                print("警告: 1 位と 2 位の差が小さい。切り出し後に必ず聞いて確認すること")
    if not chosen:
        chosen = max(totals, key=totals.get)
        print(f"\n--enroll も --participant も無いので最多発話者 {chosen} を本人とみなす（要確認）")
    print(f"\n選択: {chosen}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    total = 0.0
    k = 0
    ref = emb.embed_file(Path(args.enroll)) if emb else None
    for s in sorted(by_spk.get(chosen, []), key=lambda x: x["start"]):
        dur = s["end"] - s["start"]
        if dur < args.min_dur:
            continue
        end = min(s["end"], s["start"] + args.max_dur)
        k += 1
        dst = out / f"seg_{k:04d}.wav"
        cut(audio, dst, s["start"], end)
        sim = ""
        if emb is not None and wav16 is not None:
            e = emb.embed_span_file(wav16, s["start"], end)
            if e is not None:
                sim = f"{float((e * ref).sum()):.3f}"
        rows.append({"file": dst.name, "start": f"{s['start']:.2f}", "end": f"{end:.2f}",
                     "dur": f"{end - s['start']:.2f}", "sim": sim, "text": s["text"].replace("\n", " ")})
        total += end - s["start"]
        if total >= args.max_total:
            break
    with (out / "index.csv").open("w", encoding="utf-8", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=["file", "start", "end", "dur", "sim", "text"])
        wtr.writeheader()
        wtr.writerows(rows)
    (out / "meta.json").write_text(json.dumps({"audio": str(audio), "segments": str(args.segments),
                                               "participant": chosen, "scores": scores,
                                               "n": len(rows), "total_sec": round(total, 1)},
                                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(rows)} segments, {total / 60:.1f} 分 → {out}/ (index.csv, meta.json)")
    if td is not None:
        td.cleanup()


if __name__ == "__main__":
    main()
