"""補足スライドを生成し、編集可能な数式へ変換してPPTXとPDFを保存する。"""
from pathlib import Path
import os,subprocess,sys,re,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'materials/slides/第03回_測量の座標/軸回転の式導入'
BUILD=OUT/'build'

def main():
    env=os.environ.copy()
    deps=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
    modules=Path(env.get('ARTIFACT_MODULES',str(deps/'node/node_modules')))
    node=modules.parent/'bin/node.exe'
    env['ARTIFACT_MODULES']=str(modules)
    if 'MARP_MODULES' not in env:
        matches=list((Path.home()/'AppData/Local/npm-cache/_npx').glob('*/node_modules/katex/package.json'))
        if not matches:raise RuntimeError('MARP_MODULESを指定してください。')
        env['MARP_MODULES']=str(matches[0].parents[1])
    if 'PRESENTATION_SKILL' not in env:
        matches=list((Path.home()/'.codex/plugins/cache/openai-primary-runtime/presentations').glob('*/skills/presentations/SKILL.md'))
        env['PRESENTATION_SKILL']=str(max(matches,key=lambda p:p.stat().st_mtime).parent)
    env.setdefault('RUNTIME_PYTHON',str(deps/'python/python.exe'))
    env['PYTHONIOENCODING']='utf-8'
    def run(*args):subprocess.run([str(a) for a in args],cwd=ROOT,env=env,check=True)
    BUILD.mkdir(parents=True,exist_ok=True)
    run(node,ROOT/'scripts/build_axis_rotation.mjs')
    # 既存の数式変換ロジックをそのまま使用し、出力先だけ今回の補足に合わせる。
    patch=(ROOT/'scripts/patch_session03_math.py').read_text(encoding='utf-8')
    patch=patch.replace("ROOT=Path(__file__).resolve().parents[1]",'ROOT=Path(__file__).resolve().parents[5]')
    patch=patch.replace("OUT=ROOT/'materials/slides/第03回_測量の座標'","OUT=ROOT/'materials/slides/第03回_測量の座標/軸回転の式導入'")
    (BUILD/'patch_math.py').write_text(patch,encoding='utf-8')
    run(env['RUNTIME_PYTHON'],BUILD/'patch_math.py')
    # 再生成時も、検証対象の素案は残し、完成ファイルだけ再作成する。
    for name in ('軸回転の式の導出.pptx','軸回転の式の導出.pdf'):
        target=OUT/name
        if target.exists():target.unlink()
    run(node,ROOT/'scripts/finalize_axis_rotation.mjs')
    run('powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',ROOT/'scripts/export_axis_rotation.ps1',
        '-Pptx',OUT/'軸回転の式の導出.pptx')
    # 公開リポジトリ用に、検証記録の絶対パスを相対パスにする。
    for report in [*BUILD.glob('*.json'),*(ROOT/'notes/axis_rotation').glob('*.json')]:
        if report.name=='maths.json':continue
        raw=report.read_text(encoding='utf-8')
        for candidate,replacement in ((str(ROOT),'.'),(str(ROOT).replace('\\','/'),'.'),(str(Path.home()),'<user-profile>'),(str(Path.home()).replace('\\','/'),'<user-profile>')):
            raw=raw.replace(json.dumps(candidate)[1:-1],replacement)
        report.write_text(raw,encoding='utf-8')
    print('補足スライドのPPTX・PDF・全ページのPNGを保存しました。')

if __name__=='__main__':main()
