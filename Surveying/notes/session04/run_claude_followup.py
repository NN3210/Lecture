"""既存の会話履歴を分岐し、Claude Code に読み取り専用で再検証を依頼。"""
from pathlib import Path
import subprocess
import json

folder = Path(__file__).resolve().parent
root = folder.parents[1]
prompt = (folder/'Claude_追加対話_依頼.md').read_text(encoding='utf-8')
command = ['claude', '-p', '--resume', '6039ae6a-9523-479f-8c0e-069df7344eb2',
           '--fork-session', '--tools', 'Read,Glob,Grep', '--allowedTools', 'Read,Glob,Grep',
           '--strict-mcp-config', '--output-format', 'json']
with (folder/'claude_followup_result.json').open('wb') as out, (folder/'claude_followup_stderr.log').open('wb') as err:
    p = subprocess.Popen(command, cwd=root, stdin=subprocess.PIPE, stdout=out, stderr=err)
    print(f'Claude follow-up PID={p.pid}', flush=True)
    p.communicate(prompt.encode('utf-8'))
    print(f'exit={p.returncode}', flush=True)
if p.returncode == 0:
    result = json.loads((folder/'claude_followup_result.json').read_text(encoding='utf-8-sig'))
    reply = result.get('result', '')
    (folder/'Claude_追加対話_返信.md').write_text(reply+'\n', encoding='utf-8')
    print(json.dumps({'is_error': result.get('is_error'), 'session_id': result.get('session_id'),
                      'reply_characters': len(reply)}, ensure_ascii=True), flush=True)
raise SystemExit(p.returncode)
