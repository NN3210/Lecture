#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""enroll 録音なしで、複数の会議録音から「本人（録音機の装着者）」の声を見つける。

考え方
  Circleback の話者ラベル（Participant N）は会議ごとに振り直されるので、会議をまたいで同じ人を追えない。
  しかし装着者は全部の録音に出ている。そこで会議ごと・話者ごとに声の埋め込み（speechbrain ECAPA）の
  代表ベクトルを作り、会議をまたいでクラスタリングし、最も多くの会議に現れたクラスターを本人とみなす。
  補助の手掛かり: 装着者はマイクに近いので発話量が多い。三人称で本人の名前を呼ぶ話者は本人でない（--not-self-regex）。

材料
  --audio-dir     plaud_download.py で落とした録音（ファイル名の先頭が日付、どこかに PLAUD の id 32 桁）
  --transcripts   circleback_transcript.py fetch <linkId> --json の JSON を置いたフォルダー
                  録音との突き合わせは、meeting.name に PLAUD の id があればそれで、無ければ
                  録音の長さと meeting.duration の一致（±1%）で行う（組になった対を最初に表示する）

出力（--out）
  self_map.json   録音ごとの本人ラベルと確からしさ
  report.md       クラスターの表（人が見る用）
  auto_enroll.wav 本人クラスターの中で代表ベクトルに最も近い区間を会議をまたいで集めた約 --enroll-sec 秒の WAV。
                  これを extract_speaker.py --enroll に渡せば、以後は録音 1 本ずつ自動判定できる
  cache/          録音ごとの 16 kHz WAV と話者ごとの埋め込み（<id>.units.json）。途中で止まっても再実行すれば
                  済んだ録音は飛ばす。全部やり直すときはこのフォルダーを消す

メモリ
  録音全体はメモリに載せず、区間ごとにディスクから読む。使うのは話者モデル（約 1 GB）だけ。
  それでも空きメモリが 3 GB を切る状態で動かすと PC 全体が止まるので、ブラウザー等を閉じてから 1 本ずつ動かす。

使い方（仮想環境の python で）:
  python scripts/ondemand/find_self.py --audio-dir ondemand/voice/raw --transcripts ondemand/voice/raw/transcripts \
      --out ondemand/voice/self_search [--per-spk 30] [--threshold 0.55] [--not-self-regex "〇〇先生"]

判定の目安: 本人クラスターが全録音の 8 割以上に現れ、各録音でのラベルの代表ベクトルとの類似度が 0.5 以上なら採用。
それ以外は report.md を見て --participant で手動指定する（extract_speaker.py）。
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
from extract_speaker import Embedder, load_segments, to_wav16k  # noqa: E402

HEX32 = re.compile(r"[0-9a-f]{32}")


def plaud_id(name: str) -> str | None:
    m = HEX32.search(name)
    return m.group(0) if m else None


def media_duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def pair_files(audio_dir: Path, tr_dir: Path) -> list[tuple[str, Path, Path]]:
    """録音と文字起こしを突き合わせる。meeting.name に PLAUD の id があればそれで、無ければ長さ（±1%）で。"""
    audios = {}
    for p in audio_dir.iterdir():
        if p.suffix.lower() in (".mp3", ".ogg", ".opus", ".m4a", ".wav", ".flac"):
            pid = plaud_id(p.name) or p.stem
            audios[pid] = p
    durs = {pid: media_duration(p) for pid, p in audios.items()}
    pairs = []
    used = set()
    for j in sorted(tr_dir.glob("*.json")):
        try:
            d = json.loads(j.read_text(encoding="utf-8"))
        except Exception:
            continue
        meeting = d.get("meeting") or {}
        pid = plaud_id(meeting.get("name") or "") or plaud_id(j.name)
        if not (pid and pid in audios):
            pid = None
            mdur = float(meeting.get("duration") or 0)
            segs = d.get("segments") or []
            if not mdur and segs:
                mdur = float(segs[-1].get("end") or 0)
            if mdur:
                best = sorted(((abs(durs[k] - mdur) / mdur, k) for k in audios if k not in used), key=lambda x: x[0])
                if best and best[0][0] <= 0.01:
                    pid = best[0][1]
        if pid:
            used.add(pid)
            pairs.append((pid, audios[pid], j))
            print(f"  組: {j.name}  ↔  {audios[pid].name}", flush=True)
        else:
            print(f"  未対応: {j.name}（長さが合う録音が無い）", flush=True)
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--transcripts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-spk", type=int, default=30, help="話者ごとに埋め込む区間数（長い順）")
    ap.add_argument("--min-dur", type=float, default=2.0)
    ap.add_argument("--max-dur", type=float, default=15.0)
    ap.add_argument("--threshold", type=float, default=0.55, help="同一人物とみなすコサイン類似度（平均連結）")
    ap.add_argument("--min-share", type=float, default=0.03, help="発話量がこれ未満の話者は無視（割合）")
    ap.add_argument("--not-self-regex", default=None, help="この正規表現を発話に含む話者は本人でない（例: 本人の姓+先生）")
    ap.add_argument("--enroll-sec", type=float, default=90.0)
    ap.add_argument("--cache-dir", default=None, help="16 kHz WAV と埋め込みの保存先（既定: <out>/cache）。再実行時は済んだ録音を飛ばす")
    args = ap.parse_args()

    import numpy as np
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import pdist

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = Path(args.cache_dir) if args.cache_dir else out / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    pairs = pair_files(Path(args.audio_dir), Path(args.transcripts))
    if not pairs:
        raise SystemExit("録音と文字起こしの組が見つからない（PLAUD の id か、録音の長さと duration の一致で突き合わせている）")
    print(f"{len(pairs)} 組の録音と文字起こし", flush=True)
    emb = None  # 話者モデルは必要になってから読む（全部キャッシュ済みなら読まない）
    not_self = re.compile(args.not_self_regex) if args.not_self_regex else None

    # 会議ごと・話者ごとの代表ベクトル
    units = []  # dict(pid, audio, json, speaker, centroid, share, n, within, mentions, segs=[(start,end,sim,text)])
    for pid, audio, j in pairs:
        uj = cache / f"{pid}.units.json"
        if uj.exists():
            cached = json.loads(uj.read_text(encoding="utf-8"))
            for u in cached:
                u["centroid"] = np.asarray(u["centroid"], dtype=np.float32)
                units.append(u)
            print(f"  {pid[:8]} キャッシュから {len(cached)} 話者", flush=True)
            continue
        segs = load_segments(j)
        total = sum(s["end"] - s["start"] for s in segs) or 1.0
        by_spk: dict[str, list[dict]] = {}
        for s in segs:
            by_spk.setdefault(s["speaker"], []).append(s)
        w16 = cache / f"{pid}.16k.wav"
        if not w16.exists():
            to_wav16k(audio, w16)
        if emb is None:
            emb = Embedder()
        meeting_units = []
        for spk, ss in by_spk.items():
            share = sum(s["end"] - s["start"] for s in ss) / total
            if share < args.min_share:
                continue
            mentions = sum(1 for s in ss if not_self and not_self.search(s.get("text", "")))
            cand = sorted((s for s in ss if s["end"] - s["start"] >= args.min_dur),
                          key=lambda x: -(x["end"] - x["start"]))[: args.per_spk]
            embs, spans = [], []
            for s in cand:
                end = min(s["end"], s["start"] + args.max_dur)
                e = emb.embed_span_file(w16, s["start"], end)  # 区間だけ読む（録音全体は載せない）
                if e is not None:
                    embs.append(e.numpy())
                    spans.append((s["start"], end, s.get("text", "")))
            if len(embs) < 3:
                continue
            E = np.stack(embs)
            c = E.mean(0)
            c /= np.linalg.norm(c) + 1e-9
            sims = E @ c
            u = {"pid": pid, "audio": str(audio), "json": str(j), "speaker": spk, "centroid": c,
                 "share": share, "n": len(embs), "within": float(np.median(sims)),
                 "mentions": mentions,
                 "segs": [(a, b, float(si), t) for (a, b, t), si in zip(spans, sims)]}
            meeting_units.append(u)
            units.append(u)
            print(f"  {pid[:8]} {spk:14s} share {share:5.1%}  n {len(embs):3d}  within-sim {float(np.median(sims)):.2f}"
                  + (f"  三人称言及 {mentions}" if mentions else ""), flush=True)
        uj.write_text(json.dumps([{**u, "centroid": [float(x) for x in u["centroid"]]} for u in meeting_units],
                                 ensure_ascii=False), encoding="utf-8")
    if not units:
        raise SystemExit("埋め込める話者が無い（--min-share や --min-dur を下げる）")

    # 会議をまたいだクラスタリング（平均連結、コサイン距離）
    C = np.stack([u["centroid"] for u in units])
    if len(units) > 1:
        Z = linkage(pdist(C, metric="cosine"), method="average")
        labels = fcluster(Z, t=1.0 - args.threshold, criterion="distance")
    else:
        labels = np.array([1])
    clusters: dict[int, list[int]] = {}
    for i, lb in enumerate(labels):
        clusters.setdefault(int(lb), []).append(i)
    n_meet = len({u["pid"] for u in units})

    def score(idx: list[int]):
        meets = {units[i]["pid"] for i in idx}
        share = sum(units[i]["share"] for i in idx) / len(meets)
        mentions = sum(units[i]["mentions"] for i in idx)
        return (len(meets), -mentions, share)

    ranked = sorted(clusters.items(), key=lambda kv: score(kv[1]), reverse=True)
    lines = ["# 本人の声の探索結果", "", f"録音 {n_meet} 本、話者単位 {len(units)}、しきい値 {args.threshold}", "",
             "| クラスター | 出現した録音数 | 平均発話割合 | 三人称言及 | 内訳（録音 : 話者, 発話割合, 代表との類似度） |",
             "| --- | --- | --- | --- | --- |"]
    for lb, idx in ranked:
        meets = {units[i]["pid"] for i in idx}
        cc = np.stack([units[i]["centroid"] for i in idx]).mean(0)
        cc /= np.linalg.norm(cc) + 1e-9
        parts = []
        for i in idx:
            u = units[i]
            parts.append(f"{u['pid'][:8]} : {u['speaker']}, {u['share']:.0%}, {float(u['centroid'] @ cc):.2f}")
        lines.append(f"| {lb} | {len(meets)}/{n_meet} | {sum(units[i]['share'] for i in idx) / len(meets):.0%} | "
                     f"{sum(units[i]['mentions'] for i in idx)} | {'; '.join(parts)} |")
    best_lb, best_idx = ranked[0]
    best_meets = {units[i]["pid"] for i in best_idx}
    verdict = "採用可" if len(best_meets) >= max(2, round(0.8 * n_meet)) else "要確認（出現した録音が少ない）"
    lines += ["", f"本人とみなすクラスター: {best_lb}（{len(best_meets)}/{n_meet} 本に出現）→ {verdict}", ""]
    print("\n".join(lines))

    # 本人クラスターの代表ベクトルに近い区間を会議をまたいで集めて enroll を作る
    cc = np.stack([units[i]["centroid"] for i in best_idx]).mean(0)
    cc /= np.linalg.norm(cc) + 1e-9
    self_map = {}
    picks = []
    for i in best_idx:
        u = units[i]
        # 同じ録音に本人クラスターの話者が 2 つあるときは類似度の高い方
        sim_c = float(u["centroid"] @ cc)
        prev = self_map.get(u["pid"])
        if prev is None or sim_c > prev["sim_to_cluster"]:
            self_map[u["pid"]] = {"audio": u["audio"], "transcript": u["json"], "participant": u["speaker"],
                                  "share": round(u["share"], 3), "sim_to_cluster": round(sim_c, 3),
                                  "within_sim": round(u["within"], 3), "mentions_not_self": u["mentions"]}
        for a, b, si, t in u["segs"]:
            picks.append((si, u["audio"], a, b, u["pid"]))
    picks.sort(key=lambda x: -x[0])
    # 録音ごとに偏らないように、上位から順に各録音最大 1/3 まで
    cap = max(1, int(args.enroll_sec / max(1, len(self_map)) / 3.0)) * 3
    per_meet: dict[str, float] = {}
    chosen = []
    tot = 0.0
    for si, audio, a, b, pid in picks:
        if tot >= args.enroll_sec:
            break
        if per_meet.get(pid, 0.0) >= args.enroll_sec / max(1, len(self_map)) * 1.5:
            continue
        chosen.append((audio, a, b))
        per_meet[pid] = per_meet.get(pid, 0.0) + (b - a)
        tot += b - a
    with tempfile.TemporaryDirectory() as td:
        parts = []
        for k, (audio, a, b) in enumerate(chosen):
            p = Path(td) / f"p{k:03d}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", audio,
                            "-ac", "1", "-ar", "16000", str(p)], check=True)
            parts.append(p)
        lst = Path(td) / "list.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-af", "loudnorm=I=-19:TP=-3", "-ac", "1", "-ar", "16000", str(out / "auto_enroll.wav")], check=True)
    (out / "self_map.json").write_text(json.dumps({"cluster": best_lb, "verdict": verdict, "threshold": args.threshold,
                                                   "recordings": self_map, "enroll_sec": round(tot, 1)},
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    lines += [f"auto_enroll.wav: {len(chosen)} 区間、{tot:.0f} 秒（{len(per_meet)} 本の録音から）", ""]
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}/self_map.json, report.md, auto_enroll.wav ({tot:.0f} s)")


if __name__ == "__main__":
    main()
