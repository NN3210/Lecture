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
  3. 選んだ話者の区間を Silero VAD（vad_util.py）で発話だけの区間（min-dur〜max-dur 秒）に割り、元の mp3 から
     切り出す（前後 0.1 秒の余白）。区間ごとの enroll との類似度を index.csv に書き、--min-sim 未満は捨てる
     （Circleback の区間は粗く、無音や他人の声を含むことがあるため）

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vad_util import pieces_in, speech_regions  # noqa: E402

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
    ap.add_argument("--max-dur", type=float, default=20.0, help="これより長い発話区間は max-dur 秒ずつに割る")
    ap.add_argument("--min-sim", type=float, default=0.0, help="--enroll があるとき、本人との類似度がこれ未満の発話区間は切り出さない（0.5 が目安）")
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
    # 16 kHz WAV はディスクに置き、区間ごとに読む（録音全体をメモリに載せない）
    if args.wav16 and Path(args.wav16).exists():
        wav16 = Path(args.wav16)
        vad_json = Path(str(wav16)[: -len(".16k.wav")] + ".vad.json") if str(wav16).endswith(".16k.wav") else None
    else:
        td = tempfile.TemporaryDirectory()
        wav16 = Path(td.name) / "a16.wav"
        to_wav16k(audio, wav16)
        vad_json = None
    # Circleback の話者区間は粗く大半が無音のことがあるので、VAD で発話区間（piece）に割ってから使う
    print("発話区間検出（VAD）...", flush=True)
    regions = speech_regions(wav16, vad_json)

    def pieces_of(ss: list[dict]) -> list[tuple[float, float, dict]]:
        out_p = []
        for s in ss:
            for a, b in pieces_in(s["start"], s["end"], regions, args.min_dur, args.max_dur):
                out_p.append((a, b, s))
        return out_p

    if args.enroll:
        emb = Embedder()
        ref = emb.embed_file(Path(args.enroll))
        for spk, ss in by_spk.items():
            cand = sorted(pieces_of(ss), key=lambda x: -(x[1] - x[0]))[: args.probe]
            sims = []
            for a, b, _s in cand:
                e = emb.embed_span_file(wav16, a, b)
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
    skipped = 0
    for a, b, s in sorted(pieces_of(by_spk.get(chosen, [])), key=lambda x: x[0]):
        sim = ""
        if emb is not None:
            e = emb.embed_span_file(wav16, a, b)
            if e is None:
                continue
            sv = float((e * ref).sum())
            if sv < args.min_sim:
                skipped += 1
                continue
            sim = f"{sv:.3f}"
        k += 1
        dst = out / f"seg_{k:04d}.wav"
        cut(audio, dst, a, b)
        rows.append({"file": dst.name, "start": f"{a:.2f}", "end": f"{b:.2f}",
                     "dur": f"{b - a:.2f}", "sim": sim, "text": s["text"].replace("\n", " ")[:200]})
        total += b - a
        if total >= args.max_total:
            break
    if skipped:
        print(f"enroll との類似度が {args.min_sim} 未満で捨てた発話区間: {skipped}")
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
