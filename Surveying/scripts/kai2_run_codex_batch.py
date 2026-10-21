#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第3回・改2 用：資料バッチを Codex（gpt-6-astra、推論 high、計算機操作あり）に順に処理させる。

使い方（Surveying/ で実行）:
    python scripts/kai2_run_codex_batch.py v01 v02 ...      # 指定したバッチを順に実行
    python scripts/kai2_run_codex_batch.py --list           # バッチと結果の有無を表示
入力:
    notes/session03_kai2_20261021/codex/batch_prompt_template.md
    notes/session03_kai2_20261021/codex/batches/batch_<id>.md
出力:
    notes/session03_kai2_20261021/codex/prompts/batch_<id>_prompt.md   （実際に渡したプロンプト）
    notes/session03_kai2_20261021/codex/logs/batch_<id>_stdout.log     （Codex の標準出力）
    notes/session03_kai2_20261021/codex/logs/batch_<id>_last_message.md（Codex の最終返答）
    notes/session03_kai2_20261021/codex/results/資料NNN.md             （Codex が書く）

注意:
    - 承認ゲートとサンドボックスを外す（--dangerously-bypass-approvals-and-sandbox）。
      これ無しでは Chrome へのアクセスが拒否され、シェルも起動できなかった（動作確認 2026-10-21）。
    - Codex は Lecture/AGENTS.md を読んで勝手に commit / push しようとするので、プロンプトで git 操作を禁じている。
    - 終了後に残る codex*.exe を止める。
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("notes/session03_kai2_20261021/codex")
MODEL = "gpt-6-astra"
TIMEOUT_SEC = 90 * 60


def fill_prompt(batch_id: str) -> Path:
    tmpl = (ROOT / "batch_prompt_template.md").read_text(encoding="utf-8")
    table = (ROOT / "batches" / f"batch_{batch_id}.md").read_text(encoding="utf-8").strip()
    n = sum(1 for ln in table.splitlines() if re.match(r"\|\s*\d+\s*\|", ln))
    prompt = (
        tmpl.replace("{{BATCH_NAME}}", f"batch_{batch_id}")
        .replace("{{BATCH_ID}}", f"batch_{batch_id}")
        .replace("{{N}}", str(n))
        .replace("{{No3}}", "NNN")
        .replace("{{BATCH_TABLE}}", table)
    )
    out = ROOT / "prompts" / f"batch_{batch_id}_prompt.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    return out


def batch_numbers(batch_id: str) -> list[int]:
    table = (ROOT / "batches" / f"batch_{batch_id}.md").read_text(encoding="utf-8")
    return [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", table, re.M)]


def kill_codex() -> None:
    """親が死んでいる（孤児になった）codex*.exe だけ止める。並列で動く別バッチの codex は殺さない。"""
    ps = (
        "$alive = (Get-Process).Id; "
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'codex*' -and ($alive -notcontains $_.ParentProcessId) } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)


def run_batch(batch_id: str) -> None:
    prompt = fill_prompt(batch_id)
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "tmp").mkdir(exist_ok=True)
    log = ROOT / "logs" / f"batch_{batch_id}_stdout.log"
    last = ROOT / "logs" / f"batch_{batch_id}_last_message.md"
    codex = shutil.which("codex") or shutil.which("codex.cmd") or "codex"
    cmd = [
        codex, "exec", "-m", MODEL, "-c", "model_reasoning_effort=high",
        "--dangerously-bypass-approvals-and-sandbox", "-C", ".", "--skip-git-repo-check",
        "-o", str(last), "-",
    ]
    t0 = time.time()
    print(f"[{batch_id}] start {time.strftime('%H:%M:%S')}", flush=True)
    with prompt.open("rb") as fin, log.open("wb") as fout:
        try:
            rc = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=subprocess.STDOUT, timeout=TIMEOUT_SEC).returncode
        except subprocess.TimeoutExpired:
            rc = -1
            print(f"[{batch_id}] timeout after {TIMEOUT_SEC}s", flush=True)
    kill_codex()
    done = [n for n in batch_numbers(batch_id) if (ROOT / "results" / f"資料{n:03d}.md").exists()]
    missing = [n for n in batch_numbers(batch_id) if n not in done]
    print(f"[{batch_id}] rc={rc} {int(time.time()-t0)}s results={len(done)} missing={missing}", flush=True)


def list_batches() -> None:
    for p in sorted((ROOT / "batches").glob("batch_*.md")):
        bid = p.stem.replace("batch_", "")
        nums = batch_numbers(bid)
        done = sum((ROOT / "results" / f"資料{n:03d}.md").exists() for n in nums)
        print(f"{bid}: {len(nums)} items, {done} results")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--list"]:
        list_batches()
    else:
        for b in args:
            run_batch(b)
