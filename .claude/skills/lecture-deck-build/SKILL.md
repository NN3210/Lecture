---
name: lecture-deck-build
description: 指針 03（順序の抽象化と理由）と既存デッキの構成診断をもとに、講義スライドの枚順を決めて pptx を組み立て、PDF・PNG を書き出し、全枚を点検して直すまでの手順（lecture-design-pipeline の段階 4）。既存デッキがある回は dump_pptx_outline.py で全枚を抽出 → 改N_構成診断.md → 04_構成案.md（k1:NN / new:ID の表）＋ 04_新規枚.md → build_pptx.py で並べ替え・削除・非表示解除・新規枚の複製・ヘッダー書換・ページ番号振り直し → pptx_compress_images.py で 50 MB 以下に → pptx_export.ps1（PowerPoint COM）で PDF と PNG → Sonnet に全枚の PNG を点検させる。新規設計の回は Marp の slides.md → md2pptx.py → pptx_export.ps1。ユーザーが「構成案どおりに pptx を組み立てて」「改2 を作って」「スライドを並べ替えて」「橋渡しの枚を差し込んで」「ページ番号を振り直して」「PNG に書き出して全枚確認して」「50 MB を超えたので縮めて」「既存のスライドの重複と飛び石を診断して」と言ったとき、または lecture-design-pipeline の段階 4 に入ったときに使う。PowerPoint を手で触らず、Markdown の構成案だけ直せば何度でも作り直せる形にする。
---

# lecture-deck-build — 指針に従って枚順を決め、pptx を組み立てて点検する（段階 4）

## 目的

段階 3 の指針（`03_順序の抽象化と理由.md` §4 飛び石チェック表・§5 骨格）を、実際の pptx に落とす。
守ること：**pptx を手で編集しない**。枚順は `04_構成案.md`、新規枚は `04_新規枚.md` に書き、スクリプトで何度でも組み直す。手で直すと 2 回目の組み直しで消える。

第 3 回の実績：改 1（132 枚）→ 改 2（108 枚。使用 104・削除 28・新規 4・非表示から復帰 2・ヘッダー書換 3）。組み直し 3 回（新規枚の文字あふれ → 章ヘッダーの戻り → 旧版脚注の古い番号）。pptx 56 MB → 29 MB。

## 入力（読む順）

| 順 | ファイル | 何を読むか |
| --- | --- | --- |
| 1 | `<root>/00_設定.md` | DECK（既存デッキのパス。無ければ新規設計）、HEADER（ヘッダー接頭辞。例「測量学 第3回」）、PLAN |
| 2 | `<root>/03_順序の抽象化と理由.md` §4・§5 | 必ず踏む段階、守る順序対、骨格の章立て |
| 3 | [references/plan_formats.md](references/plan_formats.md) | 構成案・新規枚の書式と、build_pptx.py が読む規則 |
| 4 | [references/diagnosis_template.md](references/diagnosis_template.md) | 既存デッキの構成診断の雛形（経路 A のみ） |
| 5 | [references/review_prompts.md](references/review_prompts.md) | 点検の一行スクリプトと Sonnet の PNG 点検プロンプト、直す／直さないの判断例 |
| 6 | `materials/slides/_guidelines/slide_guidelines.md` | 新規設計（経路 B）のときの Marp の書き方・枚数配分 |

`$SK` はスキル群の置き場（`Surveying/` から見ると `../.claude/skills`）。cwd は `Surveying/`。Python は `-I` で起動する。

## 経路を選ぶ

- **A. 既存デッキがある**（DECK あり）：並べ替え・削除・差し込みで作る。本スキルの主経路。
- **B. 新規設計**（DECK なし）：`slides.md`（Marp）を 03 §5 の骨格どおりに書き、`scripts/md2pptx.py` → `pptx_export.ps1`。B の後に改訂するときは A に移る。

## 手順 A（既存デッキ）

### A1. 全枚を抽出する（5 分）

```
python -I $SK/lecture-deck-build/scripts/dump_pptx_outline.py "<DECK>.pptx" > "<root>/改N_全NNN枚の内容抽出.md"
```

枚ごとに `[NNN] (HIDDEN) layout title` と本文テキスト・表・グループ内の文字が出る。画像だけの枚は本文が空になる。

### A2. 構成診断を書く（30〜60 分）

[references/diagnosis_template.md](references/diagnosis_template.md) を `<root>/改N_構成診断.md` に写して埋める：§1 全体像（枚数・非表示・世代の混在・画像だけの枚）、§2 同じ内容の重複、§3 順序の問題（飛び石になっている所。番号付きで）、§4 欠けている可能性のある段階（候補。段階 3 で確定）、§5 非表示枚の扱い。
段階 3 より前に書いてよい（診断は資料に依存しない）。段階 3 の §4 はこの診断を参照して「改 N の該当枚」「改 N での状態」を埋める。

### A3. 構成案と新規枚を書く（1〜2 時間）

`<root>/04_構成案.md`：§1 方針（03 §5 の骨格を 3〜5 行）、§2 枚順の表 `| 順 | 元 | 題 | 備考 |`（1 行 1 枚。`元` は `k1:NN` か `new:ID`。章を移した枚は備考に `header=測量学 第N回  /  03  \|  章名`）、§3 外した枚（枚番号と理由）。
`<root>/04_新規枚.md`：`## new:ID` の下に `- template / header / title / subtitle / card1..3 / bullets / takeaway / notes`。
書式の細則と文字数の上限（カード 1 枚 全角 40 字前後、帯 45 字）は [references/plan_formats.md](references/plan_formats.md)。
型紙の枚に `--list-shapes NN` を当てて部品名を確かめる（型紙が第 3 回の 3 枚カード型と違えば `--shape-map` で部品名を渡す）。

### A4. 組み立てる（1 分）

```
python -I $SK/lecture-deck-build/scripts/build_pptx.py "<DECK>.pptx" "<root>/04_構成案.md" "<scratch>/build.pptx" --new-spec "<root>/04_新規枚.md" --renumber --header-prefix "測量学 第N回"
```

出力例：`ページ番号書換 NNN 段落` → `元 132 枚 → 使用 104 枚、削除 28 枚、新規 4 枚、ヘッダー書換 3 枚、出力 108 枚`。
無い枚番号・同じ枚の二重使用・仕様の無い新規枚があれば止まる。`--header-prefix` を省くと構成案の `header=` の値から「/」の前を取る。

### A5. 50 MB 以下にする

```
python -I $SK/lecture-deck-build/scripts/pptx_compress_images.py "<scratch>/build.pptx" "materials/slides/第NN回_…/<名前>_改N+1.pptx"
```

既定（長辺 1600 px、300 KB 以上だけ、JPEG 品質 85）。`--quantize` は写真が荒れるので最後の手段。出力が 50 MB を超えるなら commit しない（AGENTS.md）。

### A6. PDF と PNG を書き出す

```
powershell -ExecutionPolicy Bypass -File $SK/lecture-deck-build/scripts/pptx_export.ps1 -Pptx "materials/slides/第NN回_…/<名前>_改N+1.pptx" -PngDir "<scratch>/png"
```

PDF は pptx と同じ場所に同名で出る。PNG は `スライド1.PNG`…（1280×720）。
注意：PowerPoint COM は Codex の計算機操作と同時に動かさない（画面を取り合う）。`-PngDir` は空のフォルダーを先に作らない（既にあると Export が失敗する例があった。無ければ作られる）。

### A7. 点検する（3 段）

1. **機械で**：`check_headers.py` で全枚のヘッダーとページ番号を抜き出し、非表示の残り・番号の不一致・章番号の戻りを見る（PNG を全部見るより速い）。
   ```
   python -I $SK/lecture-deck-build/scripts/check_headers.py "<pptx>" --header-prefix "測量学 第N回"
   ```
2. **統括が目で**：新規枚・ヘッダーを書き換えた枚・非表示から戻した枚・章の切れ目・最終枚の PNG を `Read` で見る（10 枚まで）。
3. **Sonnet が全枚**：[references/review_prompts.md](references/review_prompts.md) のプロンプトで Sonnet 1 体に全 PNG を「はみ出し・重なり・空枠・番号不一致・章の戻り」の観点で見させ、指摘を表で受け取る（108 枚で約 3.5 分）。

### A8. 直して組み直す（2〜3 回が普通）

指摘ごとに「直す／改 N 由来なので今回は直さない」を決め、直すものは **構成案か新規枚の Markdown を直して A4〜A7 をやり直す**。
よくある直し：新規枚のカードが枠からあふれる（文を短く）、章を移した枚のヘッダーが前の章のまま（備考に `header=`）、旧世代の枚の脚注番号が古いまま（`--renumber` が下端 15% の数字だけの枠も書き換える）。
直さないものは手順書か worklog に「改 N 由来、今回は直さない」と理由付きで残す。

### A9. 記録して commit

- 目視に使った PNG のうち新規枚・書き換え枚など数枚だけを `<root>/確認画像/` に置く（全枚は置かない。数十 MB になる）。
- `00_設定.md` の実行記録に、枚数の増減と組み直し回数を 1 行。
- commit：改 N+1 の pptx・pdf、`<root>/改N_*.md`、`04_*.md`、`確認画像/`、手順書。元デッキが 50 MB 超ならリポジトリに無いので、次回は改 N+1 を入力にして `k2:NN` で書く（`build_pptx.py` は接頭辞を問わない）。

## 手順 B（新規設計）

1. `slide_guidelines.md` の枚数配分（導入 4〜6・講義 48〜58・演習 3〜5・まとめ 3〜4）を、03 §5 の骨格の章に割り振る。章ごとに「定義 → 公式 → 例題 → 注意」の 3〜6 枚。
2. `materials/slides/第NN回_テーマ/slides.md` を Marp で書く。各枚の末尾に発表者ノート（HTML コメント）。03 §3 の工夫（問いで始める、数値例を最後まで通す、反例）を該当する章に入れる。
3. `python -I scripts/md2pptx.py slides.md -o slides.pptx` → `pptx_export.ps1` → A7 と同じ 3 段点検。
4. 次の改訂からは経路 A（この pptx が DECK）。

## 点検

```
[ ] 04_構成案 の行数 = 出力の枚数。元の枚が二重に使われていない
[ ] 03 §4.2 の順序対（90% 以上）を構成案の並びが満たしている
[ ] 03 §4.1 の「必ず踏む段階」に対応する枚が構成案にある（無ければ new:）
[ ] check_headers.py で非表示 0、ページ番号が位置と一致、章番号が戻らない
[ ] 新規枚の PNG を自分の目で見た（カード・帯のはみ出し無し）
[ ] Sonnet の指摘に「直す／直さない（理由）」を付けた
[ ] pptx が 50 MB 以下、確認画像は数枚だけ
[ ] 元デッキが手元に無くなっても改 N+1 から組み直せる（構成案と新規枚が commit されている）
```

## やらないこと

- PowerPoint で pptx を直接直す（次の組み直しで消える。改 N 側の枚の中身を直すときだけ元デッキを直し、記録する）。
- 全枚の PNG を統括が読む（文脈を食う。Sonnet に回す）。
- PowerPoint COM と Codex の計算機操作を同時に動かす。
- 確認画像を全枚 commit する。50 MB 超の pptx を commit する。
- 構成案に無い枚をスクリプトの外で足す。

## 参照

- 第 3 回の実例：`Surveying/notes/session03_kai2_20261021/`（`改1_構成診断.md`、`04_改2構成案.md`、`04_新規枚.md`、`手順書/手順書_04_改2組み立てと確認.md`、`確認画像/`）。元スクリプト `Surveying/scripts/kai2_build_pptx.py`。
- 新規設計の書き方：`Surveying/materials/slides/_guidelines/slide_guidelines.md`、`Surveying/scripts/md2pptx.py`。
- 前の段階：`lecture-order-guideline`。できた枚の「一本の筋」を講師向けに解説するなら `lecture-storyline-guide`。
