#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""<root>/codex/ を初期化する：.gitignore と、設定を埋めた Codex 用の雛形 2 本（通常版・省メモリ版）を置く。

使い方（科目のプロジェクト直下、例 Surveying/ で実行）:
    python -I .claude/skills/lecture-structure-extract/scripts/init_codex_dir.py --root notes/session05_traverse_20261101
    オプション:
      --workdir "Lecture/Surveying"   Codex に伝える作業ディレクトリ名（省略時は cwd の親/自分）
      --subject / --topic / --subtopics   00_設定.md の値を上書き
      --force   既にある雛形を上書き
雛形の {{SUBJECT}} {{TOPIC}} {{SUBTOPICS}} {{ROOT}} {{WORKDIR}} をここで埋め、{{BATCH_NAME}} {{BATCH_ID}} {{N}} {{No3}} {{BATCH_TABLE}} は
run_codex_batch.py が実行時に埋める。
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
GITIGNORE = "cache/\ntmp/\nlogs/*_stdout.log\ntest*_stdout.log\n"
SUBDIRS = ["batches", "prompts", "logs", "results", "tmp", "cache", "merged"]


def read_config(root: Path) -> dict[str, str]:
    cfg = root / "00_設定.md"
    out: dict[str, str] = {}
    if not cfg.exists():
        return out
    for ln in cfg.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = KEY_RE.search(cells[0]) if len(cells) >= 2 else None
        if m:
            out[m.group(1)] = cells[1]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--workdir")
    ap.add_argument("--subject")
    ap.add_argument("--topic")
    ap.add_argument("--subtopics")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    root = Path(a.root)
    cfg = read_config(root)
    cwd = Path.cwd().resolve()
    v = {
        "ROOT": a.root.replace("\\", "/").rstrip("/"),
        "WORKDIR": a.workdir or f"{cwd.parent.name}/{cwd.name}",
        "SUBJECT": a.subject or cfg.get("SUBJECT", "（科目）"),
        "TOPIC": a.topic or cfg.get("TOPIC", "（テーマ）"),
        "SUBTOPICS": a.subtopics or cfg.get("SUBTOPICS", "（副話題）"),
    }
    for k in ("SUBJECT", "TOPIC", "SUBTOPICS"):
        if v[k].startswith("（"):
            print(f"警告: {k} が 00_設定.md にもオプションにも無い。雛形の {{{{{k}}}}} が残る")

    codex = root / "codex"
    for d in SUBDIRS:
        (codex / d).mkdir(parents=True, exist_ok=True)
    gi = codex / ".gitignore"
    if not gi.exists():
        gi.write_text(GITIGNORE, encoding="utf-8")
        print(f"作成: {gi}")
    for name in ("batch_prompt_template.md", "batch_prompt_template_light.md"):
        dst = codex / name
        if dst.exists() and not a.force:
            print(f"既にある（--force で上書き）: {dst}")
            continue
        text = (REF / name).read_text(encoding="utf-8")
        for k, val in v.items():
            text = text.replace("{{" + k + "}}", val)
        dst.write_text(text, encoding="utf-8")
        print(f"作成: {dst}")
    print("次: 雛形にテーマ固有の読み方を 1〜2 行足し、batch_t01.md（2 件）で動作確認する")


if __name__ == "__main__":
    main()
