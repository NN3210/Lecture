// 数式変換後のPPTXの構造・配置・フォントを検証して成果物へ書き出す。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第03回_測量の座標/軸回転の式導入');
const skill=process.env.PRESENTATION_SKILL;
if(!skill||!process.env.RUNTIME_PYTHON)throw Error('実行環境を指定してください。');
process.env.RUNTIME_NODE_MODULES=process.env.ARTIFACT_MODULES;
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const requirements=JSON.parse(await fs.readFile(path.join(out,'build/requirements.json'),'utf8'));
const reports=path.join(root,'notes/axis_rotation');
await fs.mkdir(reports,{recursive:true});
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(out,'build/native-math.pptx'),finalPath:path.join(out,'軸回転の式の導出.pptx'),
 pythonExecutable:process.env.RUNTIME_PYTHON,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:requirements.explicitTotalSlideCount,
 requiredNativeTableOwnerSlides:[],fontPolicy:requirements.fontPolicy,
 layoutArgs:['--expected-slide-size-emu',requirements.expectedSlideSizeEmu,'--validate-heading-fit'],
 // 既存第3回と同様、OMMLの実表示はPowerPointの出力で検査する。
 verifyArtifactToolImport:false,
 receiptPath:path.join(reports,'final-validation.json'),
});
console.log(JSON.stringify({saved:path.basename(result.finalPath)}));
