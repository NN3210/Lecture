---
name: lecture-source-search
description: 講義テーマ 1 つについて、世界中の大学・MOOC・公的機関の講義スライド・講義ノート・YouTube 講義動画を約 100 件、URL を推測せずに集めて 1 枚の Markdown 表（01_資料一覧.md）と Codex 用のバッチ一覧にする手順（lecture-design-pipeline の段階 1）。Sonnet サブエージェント 4 体（英語スライド／英語動画／日本語／他言語）を WebSearch・WebFetch で並列に走らせ、統括が merge_sources.py で統合する。ユーザーが「このテーマの講義資料を世界中から集めて」「YouTube の講義動画を探して一覧にして」「ネット検索して資料のリストを作って」「他の大学はどう教えているか調べて」「トラバース測量の資料収集」と言ったとき、または lecture-design-pipeline の段階 1 に入ったときに使う。収集だけで、各資料の中身の順番の抽出は lecture-structure-extract が担当する。
---

# lecture-source-search — 世界の講義資料・動画を集めて一覧にする（段階 1）

## 目的

後段（構成抽出）は 1 件 1〜2 分の計算機操作なので、ここで集める一覧の質が全体の時間を決める。
欲しいのは「実在し、テーマの講義であり、中の順番が読める」資料。URL を推測して作った行や、ログインが要る LMS のページは、後で NG になって Codex の時間を捨てる。
だから収集はサブエージェントに任せるが、「URL は検索結果からそのまま写す」「1 回は WebFetch で開く」「個人名を書かない」を共通指示で縛り、統括は件数と列の形だけを点検する。

第 3 回「座標系」では 4 体で約 40 分、110 件（重複 0）を集め、後段で 18 件が NG（404、bot 確認、JS 描画、字幕なし）だった。

## 入力（読む順）

| 順 | ファイル | 何を読むか |
| --- | --- | --- |
| 1 | `<root>/00_設定.md` | 科目・テーマ・副話題・隣接範囲・検索語・目標件数（lecture-design-pipeline が作る） |
| 2 | [references/collect_instructions_template.md](references/collect_instructions_template.md) | サブエージェント共通指示の雛形（`{{SUBJECT}}` などを埋めて `collect/_収集指示.md` にする） |
| 3 | [references/subagent_prompt.md](references/subagent_prompt.md) | 4 体の分担と、起動プロンプトの雛形 |
| 4 | [references/browser_tools.md](references/browser_tools.md) | 検索・閲覧の道具（WebSearch／WebFetch、claude-in-chrome、Codex の cua、curl）の使い分け。詰まったときだけ |

`$SK` はスキル群の置き場（`Surveying/` から見ると `../.claude/skills`）。cwd は `Surveying/`。Python は `-I` で起動する。

## 手順

### 1. 共通指示を作る

```
python -I $SK/lecture-source-search/scripts/init_collect_dir.py --root notes/session05_traverse_20261101
```

`00_設定.md` の SUBJECT・TOPIC・SUBTOPICS・ADJACENT を雛形に埋めて `collect/_収集指示.md` を書き、4 体分の起動プロンプトを `collect/_起動プロンプト.md` に書く。
作った共通指示を一度読み、科目固有の例（対象とする公的機関、対象外の例）をテーマに合わせて直す。測量なら国土地理院・NOAA/NGS・Ordnance Survey、別の科目なら別の機関。

### 2. サブエージェント 4 体を同時に起動する

`collect/_起動プロンプト.md` の 4 本を、**1 つのメッセージで 4 つの Agent 呼び出し**として送る（Sonnet、general-purpose）。順に起動すると 4 倍の時間がかかる。

| 体 | 担当 | 目標 | 出力 |
| --- | --- | --- | --- |
| A | 英語の大学・MOOC の講義スライド・講義ノート・教科書章 | 28 | `collect/資料収集_A_英語スライド.md` |
| B | 英語の YouTube 講義動画（再生リストは代表 1 本） | 28 | `collect/資料収集_B_英語動画.md` |
| C | 日本語の資料（大学・高専・公的機関・YouTube） | 28 | `collect/資料収集_C_日本語.md` |
| D | 英語・日本語以外（1 言語 6 件以内。独・西・仏・葡・尼・露・土・中・韓 など） | 24 | `collect/資料収集_D_他言語.md` |

サブエージェントには WebSearch（standard。薄いときだけ extended）と WebFetch を使わせる。返答は「件数」「未確認の件数」の 2 行だけ受け取る（一覧の本文を統括の文脈に戻さない）。
4 体とも 30〜45 分かかる。待つ間に lecture-structure-extract の準備（Codex の雛形、`codex/` の初期化）を進めてよい。

### 3. 出力を点検する

4 ファイルがそろったら、表の形と件数だけを機械的に見る。

```
python -I $SK/lecture-source-search/scripts/merge_sources.py --root notes/session05_traverse_20261101 --check
```

`--check` は統合せず、ファイルごとの行数・列数不足の行・「未確認」の数・URL の重複を出す。列が 10 に満たない行が多ければ、そのサブエージェントに「表の列を 10 列にそろえて書き直す」とだけ送り直す（SendMessage で続きを頼めば、検索し直しにならない）。

### 4. 統合してバッチを作る

```
python -I $SK/lecture-source-search/scripts/merge_sources.py --root notes/session05_traverse_20261101
```

- `01_資料一覧.md`：通し番号 No.（001〜）、元（A-12 など）、種別・言語の表記をそろえた全件表。先頭に種別・言語の集計。
- `codex/batches/batch_v01.md …`（動画）、`batch_p01.md …`（文書）：10 件ずつ。動画と文書を分けるのは、後段で動画は字幕の先取りが要り、処理時間も違うため。
- URL が同じ行は除く（正規化：`utm_*` と `feature=` を落とし、末尾の `/` と大文字小文字を無視）。

通し番号は以後ずっと使う（`codex/results/資料NNN.md`、集計、構成案の根拠）。統合後に行を足す・消すと番号がずれるので、足すときは末尾に追加し、消すときは消さずに後段で NG 扱いにする。

### 5. 記録する

`00_設定.md` の実行記録に 1 行（件数、所要、未確認の数）。`collect/` と `01_資料一覧.md`、`codex/batches/` を commit する。

## 点検

```
[ ] collect/_収集指示.md のテーマ・副話題が 00_設定.md と一致している
[ ] 4 ファイルとも 10 列の表で、No. が 1 から連番
[ ] URL が検索結果からの転記である（短縮 URL や「example.edu/...」のような作り物が無い）
[ ] 「未確認」が各ファイル 3 割以下。多ければ WebFetch で開かせ直す
[ ] 作成者欄に個人名が無い（機関名・チャンネル名・講義名）
[ ] merge_sources.py の出力：件数が目標の 8 割以上、重複が報告されている
[ ] 01_資料一覧.md の先頭の集計（種別・言語）が妥当（動画と文書が半々程度）
```

## 検索の道具

- 統括とサブエージェント（Claude Code）：WebSearch と WebFetch で足りる。ブラウザーは要らない。
- JS 描画のページ（Google Slides、SlideShare、LMS）を確認したいとき：claude-in-chrome の `navigate` → `get_page_text`。ただし収集の段階では深追いせず、「未確認」と書いて次へ進む（後段の Codex が Chrome で開く）。
- 例として渡された chrome-cdp（macOS 向け Chrome DevTools Protocol ラッパー）は Windows では動かない。相当する道具は [references/browser_tools.md](references/browser_tools.md)。

## やらないこと

- URL を推測して作らない・作らせない（共通指示に明記。NG の最大の原因）。
- サブエージェントに「中身の順番」まで書かせすぎない。「扱う話題」欄は粗くてよく、順番の抽出は次の段階が固定の雛形でやる。
- 一覧の本文を統括の文脈に読み込まない（点検はスクリプトの数字で）。
- 個人名・連絡先を書かない（公開リポジトリ）。
- 統合後に通し番号を振り直さない。

## 参照

- 第 3 回の実例：`Surveying/notes/session03_kai2_20261021/collect/`（共通指示と 4 ファイル）、`01_資料一覧.md`、`手順書/手順書_01_資料収集.md`。
- 次の段階：`lecture-structure-extract`（バッチを Codex で処理）。
