#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""合成した音声を音声認識（faster-whisper）で文字に戻し、台本と突き合わせて誤読・欠落を見つける。

人が聞かなくても（AI エージェントでも）ナレーションの点検ができるようにするための道具。
build_video.py の作業フォルダー（work_<名前>/audio/slideNN.wav）と narration.md を渡すと、スライドごとに
文字誤り率（CER）と差分を表にする。CER が高いスライドだけ聞き直せばよい。

使い方（仮想環境の python で）:
  python scripts/ondemand/check_asr.py --narration narration.md --work ondemand/work/work_lecture05_edge [--model small] [--only 3,5]
  python scripts/ondemand/check_asr.py --wav out.wav --text "読ませた文"          # 1 本だけ

比較は漢字を読み（ローマ字）に直してから行うので、音声認識が同音の別の漢字を当てても（測角→即格）誤りに数えない。
認識側の算用数字（360）・ラテン文字（TS）・記号（°）は、台本と同じ漢数字・片仮名（三百六十、ティーエス、度）に直してから比べる。
目安: CER 15% 未満なら正常。他のスライドより目立って高い枚、長い delete（途切れ）がある枚を聞き直す。
初回は Whisper のモデル（small で約 470 MB）をダウンロードする。
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

STRIP_RE = re.compile(r"[\s、。，．,.!?！？「」『』（）()\[\]【】・:：;；\-—–~〜…]+")

# 音声認識は「三百六十度」を「360度」、「ティーエス」を「TS」と書くことが多い。台本（3 章の規則で漢数字・片仮名）と
# 同じ表記にそろえてから比べないと、表記の違いが誤読として数えられる（2026-10-22 の edge-tts 検査で CER 20〜48%）。
_KANJI_DIGITS = "零一二三四五六七八九"
_LETTER_READING = {"a": "エー", "b": "ビー", "c": "シー", "d": "ディー", "e": "イー", "f": "エフ", "g": "ジー",
                   "h": "エイチ", "i": "アイ", "j": "ジェー", "k": "ケー", "l": "エル", "m": "エム", "n": "エヌ",
                   "o": "オー", "p": "ピー", "q": "キュー", "r": "アール", "s": "エス", "t": "ティー", "u": "ユー",
                   "v": "ブイ", "w": "ダブリュー", "x": "エックス", "y": "ワイ", "z": "ゼット"}
_SYMBOL_READING = {"°": "度", "′": "分", "″": "秒", "'": "分", '"': "秒", "√": "ルート", "Δ": "デルタ", "δ": "デルタ",
                   "ε": "イプシロン", "β": "ベータ", "σ": "シグマ", "Σ": "シグマ", "%": "パーセント", "％": "パーセント",
                   "±": "プラスマイナス", "×": "かける", "÷": "割る", "=": "イコール", "＝": "イコール"}
_NUMBER_RE = re.compile(r"([-−＋+])?(\d+)(?:[.．](\d+))?")


def _int_to_kanji(n: int) -> str:
    """360 → 三百六十、1500 → 千五百、206265 → 二十万六千二百六十五（台本の書き方に合わせる）。"""
    if n == 0:
        return "ゼロ"

    def under_10000(m: int) -> str:
        out = ""
        for unit, name in ((1000, "千"), (100, "百"), (10, "十")):
            d, m = divmod(m, unit)
            if d:
                out += ("" if d == 1 else _KANJI_DIGITS[d]) + name
        if m:
            out += _KANJI_DIGITS[m]
        return out

    parts = []
    for name in ("", "万", "億"):
        n, r = divmod(n, 10000)
        if r:
            s = under_10000(r)
            if name and r < 10:
                s = _KANJI_DIGITS[r]  # 一万、二万
            parts.append(s + name)
        if n == 0:
            break
    return "".join(reversed(parts))


def _number_to_spoken(m: re.Match) -> str:
    sign, ip, fp = m.group(1), m.group(2), m.group(3)
    out = ""
    if sign in ("-", "−"):
        out += "マイナス"
    elif sign in ("+", "＋"):
        out += "プラス"
    if fp is not None:
        out += ("零" if int(ip) == 0 else _int_to_kanji(int(ip))) + "点" + "".join(_KANJI_DIGITS[int(c)] for c in fp)
    else:
        out += _int_to_kanji(int(ip))
    return out


def spoken_form(s: str) -> str:
    """算用数字・ラテン文字・記号を、台本と同じ漢数字・片仮名の読みに直す（比較用。音声合成には使わない）。"""
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)  # 1,500 → 1500
    s = _NUMBER_RE.sub(_number_to_spoken, s)
    s = "".join(_SYMBOL_READING.get(c, c) for c in s)
    s = s.translate(str.maketrans({chr(0xFF21 + i): chr(0x41 + i) for i in range(26)}))  # 全角 A → A
    s = s.translate(str.maketrans({chr(0xFF41 + i): chr(0x61 + i) for i in range(26)}))
    return re.sub(r"[A-Za-z]", lambda mm: _LETTER_READING[mm.group(0).lower()], s)


def normalize(s: str) -> str:
    s = STRIP_RE.sub("", spoken_form(s))
    return s.lower()


_ROMAJI = None


def normalize_romaji(s: str) -> str:
    """漢字を読み（ローマ字）に直してから比べる。音声認識が同音の別の漢字を当てても（測角→即格）誤りに数えない。
    cutlet（coqui-tts[ja] と一緒に入る）が無ければ文字のままの比較に戻る。"""
    global _ROMAJI
    if _ROMAJI is None:
        try:
            import cutlet

            katsu = cutlet.Cutlet()
            katsu.use_foreign_spelling = False
            _ROMAJI = katsu
        except Exception:
            _ROMAJI = False
    if not _ROMAJI:
        return normalize(s)
    r = _ROMAJI.romaji(STRIP_RE.sub("", spoken_form(s)))
    return re.sub(r"[\s\-'’]+", "", r).lower()


NORM = normalize_romaji


def cer(ref: str, hyp: str) -> float:
    ref_n, hyp_n = NORM(ref), NORM(hyp)
    if not ref_n:
        return 0.0
    sm = difflib.SequenceMatcher(None, ref_n, hyp_n, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    errors = max(len(ref_n), len(hyp_n)) - matched
    return errors / len(ref_n)


def diff_snippets(ref: str, hyp: str, max_items: int = 5) -> list[str]:
    ref_n, hyp_n = NORM(ref), NORM(hyp)
    sm = difflib.SequenceMatcher(None, ref_n, hyp_n, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append(f"{tag}: 台本「{ref_n[i1:i2]}」→ 認識「{hyp_n[j1:j2]}」")
        if len(out) >= max_items:
            break
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--narration")
    ap.add_argument("--work", help="build_video.py の作業フォルダー（audio/slideNN.wav がある）")
    ap.add_argument("--wav")
    ap.add_argument("--text")
    ap.add_argument("--model", default="small", help="faster-whisper のモデル（tiny/base/small/medium）")
    ap.add_argument("--only")
    ap.add_argument("--threshold", type=float, default=0.15, help="この CER 以上を要確認として表示")
    ap.add_argument("--no-romaji", action="store_true", help="読み（ローマ字）に直さず文字のまま比べる")
    args = ap.parse_args()
    try:  # Windows でリダイレクトしたときに cp932 で落ちないように
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    global NORM
    if args.no_romaji:
        NORM = normalize
    else:
        normalize_romaji("試")  # cutlet が無いときは文字比較に戻る
        if not _ROMAJI:
            print("(cutlet が無いので文字のまま比較。同音の漢字違いも誤りに数える)", file=sys.stderr)

    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    def asr(path: Path) -> str:
        segs, _info = model.transcribe(str(path), language="ja", beam_size=3)
        return "".join(s.text for s in segs)

    if args.wav:
        hyp = asr(Path(args.wav))
        print("認識:", hyp)
        if args.text:
            print(f"CER: {cer(args.text, hyp) * 100:.1f}%")
            for d in diff_snippets(args.text, hyp):
                print("  ", d)
        return

    if not (args.narration and args.work):
        raise SystemExit("--narration と --work、または --wav を指定")
    from build_video import parse_narration

    narration = parse_narration(Path(args.narration))
    only = {int(v) for v in args.only.split(",")} if args.only else None
    audio_dir = Path(args.work) / "audio"
    rows = []
    for n in sorted(narration):
        if only and n not in only:
            continue
        wav = audio_dir / f"slide{n:02d}.wav"
        text = narration[n].strip()
        if not wav.exists() or not text or "TODO" in text:
            continue
        # 認識結果は asr/slideNN.<model>.txt に残し、wav が変わっていなければ使い回す（認識は 1 枚 10〜20 秒かかる）
        cache = Path(args.work) / "asr" / f"slide{n:02d}.{args.model}.txt"
        if cache.exists() and cache.stat().st_mtime >= wav.stat().st_mtime:
            hyp = cache.read_text(encoding="utf-8")
        else:
            hyp = asr(wav)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(hyp, encoding="utf-8")
        c = cer(text, hyp)
        rows.append((n, c, text, hyp))
        flag = "要確認" if c >= args.threshold else ""
        print(f"slide {n:3d}  CER {c * 100:5.1f}%  {flag}", flush=True)
        if c >= args.threshold:
            for d in diff_snippets(text, hyp):
                print("     ", d)
    if rows:
        avg = sum(r[1] for r in rows) / len(rows)
        worst = max(rows, key=lambda r: r[1])
        print(f"\n{len(rows)} slides  平均 CER {avg * 100:.1f}%  最大 slide {worst[0]} ({worst[1] * 100:.1f}%)")


if __name__ == "__main__":
    main()
