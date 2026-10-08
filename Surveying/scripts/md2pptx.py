#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Marp 形式の Markdown スライドを編集可能な pptx に変換する。

このリポジトリの環境ではヘッドレスブラウザが動かず Marp CLI の pptx 書き出しが
使えないため、python-pptx で本文をテキストとして書き、数式は次のように扱う。

- ブロック数式 `$$ ... $$` : matplotlib の mathtext で PNG に描画して貼る。
- 行内数式 `$ ... $`      : Unicode（σ, √, Σ, 上付き・下付き）に簡易変換してテキストに埋め込む。

対応する Markdown の要素: 見出し（#, ##, ###）、箇条書き（-, *, 1.）、表、段落、
引用（>）、コードブロック、太字（**）、発表者ノート（<!-- -->）、Marp ディレクティブ
（<!-- _class: lead --> など。lead はタイトル風の中央寄せにする）。

使い方:
    python scripts/md2pptx.py slides.md [-o slides.pptx] [--font "Yu Gothic"]
"""
from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import sys
import tempfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

# ---------------------------------------------------------------------------
# 1. Markdown の分割
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            text = text[end + 4 :]
            for line in fm.splitlines():
                m = re.match(r"^(\w+):\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip()
    return meta, text


def split_slides(body: str) -> list[str]:
    slides, cur, in_code = [], [], False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.strip() == "---":
            slides.append("\n".join(cur))
            cur = []
            continue
        cur.append(line)
    slides.append("\n".join(cur))
    return [s for s in slides if s.strip()]


DIRECTIVE_RE = re.compile(r"^\s*_?(class|paginate|header|footer|backgroundColor|color|theme|style)\s*:", re.I)


def extract_notes(slide_md: str) -> tuple[str, list[str], dict]:
    """HTML コメントを発表者ノートとディレクティブに分ける。"""
    notes, directives = [], {}

    def repl(m):
        inner = m.group(1).strip()
        if DIRECTIVE_RE.match(inner):
            for part in inner.splitlines():
                mm = re.match(r"^\s*_?(\w+)\s*:\s*(.*)$", part)
                if mm:
                    directives[mm.group(1).lower()] = mm.group(2).strip()
        else:
            notes.append(inner)
        return ""

    md = re.sub(r"<!--(.*?)-->", repl, slide_md, flags=re.S)
    return md, notes, directives


# ---------------------------------------------------------------------------
# 2. 行内数式の Unicode 変換
# ---------------------------------------------------------------------------

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ",
    "lambda": "λ", "mu": "μ", "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ",
    "omega": "ω", "Delta": "Δ", "Sigma": "Σ", "Omega": "Ω", "varepsilon": "ε",
}
SYMBOLS = {
    "sum": "Σ", "sqrt": "√", "pm": "±", "mp": "∓", "times": "×", "cdot": "·", "propto": "∝",
    "approx": "≈", "neq": "≠", "ne": "≠", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
    "infty": "∞", "ldots": "…", "cdots": "⋯", "dots": "…", "to": "→", "rightarrow": "→",
    "Rightarrow": "⇒", "leftarrow": "←", "quad": "  ", "qquad": "    ", ",": " ", ";": " ",
    "!": "", "circ": "°", "degree": "°", "prime": "′", "partial": "∂", "in": "∈",
    "min": "min", "max": "max", "lim": "lim", "log": "log", "ln": "ln", "exp": "exp",
    "sin": "sin", "cos": "cos", "tan": "tan",
}
SUP = {c: s for c, s in zip("0123456789+-=()n i", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ ⁱ")}
SUB = {c: s for c, s in zip("0123456789+-=()aeijkmnoprstuvwx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑᵢⱼₖₘₙₒₚᵣₛₜᵤᵥₓ")}
COMBINING_BAR = "\u0304"
COMBINING_HAT = "\u0302"


def _take_group(s: str, i: int) -> tuple[str, int]:
    """s[i] が '{' のとき対応する '}' までを返す。そうでなければ 1 文字。"""
    if i < len(s) and s[i] == "{":
        depth, j = 0, i
        while j < len(s):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1 : j], j + 1
            j += 1
        return s[i + 1 :], len(s)
    if i < len(s) and s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        if m:
            return m.group(0), i + len(m.group(0))
    return (s[i], i + 1) if i < len(s) else ("", i)


# 上付き・下付きは Unicode 文字ではなく PowerPoint の書式（baseline）で表す。
# latex_to_unicode の出力に制御文字で範囲を埋め込み、inline_to_runs で run に分ける。
SUB_ON, SUB_OFF, SUP_ON, SUP_OFF = "\x02", "\x03", "\x04", "\x05"


def _script(text: str, table: dict, marker: str) -> str:
    conv = latex_to_unicode(text)
    if table is SUP:
        return SUP_ON + conv + SUP_OFF
    return SUB_ON + conv + SUB_OFF


def split_scripts(s: str) -> list[tuple[str, dict]]:
    """制御文字で囲まれた上付き・下付き範囲を (文字列, 書式) に分ける。入れ子は外側を優先。"""
    runs: list[tuple[str, dict]] = []
    stack: list[str] = []
    buf: list[str] = []

    def emit():
        if buf:
            fmt = {"math": True}
            if stack:
                fmt[stack[0]] = True
            runs.append(("".join(buf), fmt))
            buf.clear()

    for ch in s:
        if ch in (SUB_ON, SUP_ON):
            emit()
            stack.append("sub" if ch == SUB_ON else "sup")
        elif ch in (SUB_OFF, SUP_OFF):
            emit()
            if stack:
                stack.pop()
        else:
            buf.append(ch)
    emit()
    return runs


def strip_scripts(s: str) -> str:
    """制御文字を取り除いた素のテキスト（ノート・タイトル用）。"""
    return re.sub("[\x02\x03\x04\x05]", "", s)


def latex_to_unicode(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name in ("frac", "dfrac", "tfrac"):
                a, i = _take_group(s, i)
                b, i = _take_group(s, i)
                a, b = latex_to_unicode(a), latex_to_unicode(b)
                a = a if len(a) <= 1 or a.isalnum() else f"({a})"
                b = b if len(b) <= 1 or b.isalnum() else f"({b})"
                out.append(f"{a}/{b}")
            elif name == "sqrt":
                a, i = _take_group(s, i)
                a = latex_to_unicode(a)
                out.append("√" + (a if len(a) <= 1 else f"({a})"))
            elif name in ("bar", "overline"):
                a, i = _take_group(s, i)
                a = latex_to_unicode(a)
                out.append(a[0] + COMBINING_BAR + a[1:] if a else "")
            elif name == "hat":
                a, i = _take_group(s, i)
                a = latex_to_unicode(a)
                out.append(a[0] + COMBINING_HAT + a[1:] if a else "")
            elif name in ("mathrm", "text", "textrm", "mathbf", "textbf", "mathit", "operatorname"):
                a, i = _take_group(s, i)
                out.append(latex_to_unicode(a))
            elif name in ("left", "right", "displaystyle", "textstyle", "big", "Big"):
                pass
            elif name in GREEK:
                out.append(GREEK[name])
            elif name in SYMBOLS:
                out.append(SYMBOLS[name])
            elif name in ("{", "}", "%", "&", "_", "$", "#"):
                out.append(name)
            elif name == "\\":
                out.append("\n")
            else:
                out.append(name)
        elif ch == "^":
            a, i = _take_group(s, i + 1)
            out.append(_script(a, SUP, "^"))
        elif ch == "_":
            a, i = _take_group(s, i + 1)
            out.append(_script(a, SUB, "_"))
        elif ch in "{}":
            i += 1
        elif ch == "~":
            out.append(" ")
            i += 1
        elif ch == "&":
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


INLINE_MATH_RE = re.compile(r"\$([^$\n]+?)\$")


def inline_to_runs(text: str) -> list[tuple[str, dict]]:
    """行内 Markdown（太字・行内数式・HTML タグ）を (文字列, 書式) のリストに変換する。"""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?(span|div|b|i|u|em|strong|small|sup|sub|code)[^>]*>", "", text)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    runs: list[tuple[str, dict]] = []
    # 太字 **x**, 行内数式 $x$, コード `x`
    token_re = re.compile(r"(\*\*(.+?)\*\*|\$([^$\n]+?)\$|`([^`]+)`)")
    pos = 0
    for m in token_re.finditer(text):
        if m.start() > pos:
            runs.append((text[pos : m.start()], {}))
        if m.group(2) is not None:
            inner = inline_to_runs(m.group(2))
            runs.extend((t, {**f, "bold": True}) for t, f in inner)
        elif m.group(3) is not None:
            runs.extend(split_scripts(latex_to_unicode(m.group(3))))
        else:
            runs.append((m.group(4), {"code": True}))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], {}))
    return runs


# ---------------------------------------------------------------------------
# 3. ブロック数式の描画
# ---------------------------------------------------------------------------

def _brace_bare_args(s: str) -> str:
    r"""\frac1n, \sqrt5 のように波括弧なしの引数を {} で囲む（mathtext は必須）。"""
    out, i = [], 0
    two = {"frac", "dfrac", "tfrac"}
    one = {"sqrt", "bar", "hat", "vec", "overline"}
    while i < len(s):
        m = re.match(r"\\([A-Za-z]+)", s[i:])
        if m and m.group(1) in two | one:
            out.append(m.group(0))
            i += len(m.group(0))
            for _ in range(2 if m.group(1) in two else 1):
                while i < len(s) and s[i] == " ":
                    i += 1
                if i < len(s) and s[i] == "[":  # \sqrt[3]{x}
                    j = s.find("]", i)
                    out.append(s[i : j + 1])
                    i = j + 1
                    while i < len(s) and s[i] == " ":
                        i += 1
                if i < len(s) and s[i] == "{":
                    g, i = _take_group(s, i)
                    out.append("{" + _brace_bare_args(g) + "}")
                else:
                    g, i = _take_group(s, i)
                    out.append("{" + g + "}")
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def render_math_png(latex: str, outdir: str, fontsize: int = 22) -> str | None:
    """mathtext で PNG を作る。失敗したら None。"""
    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import mathtext
        from matplotlib.font_manager import FontProperties
    except Exception:  # pragma: no cover
        return None
    s = latex.strip()
    s = re.sub(r"\\begin\{(aligned|align\*?|gathered|cases)\}|\\end\{(aligned|align\*?|gathered|cases)\}", "", s)
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac").replace("\\displaystyle", "")
    s = re.sub(r"\\text(?:rm)?\{([^}]*)\}", r"\\mathrm{\1}", s)
    s = s.replace("\\,", "\\ ").replace("\\;", "\\ ").replace("\\!", "")
    s = s.replace("&", "")
    s = s.replace("\\boxed{", "{")  # mathtext に boxed はない
    s = _brace_bare_args(s)
    lines = [re.sub(r"\s*\n\s*", " ", ln).strip() for ln in re.split(r"\\\\", s) if ln.strip()]
    if not lines:
        return None
    # 日本語などを含むものは mathtext で描けないので諦める
    if any(ord(c) > 0x2FFF for c in s):
        return None
    key = hashlib.md5((s + str(fontsize)).encode("utf-8")).hexdigest()[:12]
    path = os.path.join(outdir, f"eq_{key}.png")
    if os.path.exists(path):
        return path
    try:
        if len(lines) == 1:
            mathtext.math_to_image(f"${lines[0]}$", path, dpi=300, format="png",
                                   prop=FontProperties(size=fontsize))
        else:
            import matplotlib.pyplot as plt

            fig = plt.figure(figsize=(0.1, 0.1))
            fig.patch.set_alpha(0.0)
            txt = "\n".join(f"${ln}$" for ln in lines)
            t = fig.text(0, 0, txt, fontsize=fontsize, linespacing=1.6)
            fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.05, transparent=True)
            plt.close(fig)
        return path
    except Exception as e:  # mathtext が解釈できない式
        sys.stderr.write(f"[md2pptx] mathtext failed: {e}\n   {s}\n")
        return None


# ---------------------------------------------------------------------------
# 4. ブロック解析
# ---------------------------------------------------------------------------

def parse_blocks(md: str) -> list[dict]:
    lines = md.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            blocks.append({"type": "code", "text": "\n".join(buf)})
            i = j + 1
            continue
        if s.startswith("$$"):
            inner = s[2:]
            if inner.rstrip().endswith("$$") and len(inner.rstrip()) >= 2:
                blocks.append({"type": "math", "latex": inner.rstrip()[:-2]})
                i += 1
                continue
            buf = [inner] if inner.strip() else []
            j = i + 1
            while j < len(lines) and "$$" not in lines[j]:
                buf.append(lines[j])
                j += 1
            if j < len(lines):
                buf.append(lines[j].replace("$$", ""))
            blocks.append({"type": "math", "latex": "\n".join(buf)})
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = lines[i].strip().strip("|")
                if not re.match(r"^[\s:\-|]+$", row):
                    rows.append([c.strip() for c in re.split(r"(?<!\\)\|", row)])
                i += 1
            blocks.append({"type": "table", "rows": rows})
            continue
        if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line):
            items = []
            while i < len(lines):
                mm = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
                if mm:
                    indent = len(mm.group(1).replace("\t", "    "))
                    items.append({"level": min(indent // 2, 4), "text": mm.group(3),
                                  "ordered": mm.group(2)[0].isdigit()})
                    i += 1
                elif lines[i].strip() and lines[i].startswith("  ") and items:
                    items[-1]["text"] += " " + lines[i].strip()  # 継続行
                    i += 1
                else:
                    break
            blocks.append({"type": "list", "items": items})
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append({"type": "quote", "text": " ".join(buf)})
            continue
        # 段落
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|\$\$|\||```|>|\s*([-*+]|\d+[.)])\s)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            blocks.append({"type": "para", "text": " ".join(buf)})
        else:
            i += 1
    return blocks


# ---------------------------------------------------------------------------
# 5. pptx 生成
# ---------------------------------------------------------------------------

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.6)
TITLE_H = Inches(1.0)
FOOT_H = Inches(0.4)
ACCENT = RGBColor(0x1F, 0x4E, 0x79)
GRAY = RGBColor(0x55, 0x55, 0x55)


class Builder:
    def __init__(self, font: str, title: str):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = SLIDE_W, SLIDE_H
        self.blank = self.prs.slide_layouts[6]
        self.font = font
        self.deck_title = title
        self.tmpdir = tempfile.mkdtemp(prefix="md2pptx_")
        self.page = 0

    # --- 文字列の書き込み ---------------------------------------------------
    def _write_runs(self, par, runs, size, color=None, bold=False):
        for text, fmt in runs:
            for k, piece in enumerate(text.split("\n")):
                if k > 0:
                    par.add_line_break()
                if not piece:
                    continue
                r = par.add_run()
                r.text = piece
                r.font.name = self.font
                r.font.size = Pt(size)
                r.font.bold = bold or fmt.get("bold", False)
                if fmt.get("code"):
                    r.font.name = "Consolas"
                if fmt.get("math"):
                    r.font.name = "Cambria Math"
                if fmt.get("sub"):
                    r.font._element.set("baseline", "-25000")
                elif fmt.get("sup"):
                    r.font._element.set("baseline", "30000")
                if color is not None:
                    r.font.color.rgb = color

    def _textbox(self, slide, left, top, width, height):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.05)
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        return tb, tf

    # --- 1 枚 ---------------------------------------------------------------
    def add_slide(self, blocks: list[dict], notes: list[str], directives: dict, paginate: bool):
        self.page += 1
        slide = self.prs.slides.add_slide(self.blank)
        lead = "lead" in directives.get("class", "")

        # 見出し（最初の h1/h2 をタイトル扱い）
        title_block = None
        for b in blocks:
            if b["type"] == "heading" and b["level"] <= 2:
                title_block = b
                break
        body = [b for b in blocks if b is not title_block]

        # 本文の密度から文字サイズを決める
        n_lines = self._estimate_lines(body)
        if n_lines <= 7:
            size = 22
        elif n_lines <= 10:
            size = 20
        elif n_lines <= 13:
            size = 18
        else:
            size = 16

        if lead or (title_block is not None and not body):
            # タイトル風: 中央寄せ
            tb, tf = self._textbox(slide, MARGIN, Inches(1.8), SLIDE_W - 2 * MARGIN, Inches(1.6))
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            if title_block:
                self._write_runs(p, inline_to_runs(title_block["text"]), 40, ACCENT, bold=True)
            top = Inches(3.6)
            tb2, tf2 = self._textbox(slide, MARGIN, top, SLIDE_W - 2 * MARGIN, Inches(3.2))
            first = True
            for b in body:
                for text in self._flatten(b):
                    p = tf2.paragraphs[0] if first else tf2.add_paragraph()
                    first = False
                    p.alignment = PP_ALIGN.CENTER
                    self._write_runs(p, inline_to_runs(text), 22, GRAY)
            self._footer(slide, paginate)
            self._notes(slide, notes)
            return

        top = MARGIN
        if title_block is not None:
            tb, tf = self._textbox(slide, MARGIN, Inches(0.35), SLIDE_W - 2 * MARGIN, TITLE_H)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            self._write_runs(p, inline_to_runs(title_block["text"]), 30, ACCENT, bold=True)
            # 下線
            ln = slide.shapes.add_shape(1, MARGIN, Inches(1.3), SLIDE_W - 2 * MARGIN, Emu(18000))
            ln.fill.solid()
            ln.fill.fore_color.rgb = ACCENT
            ln.line.fill.background()
            top = Inches(1.5)

        avail_h = SLIDE_H - top - FOOT_H - Inches(0.1)
        width = SLIDE_W - 2 * MARGIN
        self._place_body(slide, body, MARGIN, top, width, avail_h, size)
        self._footer(slide, paginate)
        self._notes(slide, notes)

    def _flatten(self, b):
        if b["type"] in ("para", "quote", "code"):
            return [b["text"]]
        if b["type"] == "heading":
            return [b["text"]]
        if b["type"] == "list":
            return [it["text"] for it in b["items"]]
        if b["type"] == "math":
            return [strip_scripts(latex_to_unicode(b["latex"]))]
        if b["type"] == "table":
            return [" | ".join(r) for r in b["rows"]]
        return []

    @staticmethod
    def _display_width(text: str) -> float:
        """全角 1、半角 0.55 として折り返し見積り用の幅を数える。"""
        t = re.sub(r"\*\*|\$|`", "", text)
        return sum(1.0 if ord(c) > 0x2E7F else 0.55 for c in t)

    def _wrapped(self, text: str, cols: float) -> int:
        return max(1, math.ceil(self._display_width(text) / cols))

    def _estimate_lines(self, body, cols: float = 40.0):
        """本文の行数見積り。cols は 1 行に入る全角文字数の目安。"""
        n = 0
        for b in body:
            if b["type"] == "list":
                n += sum(self._wrapped(it["text"], cols - 2) for it in b["items"])
            elif b["type"] == "table":
                n += len(b["rows"]) * 1.3
            elif b["type"] == "math":
                n += 2.2 * max(1, len(re.split(r"\\\\", b["latex"])))
            elif b["type"] == "heading":
                n += 1.3
            elif b["type"] == "code":
                n += b["text"].count("\n") + 1
            else:
                n += self._wrapped(b.get("text", ""), cols)
        return n

    def _place_body(self, slide, body, left, top, width, avail_h, size):
        """ブロックを上から順に置く。テキストはまとめて 1 つのテキストボックス、表と数式は別シェイプ。"""
        y = top
        line_h = Pt(size * 1.55)
        pending: list[dict] = []

        def flush():
            nonlocal y, pending
            if not pending:
                return
            cols = (width / 914400) * 72 / size  # 1 行に入る全角文字数
            n = sum(self._estimate_lines([b], cols) for b in pending)
            h = int(line_h * n) + Inches(0.15)
            tb, tf = self._textbox(slide, left, y, width, h)
            first = True
            for b in pending:
                if b["type"] == "heading":
                    p = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    self._write_runs(p, inline_to_runs(b["text"]), size + 2, ACCENT, bold=True)
                    p.space_before = Pt(6)
                elif b["type"] == "list":
                    for it in b["items"]:
                        p = tf.paragraphs[0] if first else tf.add_paragraph()
                        first = False
                        p.level = it["level"]
                        bullet = "• " if it["level"] == 0 else "– "
                        runs = [(bullet, {})] + inline_to_runs(it["text"])
                        self._write_runs(p, runs, size - 2 * it["level"])
                        p.space_after = Pt(4)
                elif b["type"] == "quote":
                    p = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    self._write_runs(p, inline_to_runs(b["text"]), size, GRAY)
                elif b["type"] == "code":
                    for ln in b["text"].split("\n"):
                        p = tf.paragraphs[0] if first else tf.add_paragraph()
                        first = False
                        self._write_runs(p, [(ln, {"code": True})], size - 4)
                elif b["type"] == "math":  # 描画に失敗した数式
                    p = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    p.alignment = PP_ALIGN.CENTER
                    self._write_runs(p, split_scripts(latex_to_unicode(b["latex"])), size + 2)
                else:
                    p = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    self._write_runs(p, inline_to_runs(b["text"]), size)
                    p.space_after = Pt(6)
            y += h
            pending = []

        for b in body:
            if b["type"] == "table":
                flush()
                y = self._add_table(slide, b["rows"], left, y, width, size)
            elif b["type"] == "math":
                png = render_math_png(b["latex"], self.tmpdir, fontsize=max(14, size))
                if png is None:
                    pending.append(b)
                    continue
                flush()
                y = self._add_picture(slide, png, left, y, width, size)
            else:
                pending.append(b)
        flush()
        if y > top + avail_h + Inches(0.3):
            sys.stderr.write(f"[md2pptx] warning: slide {self.page} の本文がはみ出す可能性があります\n")

    def _add_table(self, slide, rows, left, y, width, size):
        if not rows:
            return y
        ncols = max(len(r) for r in rows)
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        tsize = max(12, size - 4)
        row_h = Pt(tsize * 2.0)
        h = int(row_h * len(rows))
        shape = slide.shapes.add_table(len(rows), ncols, left, y, width, h)
        table = shape.table
        for ri, r in enumerate(rows):
            for ci, cell_text in enumerate(r):
                cell = table.cell(ri, ci)
                cell.margin_left = cell.margin_right = Inches(0.06)
                cell.margin_top = cell.margin_bottom = Inches(0.03)
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                self._write_runs(p, inline_to_runs(cell_text), tsize, bold=(ri == 0))
                if ri == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xDC, 0xE6, 0xF1)
                    for r_ in p.runs:
                        r_.font.color.rgb = RGBColor(0x1F, 0x1F, 0x1F)
                else:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if ri % 2 else RGBColor(0xF5, 0xF7, 0xFA)
        return y + h + Inches(0.15)

    def _add_picture(self, slide, png, left, y, width, size):
        from PIL import Image

        with Image.open(png) as im:
            w_px, h_px = im.size
        # 300 dpi で描いたので 1 px = 1/300 in。数式の文字高さをテキストに合わせて 1.15 倍。
        scale = 1.3
        w_in, h_in = w_px / 300 * scale, h_px / 300 * scale
        max_w = (width / 914400) * 0.95
        if w_in > max_w:
            h_in *= max_w / w_in
            w_in = max_w
        pic_left = left + int((width - Inches(w_in)) / 2)
        slide.shapes.add_picture(png, pic_left, y + Inches(0.08), Inches(w_in), Inches(h_in))
        return y + Inches(h_in) + Inches(0.25)

    def _footer(self, slide, paginate):
        tb, tf = self._textbox(slide, MARGIN, SLIDE_H - FOOT_H - Inches(0.05), SLIDE_W - 2 * MARGIN, FOOT_H)
        p = tf.paragraphs[0]
        self._write_runs(p, [(self.deck_title, {})], 11, GRAY)
        if paginate:
            tb2, tf2 = self._textbox(slide, SLIDE_W - MARGIN - Inches(1.2), SLIDE_H - FOOT_H - Inches(0.05), Inches(1.2), FOOT_H)
            p2 = tf2.paragraphs[0]
            p2.alignment = PP_ALIGN.RIGHT
            self._write_runs(p2, [(str(self.page), {})], 11, GRAY)

    def _notes(self, slide, notes):
        if notes:
            slide.notes_slide.notes_text_frame.text = "\n\n".join(notes)

    def save(self, path):
        self.prs.save(path)


def convert(md_path: str, out_path: str, font: str, title: str | None):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    meta, body = split_frontmatter(text)
    slides_md = split_slides(body)
    paginate = meta.get("paginate", "false").lower() == "true"
    if title is None:
        title = meta.get("title") or os.path.splitext(os.path.basename(md_path))[0]
        # 1 枚目の h1 をデッキ名に使う
        first_blocks = parse_blocks(extract_notes(slides_md[0])[0]) if slides_md else []
        for b in first_blocks:
            if b["type"] == "heading":
                title = re.sub(r"\*\*|\$", "", b["text"])
                break
    builder = Builder(font, title)
    for s in slides_md:
        md, notes, directives = extract_notes(s)
        blocks = parse_blocks(md)
        if not blocks and not notes:
            continue
        builder.add_slide(blocks, notes, directives, paginate)
    builder.save(out_path)
    print(f"{out_path}: {builder.page} slides")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("-o", "--output")
    ap.add_argument("--font", default="Yu Gothic")
    ap.add_argument("--title", default=None, help="フッターに入れるデッキ名（省略時は 1 枚目の見出し）")
    a = ap.parse_args()
    out = a.output or os.path.splitext(a.markdown)[0] + ".pptx"
    convert(a.markdown, out, a.font, a.title)


if __name__ == "__main__":
    main()
