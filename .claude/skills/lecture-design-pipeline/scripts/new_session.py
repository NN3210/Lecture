#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""講義 1 回分の作業ディレクトリ（notes/session<NN>_<tag>_<date>/）と 00_設定.md を作る。

使い方（Surveying/ で実行）:
    python -I .claude/skills/lecture-design-pipeline/scripts/new_session.py --root notes/session05_traverse_20261101 \
        --subject 測量学 --session 第5回 --topic "トラバース測量 I" --header "測量学 第5回" \
        --subtopics "トラバースの種類と用途→選点→測角誤差の許容と等配分→方向角の計算→緯距・経距→座標の逆計算" \
        [--adjacent "閉合差・閉合比・コンパス法則・座標計算・放射法（第 6 回）"] \
        [--search-terms "traverse surveying lecture / 多角測量 講義 / Polygonzug Vorlesung"] \
        [--codes .claude/skills/lecture-order-guideline/references/stage_codes_トラバース測量.md] \
        [--deck "なし（新規設計）"] [--plan materials/lecture_plan_13.md]

作ること:
    <root>/00_設定.md（references/session_config_template.md の {{…}} を埋めたもの）
    <root>/collect/ codex/{batches,prompts,logs,results,tmp,cache,merged} 確認画像/ 手順書/
既にあるファイルは上書きしない。
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "references" / "session_config_template.md"
SUBDIRS = ["collect", "codex/batches", "codex/prompts", "codex/logs", "codex/results",
           "codex/tmp", "codex/cache", "codex/merged", "確認画像", "手順書"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="作業ディレクトリ（例: notes/session05_traverse_20261101）")
    ap.add_argument("--subject", required=True, help="科目（例: 測量学）")
    ap.add_argument("--session", required=True, help="回（例: 第5回）")
    ap.add_argument("--topic", required=True, help="テーマ（例: トラバース測量 I）")
    ap.add_argument("--header", required=True, help="スライドのヘッダー接頭辞（例: 測量学 第5回）")
    ap.add_argument("--subtopics", required=True, help="副話題（「→」でつなぐ）")
    ap.add_argument("--adjacent", default="（なし）")
    ap.add_argument("--search-terms", default="（収集時に決める）")
    ap.add_argument("--codes", default="（lecture-order-guideline で決める）")
    ap.add_argument("--deck", default="なし（新規設計）")
    ap.add_argument("--plan", default="materials/lecture_plan_13.md")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()

    root = Path(a.root)
    for d in SUBDIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    cfg = root / "00_設定.md"
    if cfg.exists():
        print(f"既にある（上書きしない）: {cfg}")
    else:
        text = TEMPLATE.read_text(encoding="utf-8")
        for k, v in {
            "ROOT": a.root.replace("\\", "/"), "DATE": a.date, "SUBJECT": a.subject, "SESSION": a.session,
            "TOPIC": a.topic, "SUBTOPICS": a.subtopics, "ADJACENT": a.adjacent, "SEARCH_TERMS": a.search_terms,
            "HEADER": a.header, "CODES": a.codes, "DECK": a.deck, "PLAN": a.plan,
        }.items():
            text = text.replace("{{" + k + "}}", v)
        cfg.write_text(text, encoding="utf-8")
        print(f"作成: {cfg}")
    print(f"ディレクトリ: {root}/ に {len(SUBDIRS)} 個のサブディレクトリ")
    print("次: lecture-source-search の init_collect_dir.py で collect/_収集指示.md を作る")


if __name__ == "__main__":
    main()
