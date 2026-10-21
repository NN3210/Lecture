---
name: lecture-structure-extract
description: 集めた講義資料・動画（01_資料一覧.md のバッチ）を 1 件ずつ Codex CLI の計算機操作（Chrome・シェル・yt-dlp 字幕）で開き、「扱う話題の順番・導入のしかた・段階どうしのつなぎ（なぜ次に進むか）・分かりやすさの工夫・無い段階」を固定の雛形で codex/results/資料NNN.md に書かせる手順（lecture-design-pipeline の段階 2）。10 件 1 バッチを 1 本ずつ回し、字幕は yt-dlp（player_client=ios）で先取りし、途中停止は再実行バッチで埋め、メモリが少ないときは省メモリ版の雛形に切り替える。ユーザーが「各資料がどの順番で教えているか抽出して」「Codex に資料を読ませて構成を取り出して」「YouTube 講義の話題の順番を字幕から出して」「バッチを回して」「止まったバッチの続きを」と言ったとき、または lecture-design-pipeline の段階 2 に入ったときに使う。集計と抽象化は lecture-order-guideline が担当する。
---

# lecture-structure-extract — 各資料の「教える順番」を Codex の計算機操作で抽出する（段階 2）

## 目的

100 件の資料を 1 件ずつ開いて見出し・章立て・字幕を読み、同じ雛形で「順番」「導入」「つなぎ」「工夫」「無い段階」を書き出す。
後段で段階コードに置き換えて数えるので、**雛形の見出しが全件で同じ**であることが最も大事。中身の深さより形の揃い方を優先する。
外部サイトの閲覧と PDF・字幕の処理は Codex（gpt-6-astra、推論 high）に任せ、統括は「何件できたか」「NG の理由は何か」「tmp と git が汚れていないか」だけを見る。

第 3 回「座標系」の実績：110 件を 12 バッチ＋再実行 6 本で約 4 時間。実在 OK 92、NG 18（404、bot 確認、タイムアウト、保守中、別の PDF、字幕なし）。1 バッチ 10 件が 10〜19 分。

## 入力（読む順）

| 順 | ファイル | 何を読むか |
| --- | --- | --- |
| 1 | `<root>/00_設定.md` | SUBJECT・TOPIC・SUBTOPICS・ROOT |
| 2 | `<root>/codex/batches/batch_*.md` | lecture-source-search が作ったバッチ（動画 v、文書 p） |
| 3 | [references/codex_cli_notes.md](references/codex_cli_notes.md) | Codex CLI の起動方法、動かない設定、メモリ、NG の原因、再開手順。**実行前に必ず読む** |
| 4 | [references/batch_prompt_template.md](references/batch_prompt_template.md) / [batch_prompt_template_light.md](references/batch_prompt_template_light.md) | Codex への雛形（通常版・省メモリ版）。`init_codex_dir.py` が設定を埋めて `codex/` に置く |

`$SK` はスキル群の置き場（`Surveying/` から見ると `../.claude/skills`）。cwd は `Surveying/`。Python は `-I` で起動する。

## 手順

### 1. `codex/` を初期化する

```
python -I $SK/lecture-structure-extract/scripts/init_codex_dir.py --root notes/session05_traverse_20261101
```

`codex/.gitignore`（cache・tmp・標準出力ログを除外）と、`{{SUBJECT}}` `{{TOPIC}}` `{{SUBTOPICS}}` `{{ROOT}}` `{{WORKDIR}}` を埋めた雛形 2 本を `codex/` に置く。
置いた雛形を一度読み、テーマ固有の読み方（例：トラバースなら「計算例の数値の順番」も段階として拾う）を「種別ごとに中身を読む」の項に 1〜2 行足す。

### 2. 2 件で動作確認する

`codex/batches/batch_t01.md` に文書 1 件・動画 1 件の表を手で作り（形は他のバッチと同じ 6 列）、字幕を先取りしてから 1 本回す。

```
python -I $SK/lecture-structure-extract/scripts/prefetch_subs.py --root notes/session05_traverse_20261101 t01
python -I $SK/lecture-structure-extract/scripts/run_codex_batch.py --root notes/session05_traverse_20261101 t01
python -I $SK/lecture-structure-extract/scripts/check_results.py --root notes/session05_traverse_20261101
```

`results/資料NNN.md` が 2 つでき、雛形の見出しが揃っていれば本番へ。Chrome が開けない・シェルが失敗する場合は [references/codex_cli_notes.md](references/codex_cli_notes.md) §1 の起動オプションを確認する。

### 3. 字幕を先取りする

```
python -I $SK/lecture-structure-extract/scripts/prefetch_subs.py --root notes/session05_traverse_20261101 --all
```

動画バッチ（v*）の YouTube 全件について `codex/cache/資料NNN/` に `v.info.json`（題・長さ・チャプター・説明）と `v.<言語>.vtt`、再生リストなら `playlist.json` を置く。1 件 10〜40 秒。
Codex に yt-dlp を実行させると 1 件ごとに待ち時間が入り、429 も起きやすい。先取りしておけば Codex は読むだけになる。
**Codex のバッチと同時に走らせない**（メモリ）。

### 4. バッチを 1 本ずつ回す

```
python -I $SK/lecture-structure-extract/scripts/run_codex_batch.py --root notes/session05_traverse_20261101 v01 v02 v03
```

指定した順に 1 本ずつ実行する（内部で直列）。長いので `run_in_background` で起動し、終了通知を待つ。1 本 10〜20 分。
終わるたびに `--list` で件数を見る。`results` が件数に満たないバッチは次の手順で埋める。

```
python -I $SK/lecture-structure-extract/scripts/run_codex_batch.py --root notes/session05_traverse_20261101 --list
```

- 次のバッチに進む前に、Codex が開いたままの Chrome タブを手で閉じる（雛形に「閉じろ」と書いてあっても残ることがある）。
- 空きメモリが 2.5 GB を切ったら（タスクマネージャー、または `Get-CimInstance Win32_OperatingSystem | % FreePhysicalMemory`）、`--light` を付けて省メモリ版の雛形で回す。省メモリ版は curl → PyMuPDF／html.parser で読み、ブラウザーは最後の手段にする。Codex の常駐メモリが 1 GB 超から 0.3 GB 程度に下がる。
- 省メモリ版の弱点：JS 描画のページ（LMS、Google Slides、SlideShare）が NG になりやすい。その分は通常版で再実行する。

### 5. 止まった分を再実行バッチで埋める

```
python -I $SK/lecture-structure-extract/scripts/make_rerun_batch.py --root notes/session05_traverse_20261101 --status
python -I $SK/lecture-structure-extract/scripts/make_rerun_batch.py --root notes/session05_traverse_20261101 v03 v03r
python -I $SK/lecture-structure-extract/scripts/run_codex_batch.py --root notes/session05_traverse_20261101 v03r
```

結果ファイルがまだ無い No. だけを集めた `batch_v03r.md` を作って回す。何度でも（`v03r2` など）。
NG が正当な理由（404、bot 確認、字幕なし）なら、Codex は `実在確認：NG` の結果ファイルを書くので「欠け」には数えない。欠けは「タイムアウトやメモリ停止で結果ファイル自体が無い」件。

### 6. 結果の形を点検する

```
python -I $SK/lecture-structure-extract/scripts/check_results.py --root notes/session05_traverse_20261101
```

全結果について、雛形の見出し 5 つと「実在確認」行の有無、「扱う話題の順番」の段階数（5〜15 の範囲外を警告）、個人名らしき語の有無を報告する。見出しが欠ける結果は、その No. だけ再実行バッチで取り直す（Codex に「見出しを直せ」と頼むより速い）。
中身は統括は読まない。2〜3 件だけ開いて「順番が本当に資料の順か」を目で確かめる程度にとどめる。

### 7. 後始末と記録

- `codex/tmp/` が空か確認（Codex が消し忘れた PDF を消す）。
- `git status` で Codex がインデックスや worklog・AGENTS・README を触っていないか確認（雛形で禁止しているが、過去に自動 commit した前例がある）。触っていたら `git restore --staged` で戻す。
- `00_設定.md` の実行記録に、バッチごとの件数・所要・NG の理由を 1 行ずつ。
- commit するのは `codex/batches/`、`codex/prompts/`、`codex/results/`、`codex/logs/*_last_message.md`、`codex/logs/*_操作ログ.md`。cache・tmp・標準出力ログは `.gitignore` で除外済み。

## 点検

```
[ ] codex/.gitignore がある（cache/ tmp/ logs/*_stdout.log）
[ ] 雛形に git 禁止・worklog/AGENTS/README 禁止・書いてよい場所の 3 点が残っている
[ ] 動作確認バッチ（t01）で results が 2 件でき、見出しが雛形どおり
[ ] 字幕の先取りが v バッチ全件で done.txt を持つ（info-ng は NG 候補として控える）
[ ] バッチは 1 本ずつ。Codex・字幕先取り・PowerPoint COM を同時に走らせていない
[ ] --list で全バッチの results = 件数（NG を含む）
[ ] check_results.py で見出し欠けゼロ、段階数 5〜15 の外が数件以内
[ ] codex/tmp/ が空、git status に Codex の変更が無い、Chrome のタブが閉じている
```

## やらないこと

- 並列実行（Codex 2 本、Codex＋字幕先取り、Codex＋PowerPoint COM）。16 GB の PC では停止する。
- `-s workspace-write -c approval_policy=never` での起動（Chrome が拒否され、シェルも失敗した）。使うのは `--dangerously-bypass-approvals-and-sandbox`。
- Codex に検索させる・代替 URL を探させる（一覧にない資料が混ざる）。
- 動画を再生して待たせる（字幕・説明欄・チャプターで判断）。
- 結果ファイルを統括が手で直す（取り直す方が形が揃う）。
- 字幕キャッシュを commit する（著作物）。

## 参照

- Codex の起動・設定・メモリ・NG・再開：[references/codex_cli_notes.md](references/codex_cli_notes.md)
- 第 3 回の実例：`Surveying/notes/session03_kai2_20261021/codex/`（雛形 2 本、batches、results 110 件、logs）、`手順書/手順書_02_構成抽出_Codex計算機操作.md`（実行記録とメモリ停止の経緯）。
- 次の段階：`lecture-order-guideline`（Sonnet で圧縮 → 集計 → 抽象化）。
