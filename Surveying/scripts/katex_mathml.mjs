// ブロック数式（TeX）を KaTeX で MathML にする。
// 使い方: node scripts/katex_mathml.mjs <入力 JSON> <出力 JSON>
//   入力: {"EQM00001": {"tex": "...", "display": true}, ...}
//   出力: 同じ構造に "mathml" を加えたもの（Office 数式への変換は omml_equations.py が行う）。
// KaTeX は npx のキャッシュ（Marp CLI が同梱するもの）から読む。別の場所なら KATEX_MODULES で指定する。
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const [, , inPath, outPath] = process.argv;
if (!inPath || !outPath) throw new Error('使い方: node katex_mathml.mjs <入力 JSON> <出力 JSON>');

let modules = process.env.KATEX_MODULES;
if (!modules) {
  const home = process.env.USERPROFILE || process.env.HOME;
  const base = path.join(home, 'AppData', 'Local', 'npm-cache', '_npx');
  if (fs.existsSync(base)) {
    for (const d of fs.readdirSync(base)) {
      const p = path.join(base, d, 'node_modules', 'katex', 'package.json');
      if (fs.existsSync(p)) { modules = path.join(base, d, 'node_modules'); break; }
    }
  }
}
if (!modules) throw new Error('KaTeX が見つかりません。KATEX_MODULES に node_modules の場所を指定してください。');
const katex = createRequire(path.join(modules, 'package.json'))('katex');

const input = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const out = {};
for (const [id, rec] of Object.entries(input)) {
  const html = katex.renderToString(rec.tex, {
    output: 'mathml', displayMode: !!rec.display, throwOnError: true, strict: false,
  });
  const mathml = html.match(/<math[\s\S]*<\/math>/)[0];
  out[id] = { ...rec, mathml };
}
fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
console.log(`KaTeX MathML: ${Object.keys(out).length} 式（katex ${katex.version}）`);
