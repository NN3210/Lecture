#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""codex/merged/<batch>.md（Sonnet が圧縮したバッチ別ファイル）を No. 順に連結し、
notes/session03_kai2_20261021/02_各資料の構成抽出.md を作る。

使い方:
    python -I scripts/kai2_concat_merged.py            （Surveying/ で実行）

やること:
- 各 merged ファイルの「## 一覧」表の行（| 004 | ... |）を集め、No. 順に 1 つの表にする。
- 「### 資料NNN：」で始まる節を集め、No. 順に並べる（同じ No. が複数あれば後のファイルを採用＝再実行の結果を優先）。
- 先頭に件数・OK/NG・段階コードの凡例を置く。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021")
MERGED = ROOT / "codex" / "merged"
OUT = ROOT / "02_各資料の構成抽出.md"
ROW = re.compile(r"^\|\s*(\d{3})\s*\|")
SEC = re.compile(r"^### 資料(\d{3})")

LEGEND = """段階コード：WHY なぜ座標が要るか／COORD 座標とは／SHAPE 地球の形／GEOID ジオイド・平均海面／HEIGHT 高さの種類／LATLON 緯度経度／ECEF 地心直交／DATUM 測地系／TRANSFORM 座標・測地系変換／PROJ 投影の概念・ひずみ／MAPPROJ 投影法の種類／TMUTM 横メルカトル・UTM／PLANE 州平面・平面直角座標系／SCALE 縮尺係数・距離換算／AXIS 軸の向き・北・方位角／CALC 座標計算／GNSS 測位と機器設定／LAW 法令・元期／EX 演習・まとめ／OTHER その他。
導入型：問い／例／歴史／定義／目次／不明。"""


def main() -> None:
    files = sorted(MERGED.glob("*.md"))
    if not files:
        sys.exit("merged ファイルがありません")
    rows: dict[str, str] = {}
    secs: dict[str, list[str]] = {}
    header_line = ""
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        cur: str | None = None
        in_table = False
        for ln in lines:
            if ln.startswith("| No |") and not header_line:
                header_line = ln
            if ROW.match(ln) and cur is None:
                rows[ROW.match(ln).group(1)] = ln
                in_table = True
                continue
            m = SEC.match(ln)
            if m:
                cur = m.group(1)
                secs[cur] = [ln]
                continue
            if cur is not None:
                if ln.startswith("## ") or ln.startswith("# "):
                    cur = None
                    continue
                secs[cur].append(ln)
    ok = sum(1 for r in rows.values() if "| OK |" in r or "| OK（" in r)
    ng = sum(1 for r in rows.values() if "| NG" in r)
    out = [
        "# 02 各資料の構成抽出（Codex の結果を Sonnet が圧縮し、No. 順に連結）",
        "",
        f"作成：2026-10-22。元ファイル：`codex/results/資料NNN.md`（Codex GPT-6 Astra、推論 High）。圧縮：`codex/merged/*.md`（Sonnet、指示書 `codex/merge_instructions.md`）。",
        f"件数：{len(rows)}（実在確認 OK {ok}、NG {ng}）。NG の資料は一覧の行のみ。",
        "",
        LEGEND,
        "",
        "## 一覧（No. 順）",
        "",
        header_line or "| No | 題 | 種別・言語・長さ | 機関 | レベル | 実在 | 段階数 | 導入型 | 段階コード列 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    out += [rows[k] for k in sorted(rows)]
    out += ["", "## 各資料", ""]
    for k in sorted(secs):
        body = [ln for ln in secs[k]]
        while body and not body[-1].strip():
            body.pop()
        out += body + [""]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT}: 一覧 {len(rows)} 行、節 {len(secs)}、OK {ok}、NG {ng}、元 {len(files)} ファイル")


if __name__ == "__main__":
    main()
