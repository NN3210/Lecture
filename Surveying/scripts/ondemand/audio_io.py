#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""torchaudio.load を soundfile 実装に差し替える（Windows で torchcodec が FFmpeg の DLL を見つけられない対策）。

PyTorch 2.9 以降の torchaudio.load は torchcodec 経由で音声を読み、torchcodec は FFmpeg の共有ライブラリ
（avcodec-xx.dll など）を要求する。winget の Gyan.FFmpeg（static ビルド）には DLL が無いので失敗する。
XTTS が torchaudio.load を使うのは参照音声の読み込みだけ、speechbrain も本スクリプト側で音声を渡すだけなので、
soundfile（libsndfile 同梱、WAV/FLAC/OGG/MP3 可）で読む関数に差し替えれば torchcodec は不要になる。

使い方: TTS や speechbrain を import する前に  patch_torchaudio_load()  を呼ぶ。
環境変数 ONDEMAND_KEEP_TORCHCODEC=1 を付けると差し替えない（共有版 FFmpeg を入れた環境で元に戻したいとき）。
"""
from __future__ import annotations

import os


def sf_load(path, frame_offset: int = 0, num_frames: int = -1, normalize: bool = True,
            channels_first: bool = True, format=None, buffer_size: int = 4096, backend=None):
    """torchaudio.load と同じ戻り値 (Tensor[channels, frames] float32, sample_rate) を soundfile で作る。"""
    import numpy as np
    import soundfile as sf
    import torch

    stop = None if num_frames is None or num_frames < 0 else frame_offset + num_frames
    data, sr = sf.read(str(path), start=frame_offset, stop=stop, dtype="float32", always_2d=True)
    arr = np.ascontiguousarray(data.T if channels_first else data)
    return torch.from_numpy(arr), int(sr)


def patch_torchaudio_load() -> bool:
    """torchaudio.load を差し替える。差し替えたら True。"""
    if os.environ.get("ONDEMAND_KEEP_TORCHCODEC") == "1":
        return False
    import torchaudio

    if getattr(torchaudio.load, "__name__", "") == "sf_load":
        return True
    torchaudio.load = sf_load  # type: ignore[assignment]
    try:  # 新しい torchaudio は torchaudio._torchcodec.load_with_torchcodec を直接呼ぶ所がある
        import torchaudio._torchcodec as tc  # type: ignore

        tc.load_with_torchcodec = sf_load  # type: ignore[attr-defined]
    except Exception:
        pass
    return True
