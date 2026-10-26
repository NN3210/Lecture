"""公開する対話本文と照合情報を残し、重複するCLI実行メタデータを除く。"""
from pathlib import Path
import json,hashlib
F=Path(__file__).resolve().parent
ROOT=F.parents[1]
out=F/'kai2/claude_dialogue_receipts.json'
rows=json.loads(out.read_text(encoding='utf-8')) if out.exists() else []
for result,reply in [(F/'claude_followup_result.json',F/'Claude_追加対話_返信.md'),(F/'kai2/claude_material_result.json',F/'Claude_教材化後_返信.md')]:
    if not result.exists():continue
    v=json.loads(result.read_text(encoding='utf-8-sig'))
    assert v.get('is_error') is False
    assert reply.read_text(encoding='utf-8').rstrip()==v['result'].rstrip()
    rows.append({'reply_file':reply.relative_to(ROOT).as_posix(),'session_id':v['session_id'],'is_error':v['is_error'],'sha256':hashlib.sha256(reply.read_bytes()).hexdigest(),'mode':'Claude Code CLI / 元の会話履歴から分岐 / Read,Glob,Grepのみ'})
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for f in [F/'claude_followup_result.json',F/'claude_followup_stderr.log',F/'kai2/claude_material_result.json',F/'kai2/claude_material_stderr.log']:
    assert f.resolve().is_relative_to(ROOT.resolve())
    if f.exists():f.unlink()
print(f'Claudeの実際の返信{len(rows)}件とSHA-256を保存')
