#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""収集の共通指示（collect/_収集指示.md）と、サブエージェント 4 体の起動プロンプト（collect/_起動プロンプト.md）を
00_設定.md と雛形から作る。

使い方（科目のプロジェクト直下、例 Surveying/ で実行）:
    python -I .claude/skills/lecture-source-search/scripts/init_collect_dir.py --root notes/session05_traverse_20261101
    オプション（00_設定.md の値を上書き）:
      --subject 測量学 --topic "トラバース測量" --subtopics "…→…" --adjacent "…" --search-terms "…"
      --institutions "国土地理院、NOAA/NGS、Ordnance Survey、Geoscience Australia など"
      --force   既にあるファイルを上書きする
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "references"
KEY_RE = re.compile(r"[（(]\s*([A-Z_]{3,})\b")

SPLIT = [
    ("A", "英語スライド", "英語の大学・MOOC・公的機関の講義スライド・講義ノート・教科書章（pdf / pptx / html）。動画は含めない", 28),
    ("B", "英語動画", "英語の YouTube 講義動画・解説動画（大学の公式チャンネル、MOOC、教育チャンネル）。再生リストは代表 1 本をリストにし、備考に本数を書く", 28),
    ("C", "日本語", "日本語の資料。大学・高専の講義ページ・スライド・ノート、公的機関の解説ページ、YouTube の講義・解説動画。資格試験対策の動画は講義の形になっているものだけ", 28),
    ("D", "他言語", "英語・日本語以外の言語の資料（スライド・ノート・動画）。1 言語 6 件以内で、ドイツ語・スペイン語・フランス語・ポルトガル語・インドネシア語・ロシア語・ウクライナ語・トルコ語・中国語・韓国語などから幅広く", 24),
]


def read_config(root: Path) -> dict[str, str]:
    """00_設定.md の表から、1 列目の括弧内の大文字キー（SUBJECT など）→ 2 列目の値を読む。"""
    cfg = root / "00_設定.md"
    out: dict[str, str] = {}
    if not cfg.exists():
        return out
    for ln in cfg.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        m = KEY_RE.search(cells[0])
        if m:
            out[m.group(1)] = cells[1]
    return out


def fill(text: str, values: dict[str, str]) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--topic")
    ap.add_argument("--subtopics")
    ap.add_argument("--adjacent")
    ap.add_argument("--search-terms")
    ap.add_argument("--institutions", default="測量なら国土地理院、NOAA/NGS、Ordnance Survey、Geoscience Australia など。科目に合わせて読み替える")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    root = Path(a.root)
    cfg = read_config(root)
    v = {
        "ROOT": a.root.replace("\\", "/"),
        "SUBJECT": a.subject or cfg.get("SUBJECT", "（科目）"),
        "TOPIC": a.topic or cfg.get("TOPIC", "（テーマ）"),
        "SUBTOPICS": a.subtopics or cfg.get("SUBTOPICS", "（副話題）"),
        "ADJACENT": a.adjacent or cfg.get("ADJACENT", "（なし）"),
        "SEARCH_TERMS": a.search_terms or cfg.get("SEARCH_TERMS", "（テーマの英語名 lecture slides / 日本語名 講義 など）"),
        "INSTITUTIONS": a.institutions,
    }
    v["SUBTOPICS_EXAMPLE"] = v["SUBTOPICS"]
    missing = [k for k in ("SUBJECT", "TOPIC", "SUBTOPICS") if v[k].startswith("（")]
    if missing:
        print(f"警告: {missing} が 00_設定.md にもオプションにも無い。雛形のまま書くので、後で直すこと。")

    (root / "collect").mkdir(parents=True, exist_ok=True)
    out1 = root / "collect" / "_収集指示.md"
    if out1.exists() and not a.force:
        print(f"既にある（--force で上書き）: {out1}")
    else:
        out1.write_text(fill((REF / "collect_instructions_template.md").read_text(encoding="utf-8"), v), encoding="utf-8")
        print(f"作成: {out1}")

    tmpl = (REF / "subagent_prompt.md").read_text(encoding="utf-8")
    m = re.search(r"## 起動プロンプト（1 体分）\s*```\n(.*?)```", tmpl, re.S)
    if not m:
        sys.exit("references/subagent_prompt.md に起動プロンプトのコードブロックが無い")
    one = m.group(1)
    blocks = ["# サブエージェント起動プロンプト（4 体を 1 つのメッセージで同時に起動する。model: sonnet）", ""]
    for letter, name, scope, n in SPLIT:
        blocks.append(f"## {letter}（{name}、目標 {n} 件）→ collect/資料収集_{letter}_{name}.md")
        blocks.append("")
        blocks.append("```")
        blocks.append(fill(one, {**v, "LETTER": letter, "NAME": name, "SCOPE": scope, "N": str(n)}).rstrip())
        blocks.append("```")
        blocks.append("")
    out2 = root / "collect" / "_起動プロンプト.md"
    if out2.exists() and not a.force:
        print(f"既にある（--force で上書き）: {out2}")
    else:
        out2.write_text("\n".join(blocks), encoding="utf-8")
        print(f"作成: {out2}")
    print("次: _収集指示.md の科目固有の例を直してから、_起動プロンプト.md の 4 本を同時に Agent で起動する")


if __name__ == "__main__":
    main()
