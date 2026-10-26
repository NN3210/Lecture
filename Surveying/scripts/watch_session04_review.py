"""第4回制作と批評の更新を300秒ごとに観測する。ログ本文や個人情報は保存しない。"""
from pathlib import Path
from datetime import datetime
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'notes' / 'session04' / 'monitor.jsonl'
SESSION_NAME = '6039ae6a-9523-479f-8c0e-069df7344eb2.jsonl'


def stamp(path):
    if not path.exists():
        return None
    s = path.stat()
    return {'modified': datetime.fromtimestamp(s.st_mtime).astimezone().isoformat(), 'bytes': s.st_size}


def snapshot():
    # 実行ユーザーが異なるサンドボックスでも、既知ユーザーのログを読む。
    profile = ROOT.parents[4]
    project_key = str(ROOT).replace(':', '-').replace('\\', '-')
    session = profile / '.claude' / 'projects' / project_key / SESSION_NAME
    command = "Get-Process -Name claude,codex -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,@{N='Started';E={$_.StartTime.ToString('o')}} | ConvertTo-Json -Compress"
    proc = subprocess.run(['powershell', '-NoProfile', '-Command', command], capture_output=True, text=True)
    try:
        processes = json.loads(proc.stdout) if proc.stdout.strip() else []
    except ValueError:
        processes = {'status': 'unreadable'}
    files = {}
    for folder in [ROOT / 'notes' / 'session04', ROOT / 'materials' / 'slides' / '第04回_角測量']:
        if folder.exists():
            for p in folder.rglob('*'):
                if p.is_file() and p != OUT:
                    files[p.relative_to(ROOT).as_posix()] = stamp(p)
    record = {'checked_at': datetime.now().astimezone().isoformat(), 'claude_session': stamp(session), 'processes': processes, 'files': files}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(json.dumps(record, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    while True:
        start = time.monotonic()
        snapshot()
        time.sleep(max(0, 300 - (time.monotonic() - start)))
