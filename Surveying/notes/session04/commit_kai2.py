"""今回の成果物だけを選択する。--stageで準備、--commitで選択範囲だけをコミット。"""
from pathlib import Path
import subprocess,json,sys
ROOT=Path(__file__).resolve().parents[2]
NOTE=ROOT/'notes/session04'
slide=Path('materials/slides/第04回_角測量')
exercise=Path('materials/exercises/第04回_角測量')
paths=[p.relative_to(ROOT).as_posix() for p in (ROOT/slide).glob('*回2*')]
paths += [(slide/n).as_posix() for n in ['build_kai2.mjs','diagram_kai2.mjs','diagram_kai2_base.mjs']]
paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/exercise).glob('*回2.*')]
names=['Claude_Codex_対話.md','Claude_追加対話_依頼.md','Claude_追加対話_返信.md','Claude_教材化後_依頼.md','Claude_教材化後_返信.md','Codex_再検証_回2稿.md','run_claude_followup.py','run_claude_material_review.py','kai2_numeric_check.py','kai2_verified_numbers.json','kai2_inspect.py','build_kai2_content.py','build_kai2_worksheets.py','prepare_kai2_builder.py','finalize_kai2.mjs','hide_kai2_appendix.py','export_kai2_final.py','package_kai2.py','test_kai2_html.py','test_kai2_deck.py','test_kai2_viewer.py','preserve_claude_receipts.py','publicize_kai2_reports.py','kai2_final_review.md','monitor.jsonl','commit_kai2.py','kai2_commit_paths.json','kai2']
paths += ['notes/session04/'+n for n in names]+['notes/worklog.md']
paths=sorted(set(paths))
(NOTE/'kai2_commit_paths.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for rel in paths:
    p=(ROOT/rel).resolve()
    assert p.is_relative_to(ROOT) and p.exists(),str(p)
    for f in p.rglob('*') if p.is_dir() else [p]:
        if f.is_file():assert f.stat().st_size<=50*1024*1024,str(f)
git=['git','-c','safe.directory='+ROOT.parent.as_posix()]
def run(args,**kw):return subprocess.run(git+args,cwd=ROOT,check=True,**kw)
branch=subprocess.check_output(git+['branch','--show-current'],cwd=ROOT,text=True).strip()
assert branch=='main',branch
if '--stage' in sys.argv:
    run(['add','-f','--',*paths],capture_output=True)
    run(['diff','--cached','--check'])
    print(f'選択範囲 {len(paths)}件をstage。50MB超過なし。')
elif '--commit' in sys.argv:
    result=run(['commit','--only','-m','第4回の相互批評を反映し授業計画・解説HTML・授業スライド回2を完成','--',*paths],capture_output=True,text=True,encoding='utf-8')
    print(result.stdout.splitlines()[0])
else:print(json.dumps(paths,ensure_ascii=False,indent=2))
