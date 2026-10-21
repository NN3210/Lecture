#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""テキスト読み上げ（TTS）のバックエンド。tts_synth.py と build_video.py から使う。

バックエンド
  edge        Microsoft Edge のオンライン音声（無料、声の複製は不可。試作・仮ナレーション用）
  xtts        Coqui XTTS v2（ローカル、CPU で動く。参照音声 6〜30 秒で声を複製。非商用ライセンス）
  elevenlabs  ElevenLabs API（クラウド、有料。Instant/Professional Voice Clone の voice_id を指定）

共通: synthesize(engine, text, out_wav, **opts) が WAV（モノラル、既定 24 kHz）を書く。
ffmpeg が PATH にあること（mp3 → wav の変換に使う）。
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
DEFAULT_SR = 24000


def to_wav(src: Path | str, dst: Path | str, sr: int = DEFAULT_SR) -> None:
    """任意の音声ファイルをモノラル WAV に変換する。"""
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", str(sr), str(dst)],
        check=True,
    )


# ---------------------------------------------------------------------------
# edge-tts
# ---------------------------------------------------------------------------

def synth_edge(text: str, out_wav: Path | str, voice: str = "ja-JP-KeitaNeural",
               rate: str = "+0%", pitch: str = "+0Hz", sr: int = DEFAULT_SR, **_) -> None:
    import asyncio

    import edge_tts

    tmp_mp3 = Path(str(out_wav) + ".edge.mp3")

    async def _run() -> None:
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await com.save(str(tmp_mp3))

    asyncio.run(_run())
    to_wav(tmp_mp3, out_wav, sr)
    tmp_mp3.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Coqui XTTS v2（ローカル）
# ---------------------------------------------------------------------------

_XTTS = None
XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"


def _load_xtts():
    global _XTTS
    if _XTTS is None:
        os.environ.setdefault("COQUI_TOS_AGREED", "1")  # 初回のモデル取得時の利用規約同意
        from audio_io import patch_torchaudio_load  # torchcodec 不要にする（audio_io.py 参照）

        patch_torchaudio_load()
        from TTS.api import TTS

        _XTTS = TTS(XTTS_MODEL).to("cpu")
    return _XTTS


def synth_xtts(text: str, out_wav: Path | str, ref: str | list[str] | None = None,
               language: str = "ja", sr: int = DEFAULT_SR, **_) -> None:
    if not ref:
        raise SystemExit("xtts には --ref で参照音声（本人の声、6〜30 秒の WAV）が必要です")
    refs = [str(r) for r in (ref if isinstance(ref, (list, tuple)) else [ref])]
    for r in refs:
        if not Path(r).exists():
            raise SystemExit(f"参照音声が見つかりません: {r}")
    tts = _load_xtts()
    tmp = Path(str(out_wav) + ".xtts.wav")
    tts.tts_to_file(text=text, speaker_wav=refs, language=language, file_path=str(tmp),
                    split_sentences=True)
    to_wav(tmp, out_wav, sr)  # XTTS の出力は 24 kHz。sr を揃えるため通す
    tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# ElevenLabs（クラウド）
# ---------------------------------------------------------------------------

ELEVEN_DEFAULT_MODEL = "eleven_multilingual_v2"


def synth_elevenlabs(text: str, out_wav: Path | str, voice: str | None = None,
                     model_id: str = ELEVEN_DEFAULT_MODEL, api_key: str | None = None,
                     stability: float | None = None, similarity: float | None = None,
                     sr: int = DEFAULT_SR, **_) -> None:
    api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("環境変数 ELEVENLABS_API_KEY を設定してください")
    if not voice:
        raise SystemExit("elevenlabs には --voice で voice_id を指定してください")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
    body: dict = {"text": text, "model_id": model_id}
    if stability is not None or similarity is not None:
        body["voice_settings"] = {
            "stability": 0.5 if stability is None else stability,
            "similarity_boost": 0.75 if similarity is None else similarity,
        }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = resp.read()
    tmp = Path(str(out_wav) + ".el.mp3")
    tmp.write_bytes(data)
    to_wav(tmp, out_wav, sr)
    tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# 共通入口
# ---------------------------------------------------------------------------

ENGINES = {"edge": synth_edge, "xtts": synth_xtts, "elevenlabs": synth_elevenlabs}


def synthesize(engine: str, text: str, out_wav: Path | str, **opts) -> None:
    if engine not in ENGINES:
        raise SystemExit(f"未知のエンジン: {engine}（{', '.join(ENGINES)} のいずれか）")
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    ENGINES[engine](text, out_wav, **opts)


def wav_duration(path: Path | str) -> float:
    """ffprobe で秒数を得る。"""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)
