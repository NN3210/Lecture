#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""発話区間検出（VAD）の補助。faster-whisper に同梱の Silero VAD を使う（追加インストール不要、CPU で実時間の 50 倍以上）。

なぜ必要か: Circleback の話者区間は粗く（1 区間が数分に及び、その大半が無音のことがある）、区間の先頭 15 秒を
そのまま話者埋め込みにかけると無音・雑音を埋め込んでしまう。2026-10-22 の試行では、録音機の暗騒音どうしが
「会議をまたいで共通の声」として選ばれた。そこで、16 kHz WAV 全体に VAD をかけて発話区間だけを取り、
Circleback の話者区間と重なる発話区間（piece）を埋め込み・切り出しの単位にする。

使い方:
  from vad_util import speech_regions, pieces_in
  regions = speech_regions(Path("cache/<id>.16k.wav"), Path("cache/<id>.vad.json"))   # [(start, end), ...] 秒
  pieces = pieces_in(seg["start"], seg["end"], regions, min_dur=2.0, max_dur=15.0)     # 区間内の発話 [(a, b), ...]
"""
from __future__ import annotations

import json
from pathlib import Path


def speech_regions(wav16k: Path, cache_json: Path | None = None, chunk_sec: float = 600.0,
                   threshold: float = 0.5, min_speech_ms: int = 800, min_silence_ms: int = 500,
                   pad_ms: int = 150) -> list[tuple[float, float]]:
    """16 kHz モノラル WAV 全体の発話区間 [(start, end), ...]（秒）。chunk_sec ごとに読むので長い録音でもメモリを使わない。
    cache_json があれば結果を保存し、次回はそれを読む。"""
    if cache_json and cache_json.exists():
        d = json.loads(cache_json.read_text(encoding="utf-8"))
        return [tuple(x) for x in d["regions"]]
    import soundfile as sf
    from faster_whisper.vad import VadOptions, get_speech_timestamps

    opts = VadOptions(threshold=threshold, min_speech_duration_ms=min_speech_ms,
                      min_silence_duration_ms=min_silence_ms, speech_pad_ms=pad_ms)
    info = sf.info(str(wav16k))
    sr = info.samplerate
    assert sr == 16000, f"16 kHz の WAV が必要: {wav16k} は {sr} Hz"
    n = info.frames
    step = int(chunk_sec * sr)
    regions: list[list[float]] = []
    for a in range(0, n, step):
        data, _ = sf.read(str(wav16k), start=a, stop=min(n, a + step), dtype="float32", always_2d=True)
        x = data.mean(axis=1)
        for ts in get_speech_timestamps(x, opts, sampling_rate=sr):
            s, e = (a + ts["start"]) / sr, (a + ts["end"]) / sr
            if regions and s - regions[-1][1] < min_silence_ms / 1000.0:
                regions[-1][1] = e  # チャンク境界で割れた発話をつなぐ
            else:
                regions.append([s, e])
    out = [(round(s, 3), round(e, 3)) for s, e in regions]
    if cache_json:
        cache_json.parent.mkdir(parents=True, exist_ok=True)
        cache_json.write_text(json.dumps({"wav": str(wav16k), "threshold": threshold, "min_speech_ms": min_speech_ms,
                                          "min_silence_ms": min_silence_ms, "regions": out}), encoding="utf-8")
    return out


def pieces_in(start: float, end: float, regions: list[tuple[float, float]], min_dur: float = 2.0,
              max_dur: float = 15.0) -> list[tuple[float, float]]:
    """[start, end] と重なる発話区間を切り取り、max_dur より長いものは max_dur ずつに割り、min_dur 未満は捨てる。"""
    import bisect

    out = []
    i = bisect.bisect_left(regions, (start - max_dur * 4, 0.0))
    for s, e in regions[i:]:
        if s >= end:
            break
        a, b = max(s, start), min(e, end)
        if b - a < min_dur:
            continue
        while b - a > max_dur:
            out.append((a, a + max_dur))
            a += max_dur
        if b - a >= min_dur:
            out.append((a, b))
    return out


def speech_total(regions: list[tuple[float, float]], start: float, end: float) -> float:
    """[start, end] に含まれる発話の合計秒。"""
    return sum(max(0.0, min(e, end) - max(s, start)) for s, e in regions if e > start and s < end)
