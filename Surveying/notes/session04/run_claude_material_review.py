from pathlib import Path
import subprocess,json
folder=Path(__file__).resolve().parent
prompt=(folder/'Claude_教材化後_依頼.md').read_text(encoding='utf-8')
cmd=['claude','-p','--resume','6039ae6a-9523-479f-8c0e-069df7344eb2','--fork-session','--tools','Read,Glob,Grep','--allowedTools','Read,Glob,Grep','--strict-mcp-config','--output-format','json']
with (folder/'kai2/claude_material_result.json').open('wb') as out,(folder/'kai2/claude_material_stderr.log').open('wb') as err:
    p=subprocess.Popen(cmd,cwd=folder.parents[1],stdin=subprocess.PIPE,stdout=out,stderr=err)
    print(f'Claude material review PID={p.pid}',flush=True)
    p.communicate(prompt.encode('utf-8'))
if p.returncode==0:
    v=json.loads((folder/'kai2/claude_material_result.json').read_text(encoding='utf-8-sig'))
    (folder/'Claude_教材化後_返信.md').write_text(v.get('result','')+'\n',encoding='utf-8')
    print(json.dumps({'is_error':v.get('is_error'),'session_id':v.get('session_id'),'length':len(v.get('result',''))}),flush=True)
raise SystemExit(p.returncode)
