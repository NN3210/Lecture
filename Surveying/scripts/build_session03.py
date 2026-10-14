#!/usr/bin/env python3
"""第3回のMarkdownから、本文・表・Office数式が編集可能なPPTXとPDFを生成する。"""
from pathlib import Path
from datetime import datetime
import os,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'materials/slides/第03回_測量の座標'
HOME_DIR=Path.home()
def main():
    env=os.environ.copy()
    deps=HOME_DIR/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
    modules=Path(env.get('ARTIFACT_MODULES',str(deps/'node/node_modules')))
    node=modules.parent/'bin/node.exe'
    env['ARTIFACT_MODULES']=str(modules)
    if 'MARP_MODULES' not in env:
        matches=list((HOME_DIR/'AppData/Local/npm-cache/_npx').glob('*/node_modules/katex/package.json'))
        if not matches:raise RuntimeError('MARP_MODULESを指定してください。')
        env['MARP_MODULES']=str(matches[0].parents[1])
    if 'PRESENTATION_SKILL' not in env:
        matches=list((HOME_DIR/'.codex/plugins/cache/openai-primary-runtime/presentations').glob('*/skills/presentations/SKILL.md'))
        if not matches:raise RuntimeError('PRESENTATION_SKILLを指定してください。')
        env['PRESENTATION_SKILL']=str(max(matches,key=lambda p:p.stat().st_mtime).parent)
    env.setdefault('RUNTIME_PYTHON',str(deps/'python/python.exe'))
    env['PYTHONIOENCODING']='utf-8'
    def run(*args):subprocess.run([str(a) for a in args],cwd=ROOT,env=env,check=True)
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
    candidate=f'native-{stamp}.pptx'
    final=f'slides_validated_{stamp}.pptx'
    run(node,ROOT/'scripts/build_session03_visual.mjs')
    run(sys.executable,ROOT/'scripts/patch_session03_math.py',candidate)
    run(node,ROOT/'scripts/finalize_session03.mjs',candidate,final)
    run('powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',ROOT/'scripts/pptx_export.ps1','-Pptx',OUT/final,'-Pdf',OUT/Path(final).with_suffix('.pdf'),'-NoPng')
    shutil.copyfile(OUT/final,OUT/'slides.pptx')
    shutil.copyfile(OUT/Path(final).with_suffix('.pdf'),OUT/'slides.pdf')
    run(sys.executable,ROOT/'scripts/review_session03.py',OUT/'slides.pdf')
    print('PPTX・PDFを生成しました。全ページの表示点検は別途必要です。')
if __name__=='__main__':main()
