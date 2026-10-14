# -*- coding: utf-8 -*-
"""
Surveying/notes/exam_research/NN_*.md の報告ファイルから、年度別の問題一覧を
圧縮した表として抽出し、Markdown 断片を書き出す。

出力: Surveying/materials/exam/測量士補_測量士_過去問集.md の
GENERATED_TABLES_START 〜 GENERATED_TABLES_END の間を差し替える（前後の手書き部分は保持）。

使い方:  python Surveying/scripts/exam_build_kakomon.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "notes" / "exam_research"
OUT = ROOT / "materials" / "exam" / "測量士補_測量士_過去問集.md"
START = "<!-- GENERATED_TABLES_START（この行から END までは scripts/exam_build_kakomon.py が再生成する。手で編集しない） -->"
END = "<!-- GENERATED_TABLES_END -->"

MAX_SUMMARY = 110   # 概要の最大文字数
MAX_PM = 120        # 午後の小問内容の最大文字数


def split_row(line: str):
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    cells = [c.strip() for c in line[1:-1].split("|")]
    return cells


def is_sep(cells):
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) and any(cells)


def trunc(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("**", "")
    return s if len(s) <= n else s[: n - 1] + "…"


def read_tables(lines):
    """(heading, header, rows) のリストを返す。"""
    tables = []
    h2 = h3 = ""
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            lvl = len(ln) - len(ln.lstrip("#"))
            txt = ln.lstrip("#").strip()
            if lvl <= 2:
                h2, h3 = txt, ""
            else:
                h3 = txt
            i += 1
            continue
        heading = (h2, h3)
        cells = split_row(ln)
        if cells and i + 1 < len(lines):
            nxt = split_row(lines[i + 1])
            if nxt and is_sep(nxt):
                header = cells
                rows = []
                j = i + 2
                while j < len(lines):
                    r = split_row(lines[j])
                    if not r:
                        break
                    rows.append(r)
                    j += 1
                tables.append((heading, header, rows))
                i = j
                continue
        i += 1
    return tables


def find_col(header, keys):
    for k in keys:
        for idx, h in enumerate(header):
            if k in h:
                return idx
    return None


def choice_table(header, rows):
    """択一の問題一覧を No./分野/概要/正解 に圧縮。"""
    c_no = find_col(header, ["No", "問番", "番号", "問"])
    c_field = find_col(header, ["分野"])
    c_sum = find_col(header, ["概要", "内容", "テーマ", "主題"])
    c_ans = find_col(header, ["正解", "解答"])
    if c_no is None or c_sum is None:
        return None
    out = ["| No. | 分野 | 問題の概要 | 正解 |", "|---|---|---|---|"]
    for r in rows:
        if len(r) <= max(c_no, c_sum):
            continue
        no = r[c_no]
        field = r[c_field] if c_field is not None and c_field < len(r) else ""
        field = re.sub(r"（.*?）", "", field)
        summ = trunc(r[c_sum], MAX_SUMMARY)
        ans = r[c_ans] if c_ans is not None and c_ans < len(r) else ""
        ans = trunc(ans, 40)
        out.append(f"| {no} | {field} | {summ} | {ans} |")
    return "\n".join(out)


def pm_table(header, rows):
    """午後の大問表を 小問/内容 に圧縮。"""
    if len(header) < 2:
        return None
    # 見出しの揺れ: | 問 | 小問 | 内容 | …、| 小問 | 内容 | …、| 問 | 小問の内容 | …、
    #              | 問 | 小問 | 求められること | …
    id_cols = [i for i, h in enumerate(header) if h.strip() in ("問", "小問", "設問")]
    c_body = find_col(header, ["内容", "求められること", "求められる"])
    if c_body is None or not id_cols:
        return None
    id_cols = [i for i in id_cols if i != c_body]
    out = ["| 小問 | 内容 |", "|---|---|"]
    for r in rows:
        if len(r) <= c_body:
            continue
        ids = [r[i] for i in id_cols if i < len(r) and r[i] and r[i] not in ("〃", "同上")]
        # 「問A 測量法の条文穴埋め（…）」のように番号列に説明文が入っている報告は、
        # 説明部分を内容側に回す
        body = r[c_body]
        short, extra = [], []
        id_pat = r"[A-Z](?:-\d+)?(?:\s*[,、・]\s*[A-Z]?(?:-\d+)?)*"
        for s in ids:
            s = re.sub(r"^問", "", s).strip()
            s = re.sub(r"^([A-Z])[−－‐–]", r"\1-", s)  # 全角・長音のハイフンを統一
            m = re.match(rf"^({id_pat})([\s（(]*)(.*)$", s)
            if m and m.group(3):
                short.append(re.sub(r"\s*,\s*", ", ", m.group(1)))
                ex = m.group(3)
                if m.group(2).strip() and ex[-1:] in "）)":
                    ex = ex[:-1]
                extra.append(ex)
            elif len(s) > 10:
                extra.append(s)
            else:
                short.append(s)
        # 「B」「B-1」のように重複する表記は後者だけ残す
        if len(short) >= 2 and short[1].startswith(short[0]):
            short = short[1:]
        if extra:
            body = "、".join(e for e in extra if e) + "：" + body
        label = " ".join(short)
        out.append(f"| {label} | {trunc(body, MAX_PM)} |")
    return "\n".join(out)


def process(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tables = read_tables(lines)
    parts = []
    name = path.name
    is_pm = "_pm" in name or re.search(r"_(H30|H29|H28|H27)_shi\.md$", name) is not None
    for (h2, h3), header, rows in tables:
        h = h3 or h2
        if "問題一覧" in h2 or "問題一覧" in h3:
            t = choice_table(header, rows)
            if t:
                parts.append((h if "問題一覧" in h else "問題一覧 " + h, t))
        elif is_pm and ("必須" in h or "選択" in h) and "No" in h:
            t = pm_table(header, rows)
            if t:
                parts.append((h, t))
    return parts


YEAR_ORDER = [
    "R08", "R07", "R06", "R05", "R04", "R03", "R02", "R01",
    "H30", "H29", "H28", "H27", "H26", "H25", "H24", "H23", "H22", "H21", "H20",
]


def label(name: str) -> str:
    m = re.match(r"(\d+)_(.+)\.md", name)
    body = m.group(2)
    era = {"R": "令和", "H": "平成"}
    def yr(tok):
        n = int(tok[1:]); return era[tok[0]] + ("元" if n == 1 else str(n)) + "年"
    toks = body.split("_")
    y = toks[0]
    if len(toks) > 1 and re.fullmatch(r"[HR]\d{2}", toks[1]):
        y = toks[0] + "-" + toks[1]
        toks = [y] + toks[2:]
    if "-" in y:
        a, b = y.split("-")
        if not b[0].isalpha():
            b = a[0] + b
        ytxt = yr(a) + "〜" + yr(b)
    else:
        ytxt = yr(y)
    kind = "_".join(toks[1:])
    kind_txt = {
        "shiho": "測量士補", "shi_am": "測量士 午前", "shi_pm": "測量士 午後", "shi": "測量士",
    }.get(kind, kind)
    return f"{ytxt} {kind_txt}"


def main():
    files = sorted(p for p in SRC.glob("[0-3][0-9]_*.md") if int(p.name[:2]) <= 34)
    out = [""]
    for p in files:
        parts = process(p)
        if not parts:
            continue
        out.append(f"### {label(p.name)}")
        out.append("")
        out.append(f"詳細（形式・出題のポイント・出典）: [notes/exam_research/{p.name}](../../notes/exam_research/{p.name})")
        out.append("")
        for h, t in parts:
            if "問題一覧" not in h or len(parts) > 1:
                out.append(f"**{h}**")
                out.append("")
            out.append(t)
            out.append("")
    body = "\n".join(out).rstrip() + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        cur = OUT.read_text(encoding="utf-8")
        if START in cur and END in cur:
            pre = cur.split(START)[0]
            post = cur.split(END)[1]
            cur = pre + START + "\n" + body + END + post
        else:
            cur = cur.rstrip() + "\n\n" + START + "\n" + body + END + "\n"
    else:
        cur = "# 過去問集（自動生成部分のみ）\n\n" + START + "\n" + body + END + "\n"
    OUT.write_text(cur, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes) from {len(files)} files")


if __name__ == "__main__":
    main()
