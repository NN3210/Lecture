#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""資料バッチを Codex CLI（既定 gpt-6-astra、推論 high、計算機操作あり）に 1 本ずつ順に処理させる。

使い方（科目のプロジェクト直下で実行。長いので run_in_background で）:
    python -I .claude/skills/lecture-structure-extract/scripts/run_codex_batch.py --root notes/session05_traverse_20261101 v01 v02
    python -I .../run_codex_batch.py --root <root> --list              バッチごとの件数と results 数
    python -I .../run_codex_batch.py --root <root> --light v03r        省メモリ版の雛形で
    オプション: --model gpt-6-astra  --effort high  --timeout-min 90
読むもの: <root>/codex/batch_prompt_template.md（--light なら _light）、<root>/codex/batches/batch_<id>.md
書くもの: <root>/codex/prompts/batch_<id>_prompt.md、codex/logs/batch_<id>_stdout.log（除外）、codex/logs/batch_<id>_last_message.md
Codex 自身が codex/results/資料NNN.md と codex/logs/<id>_操作ログ.md を書く。
同時に 2 本走らせない。字幕先取り・PowerPoint COM とも同時にしない（メモリ）。
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def fill_prompt(codex: Path, batch_id: str, template: str) -> Path:
    tmpl = (codex / template).read_text(encoding="utf-8")
    table = (codex / "batches" / f"batch_{batch_id}.md").read_text(encoding="utf-8").strip()
    n = sum(1 for ln in table.splitlines() if re.match(r"\|\s*\d+\s*\|", ln))
    prompt = (tmpl.replace("{{BATCH_NAME}}", f"batch_{batch_id}").replace("{{BATCH_ID}}", f"batch_{batch_id}")
              .replace("{{N}}", str(n)).replace("{{No3}}", "NNN").replace("{{BATCH_TABLE}}", table))
    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", prompt)))
    if left:
        print(f"警告: 雛形に埋まっていない placeholder がある {left}（init_codex_dir.py をやり直す）")
    out = codex / "prompts" / f"batch_{batch_id}_prompt.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    return out


def batch_numbers(codex: Path, batch_id: str) -> list[int]:
    table = (codex / "batches" / f"batch_{batch_id}.md").read_text(encoding="utf-8")
    return [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", table, re.M)]


def kill_codex() -> None:
    """親が死んでいる（孤児になった）codex*.exe だけ止める。"""
    ps = ("$alive = (Get-Process).Id; "
          "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'codex*' -and ($alive -notcontains $_.ParentProcessId) } | "
          "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)


def run_batch(codex: Path, batch_id: str, template: str, model: str, effort: str, timeout_sec: int) -> None:
    prompt = fill_prompt(codex, batch_id, template)
    for d in ("logs", "results", "tmp"):
        (codex / d).mkdir(exist_ok=True)
    log = codex / "logs" / f"batch_{batch_id}_stdout.log"
    last = codex / "logs" / f"batch_{batch_id}_last_message.md"
    exe = shutil.which("codex") or shutil.which("codex.cmd") or "codex"
    cmd = [exe, "exec", "-m", model, "-c", f"model_reasoning_effort={effort}", "--dangerously-bypass-approvals-and-sandbox",
           "-C", ".", "--skip-git-repo-check", "-o", str(last), "-"]
    t0 = time.time()
    print(f"[{batch_id}] start {time.strftime('%H:%M:%S')} template={template}", flush=True)
    with prompt.open("rb") as fin, log.open("wb") as fout:
        try:
            rc = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=subprocess.STDOUT, timeout=timeout_sec).returncode
        except subprocess.TimeoutExpired:
            rc = -1
            print(f"[{batch_id}] timeout after {timeout_sec}s", flush=True)
    kill_codex()
    nums = batch_numbers(codex, batch_id)
    done = [n for n in nums if (codex / "results" / f"資料{n:03d}.md").exists()]
    missing = [n for n in nums if n not in done]
    print(f"[{batch_id}] rc={rc} {int(time.time() - t0)}s results={len(done)}/{len(nums)} missing={missing}", flush=True)


def list_batches(codex: Path) -> None:
    total = have = 0
    for p in sorted((codex / "batches").glob("batch_*.md")):
        bid = p.stem.replace("batch_", "")
        nums = batch_numbers(codex, bid)
        done = sum((codex / "results" / f"資料{n:03d}.md").exists() for n in nums)
        total += len(nums)
        have += done
        print(f"{bid}: {len(nums)} items, {done} results")
    n_res = len(list((codex / "results").glob("資料*.md"))) if (codex / "results").exists() else 0
    print(f"results 合計 {n_res} ファイル（バッチ行の合計 {total}、再実行バッチは重複して数える）")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--light", action="store_true", help="省メモリ版の雛形を使う")
    ap.add_argument("--model", default="gpt-6-astra")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--timeout-min", type=int, default=90)
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    codex = Path(a.root) / "codex"
    if a.list or not a.ids:
        list_batches(codex)
        return
    template = "batch_prompt_template_light.md" if a.light else "batch_prompt_template.md"
    if not (codex / template).exists():
        sys.exit(f"雛形が無い: {codex / template}（init_codex_dir.py を先に実行）")
    for b in a.ids:
        if not (codex / "batches" / f"batch_{b}.md").exists():
            print(f"無い: batch_{b}.md（飛ばす）")
            continue
        run_batch(codex, b, template, a.model, a.effort, a.timeout_min * 60)


if __name__ == "__main__":
    main()
