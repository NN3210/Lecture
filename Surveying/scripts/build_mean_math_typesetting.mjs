// 元PPTXを検査し、数式のMathMLと検証済みの別名PPTXを出力する。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const build=path.join(root,'notes/mean_math_typesetting');
const out=path.join(root,'materials/slides/第02回_測量の基礎と誤差論/補足_平均の誤差伝播_20261014');
const modules=process.env.ARTIFACT_MODULES,skill=process.env.PRESENTATION_SKILL;
const python=process.env.RUNTIME_PYTHON,katexPath=process.env.KATEX_MODULE;
if(!modules||!skill||!python||!katexPath)throw Error('実行環境のパスを環境変数で指定してください。');
process.env.RUNTIME_NODE_MODULES=modules;
const {default:katex}=await import(pathToFileURL(katexPath));
function run(args){const r=spawnSync(python,[path.join(root,'scripts/patch_mean_math_typesetting.py'),...args],{encoding:'utf8',env:{...process.env,PYTHONIOENCODING:'utf-8'}});if(r.status!==0)throw Error(r.stderr||r.stdout);console.log(r.stdout.trim());}
run(['--prepare']);
const source=path.join(out,'平均の誤差伝播_現場例追加_20261015.pptx');
// 全体を再出力すると式以外も変わるため、元ファイルは読み込みと検査に使う。
if(!process.argv.includes('--draft')){
 const {FileBlob,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
 const p=await PresentationFile.importPptx(await FileBlob.load(source));
 const inspected=await p.inspect({kind:'slide',maxChars:3000});
 await fs.writeFile(path.join(build,'source-inspection.ndjson'),inspected.ndjson);
}
const rules=JSON.parse(await fs.readFile(path.join(build,'rules.json'),'utf8'));
for(const r of rules){const s=katex.renderToString(r.tex,{output:'mathml',displayMode:false,throwOnError:true,strict:false});r.mathml=s.match(/<math[\s\S]*<\/math>/)[0];}
await fs.writeFile(path.join(build,'mathml.json'),JSON.stringify(rules,null,2));
run([]);
if(process.argv.includes('--draft'))process.exit(0);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const final=path.join(out,'平均の誤差伝播_現場例追加_数式整形_20261015.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'candidate.pptx'),finalPath:final,pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:22,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000'],
 // OMMLの実表示はPowerPointから出力して確認する。
 verifyArtifactToolImport:false,receiptPath:path.join(build,'final-validation.json')});
console.log('保存完了: '+path.basename(final));
