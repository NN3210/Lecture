import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
process.on('uncaughtException',e=>{console.error(e.message);if(e.report)console.error(JSON.stringify(e.report));process.exit(1)});
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'materials/slides/第03回_測量の座標');
const skill=process.env.PRESENTATION_SKILL;
if(!skill||!process.env.RUNTIME_PYTHON||!process.env.ARTIFACT_MODULES)throw Error('READMEの環境変数を指定してください。');
process.env.RUNTIME_NODE_MODULES=process.env.ARTIFACT_MODULES;
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const req=JSON.parse(await fs.readFile(path.join(out,'build/requirements.json'),'utf8'));
const candidate=process.argv[2]||'native-math.pptx';
const final=process.argv[3]||'slides_visual.pptx';
// Artifact Toolの読込機能はOMMLのArgumentPropertiesに未対応。
// 構造・配置・フォントを検証し、数式の実表示はPowerPointのPDF出力で点検する。
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(out,'build',candidate),finalPath:path.join(out,final),pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:81,requiredNativeTableOwnerSlides:req.requiredNativeTableOwnerSlides,fontPolicy:req.fontPolicy,layoutArgs:['--expected-slide-size-emu',req.expectedSlideSizeEmu,...req.requiredNativeTableOwnerSlides.flatMap(n=>['--require-native-table-slide',String(n)])],verifyArtifactToolImport:false,receiptPath:path.join(root,'notes/session03_redesign',final+'.validation.json')});
await fs.copyFile(result.receiptPath,path.join(root,'notes/session03_redesign/final-validation.json'));
console.log(JSON.stringify({finalPath:result.finalPath,receiptPath:result.receiptPath}));
