---
name: lecture-order-guideline
description: Codex が資料ごとに書いた構成抽出（codex/results/資料NNN.md）を、段階コード表で機械的に比べられる形に圧縮・連結・集計し、「どの順番で教えるか」「なぜその順番か」「なぜ分かりやすいか」「欠けると詰まる段階（飛び石チェック表）」の 4 問に答える指針 03_順序の抽象化と理由.md を書く手順（lecture-design-pipeline の段階 3）。Sonnet にバッチ圧縮とつなぎ理由の整理をさせ、stage_stats.py で出現率・平均位置・順序対の勝率・隣接ペアを数え、統括が「資料が明示した理由」と「統括の推測」を分けて書く。ユーザーが「集めた資料から教える順番の指針を作って」「どの順番が多数派か数えて」「なぜその順番なのか整理して」「骨格の型を分けて」「飛び石チェック表を作って」「段階コードを決めて」と言ったとき、または lecture-design-pipeline の段階 3 に入ったときに使う。スライドの組み立ては lecture-deck-build が担当する。
---

# lecture-order-guideline — 資料横断で「順番・理由・工夫・飛び石」を抽象化し、設計指針を書く（段階 3）

## 目的

段階 2 の結果（1 資料 1 ファイル、自由文の順番）を、**段階コード列**（例 `WHY→COORD→SHAPE→…→EX`）に置き換えて数えられる形にし、数の裏付けのある指針を 1 本書く。
指針は後段（lecture-deck-build）が枚の順番と欠けを決める唯一の根拠になるので、「資料が明示した理由」と「統括の推測」を混ぜない。混ぜると、後で「なぜこの順か」を学生や同僚に説明できなくなる。

第 3 回「座標系」の実績：OK 92 件（段階列あり 91 件）→ 骨格 4 型（通し型 27・測地高さ型 26・投影型 23・計算型 14）、順序対 100% が 6 組、飛び石 4 枚を新規追加。Sonnet の圧縮で 1 件（No.021）が落ちたのを検算で発見した。

## 入力（読む順）

| 順 | ファイル | 何を読むか |
| --- | --- | --- |
| 1 | `<root>/00_設定.md` | CODES（段階コード表のパス）、DECK（既存デッキの有無）、PLAN |
| 2 | [references/stage_codes_座標系.md](references/stage_codes_座標系.md) / [stage_codes_トラバース測量.md](references/stage_codes_トラバース測量.md) | 段階コード表。テーマに合う表を選び、無ければ座標系の表を手本に作る |
| 3 | [references/sonnet_prompts.md](references/sonnet_prompts.md) | Sonnet に渡す 2 種のプロンプト（バッチ圧縮、つなぎ・工夫の整理） |
| 4 | [references/abstraction_doc_template.md](references/abstraction_doc_template.md) | 指針 03 の雛形と、各節に何をどう書くか |
| 5 | `<root>/codex/results/資料NNN.md` | 読まない（Sonnet に読ませる）。統括は 2〜3 件だけ目を通す |

以下の `$SK` はこのスキル群の置き場（リポジトリでは `Lecture/.claude/skills`。`Surveying/` から見ると `../.claude/skills`）。

## 手順

### 1. 段階コード表を決める（15〜30 分）

- テーマに合う `references/stage_codes_<テーマ>.md` を選ぶ。無ければ座標系の表を手本に、**12〜20 個**のコードで作る（少ないと順番の違いが消え、多いと 1 件あたりの出現が薄くなり集計が効かない）。
- 作り方：授業計画の到達目標の項目を 1 コードずつ割り当て、その前後に「WHY（なぜ要るか）」「EX（演習・まとめ）」「OTHER」を必ず置く。隣接範囲（ADJACENT）の話題にも 1〜2 個置く（資料にはよく出るので、OTHER に溶けると順序が見えなくなる）。
- 段階 2 の結果を 10 件ほど開いて、どのコードにも入らない話題が続くなら、コードを足す。**コード表は圧縮を始めたら変えない**（変えると全バッチやり直し）。
- `00_設定.md` の CODES にパスを書く。

### 2. 統合指示書を作る

```
python -I $SK/lecture-order-guideline/scripts/make_merge_instructions.py --root notes/session05_traverse_20261101 --codes $SK/lecture-order-guideline/references/stage_codes_トラバース測量.md
```

`<root>/codex/merge_instructions.md` ができる。例の行（座標系のもの）はそのままでよい。形を示すだけ。

### 3. Sonnet でバッチごとに圧縮する（1 バッチ 3〜5 分）

[references/sonnet_prompts.md](references/sonnet_prompts.md) §1 のプロンプトで、バッチごとに Sonnet サブエージェント（`model: sonnet`）を 1 体ずつ起動する。独立なので **同じメッセージで 3〜4 体まとめて**起動してよい（Codex と違いメモリは使わない）。
出力は `<root>/codex/merged/<batch_id>.md`。返答は 2 行だけにさせ、本文を統括の文脈に戻さない（100 件分を読むと統括の文脈が尽きる）。
再実行バッチ（v03r など）は元バッチの欠けを埋めたものなので、別名で圧縮してよい（連結時に No. で合流する）。

### 4. 連結して検算する

```
python -I $SK/lecture-order-guideline/scripts/concat_merged.py --root notes/session05_traverse_20261101 --codes $SK/lecture-order-guideline/references/stage_codes_トラバース測量.md
```

`<root>/02_各資料の構成抽出.md` ができる（一覧表を先頭に集約、各資料の節を No. 順に）。
標準出力の「results にあるが一覧に無い No.」が空であることを確認する。空でなければ、その No. を含むバッチを Sonnet にやり直させる（第 3 回では 10 件バッチのうち 1 件を Sonnet が落とした）。

### 5. 数える

```
python -I $SK/lecture-order-guideline/scripts/stage_stats.py --root notes/session05_traverse_20261101 --codes $SK/lecture-order-guideline/references/stage_codes_トラバース測量.md
```

`<root>/codex/stage_stats.md` に 6 節：①コードごとの出現率と平均位置（0＝最初、1＝最後）、②最初・2 番目の段階と導入型、③隣接ペア A→B 上位 40、④同じ資料に両方出たときどちらが先か（件数 8 以上）、⑤種別・言語、⑥各資料の段階列。
読み方：①の平均位置の並びが「多数派の順番」、④の 90% 超が「守るべき順序対」、③の上位が「続けて話される一組」（間に別の話題を挟まない）。

### 6. つなぎの理由と工夫を Sonnet に整理させる

[references/sonnet_prompts.md](references/sonnet_prompts.md) §2 のプロンプトで Sonnet を 1 体。`02_各資料の構成抽出.md` の「つなぎ」「工夫」「無い段階」「導入」の行を読ませ、`<root>/codex/つなぎ理由と工夫の整理.md` に段階ペア別の明示理由・工夫の種類別対応表・無い段階の集計・導入型を書かせる。
Sonnet には「資料に書かれた範囲だけ。書かれていない理由は補わない」と必ず書く。ここで創作が混ざると §2.1 の「明示した理由」が汚れる。

### 7. 統括が指針 03 を書く（1〜2 時間）

[references/abstraction_doc_template.md](references/abstraction_doc_template.md) を `<root>/03_順序の抽象化と理由.md` に写し、stage_stats と整理ファイルを見ながら 5 節を埋める。

1. **どの順番か**：平均位置の表 → 骨格の型分け（扱う話題の有無で 2〜4 型。型ごとに件数・典型段階列・典型例 5 件）→ 順序対（90% 以上）→ 隣接ペア → 導入型。
2. **なぜその順番か**：2.1 資料が明示した理由（段階ペア別、資料番号付き）、2.2 明示されていない順序（並べているだけの資料）、2.3 統括の推測（集計の数字から読んだもの。**資料に無いと明記**）。
3. **なぜ分かりやすいか**：工夫の種類 × 効く段階 × 代表資料 × デッキでの対応。
4. **飛び石チェック表**：4.1 必ず踏む段階（出現率・最初に来る件数を根拠に）、4.2 守るべき順序対、4.3 既存デッキの重複・非表示の扱い（新規設計なら授業計画の項目との対応）。
5. **まとめ（骨格）**：章立てとコード列を 1 本の線で書く。これが lecture-deck-build の入力。

授業計画（PLAN）の到達目標と骨格を突き合わせ、到達目標に無い段階は「扱わない（隣接範囲）」と明記する。多数派に合わせることと、この回の 90 分に収めることは別の判断なので、落とした段階と理由も書く。

### 8. 記録

`00_設定.md` の実行記録に、圧縮の体数・落ちた件数・骨格の型数を 1 行。commit するのは `codex/merge_instructions.md`、`codex/merged/`、`02_…`、`codex/stage_stats.md`、`codex/つなぎ理由と工夫の整理.md`、`03_…`。

## 点検

```
[ ] 段階コードが 12〜20 個で、WHY・EX・OTHER を含み、到達目標の各項目に 1 つずつ対応している
[ ] 圧縮後、results の件数 = 02 の一覧行数（concat の「一覧に無い No.」が空）
[ ] 段階列の個数が「段階数」の列と一致している行が大半（Sonnet が省略していない）
[ ] 03 §2.1（明示）と §2.3（推測）が分かれており、§2.1 の各行に資料番号がある
[ ] 03 §4.1 の各段階に「根拠（出現率・順序）」が数字で書いてある
[ ] 03 §5 の骨格が、§1.3 の順序対（90% 以上）をすべて満たしている
[ ] 到達目標に無い段階を「扱わない」と明記している
```

## やらないこと

- 統括が results を全件読む（文脈が尽きる。Sonnet に読ませ、統括は数と整理だけ見る）。
- 圧縮の途中でコード表を変える。
- Sonnet に「理由を考えて」と頼む（創作が明示理由に混ざる）。推測は統括が §2.3 に書く。
- 多数派の順番をそのまま採用する。授業計画の 90 分と到達目標で切り、切った理由を書く。
- 資料の個人名を書く（Sonnet にも禁止させる。機関名に置き換える）。

## 参照

- 第 3 回の実例：`Surveying/notes/session03_kai2_20261021/`（`02_各資料の構成抽出.md`、`codex/stage_stats.md`、`codex/つなぎ理由と工夫の整理.md`、`03_順序の抽象化と理由.md`、`手順書/手順書_03_結果統合と順序の抽象化.md`）。
- 前の段階：`lecture-structure-extract`。次の段階：`lecture-deck-build`。
