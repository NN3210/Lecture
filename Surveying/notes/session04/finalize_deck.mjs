import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const home=process.env.USERPROFILE||os.homedir();
process.env.RUNTIME_NODE_MODULES??=path.join(home,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const skill=process.env.PRESENTATION_SKILL_DIR||path.join(home,'.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11348/skills/presentations');
const python=process.env.RUNTIME_PYTHON||execFileSync('python',['-c','import sys;print(sys.executable)'],{encoding:'utf8'}).trim();
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const folder=path.join(root,'materials/slides/第04回_角測量');
const candidatePath=path.join(folder,'build/revised/第04回_角測量.pptx');
const finalPath=path.join(folder,'slides.pptx');
const sources=[];for(let i=1;i<=3;i++)sources.push(...JSON.parse(await fs.readFile(path.join(root,`notes/session04/slides_part${i}.json`),'utf8')));
const tableOwners=sources.filter(d=>d.headers?.length).map(d=>d.id);
const receiptPath=path.join(root,'notes/session04/final_validation.json');
const result=await finalizePresentation({
 workspaceDir:root,candidatePath,finalPath,pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:tableOwners,
 requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Yu Gothic']},
 verifyArtifactToolImport:true,receiptPath,
});
console.log(JSON.stringify(result));
