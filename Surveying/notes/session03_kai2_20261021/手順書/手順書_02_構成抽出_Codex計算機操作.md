# 手順書 02：Codex（GPT-6 Astra、推論 High）の計算機操作で各資料の「教える順番」を抽出する

作成日：2026-10-21〜22。統括：Claude Code（Fable 5.1）。実作業：Codex CLI 0.162.1、モデル `gpt-6-astra`、`model_reasoning_effort=high`。
目的：[01_資料一覧.md](../01_資料一覧.md) の 110 件について、Codex にブラウザー（Chrome）とシェルを操作させ、資料ごとに「扱う話題の順番・導入・段階のつなぎ・分かりやすさの工夫・無い段階」を固定の雛形で `codex/results/資料NNN.md` に書かせる。

## 1. 事前の動作確認（2026-10-21、23:50 ごろ）

| 回 | 起動オプション | 結果 |
| --- | --- | --- |
| 1 | `-s workspace-write -c approval_policy=never` | in-app browser は `Browser is not available: iab`。Chrome は承認ゲートで拒否（外部サイトへのアクセスが自動で否認）。シェルは `helper_unknown_error: setup refresh had errors` で起動不可。ファイル書き込み（node_repl）だけ可能 |
| 2 | `--dangerously-bypass-approvals-and-sandbox` | Chrome でページ表示・スクロール・h1〜h3 取得に成功。シェル（PowerShell）も動作。**ただし Codex が `../AGENTS.md`（Lecture 全体の作業ルール）を読み、勝手に worklog へ追記し commit・push した**（コミット `aa6d2cc`） |

確認用プロンプト：[`codex/test_prompt.md`](../codex/test_prompt.md)。結果：[`codex/test_browser_result.md`](../codex/test_browser_result.md)。
`~/.codex/config.toml` には `model = "gpt-6-astra"`、`model_reasoning_effort = "high"` を設定済み（コマンド行でも同じ値を明示する）。Codex の MCP サーバー経由は接続できず、CLI のみ使う。

教訓として、本番プロンプトには次を入れた。
- **git 操作（add / commit / push / update-index / reset）を禁止**。コミットは統括側がまとめて行う。
- `notes/worklog.md`・`AGENTS.md`・`README.md` へ書かない。書いてよい場所を `codex/results/`、`codex/logs/`、`codex/tmp/` に限定。
- Chrome の操作のコツ（`cua.createBrowserTab("chrome", url)`、座標指定スクロール、`playwright.locator('h1, h2, h3, h4').evaluateAll(...)`）。

## 2. 入力の準備

1. `python scripts/kai2_merge_sources.py`（Surveying/ で実行）
   - `collect/` の 4 ファイルを統合し、URL 重複を除いて通し番号を振る → [`01_資料一覧.md`](../01_資料一覧.md)。
   - バッチを作る → `codex/batches/batch_v01.md`〜`v06`（動画 58 件、字幕は yt-dlp＝シェル中心）、`batch_p01.md`〜`p06`（スライド・講義ノート・解説ページ・教科書章 52 件、ブラウザー中心）。
   - 動画と文書を分けるのは、2 本を並列に走らせたとき Chrome の取り合いを減らすため。
2. プロンプト雛形 [`codex/batch_prompt_template.md`](../codex/batch_prompt_template.md) を確認する。プレースホルダーは `{{BATCH_NAME}}`、`{{N}}`、`{{BATCH_ID}}`、`{{No3}}`（→ `NNN`）、`{{BATCH_TABLE}}`。
3. 動画の字幕を先取りする（v01 の途中で分かった対策。2026-10-22 00:15）
   ```
   python -I scripts/kai2_prefetch_subs.py --all        # または v02 v03 ... と指定
   ```
   - `codex/cache/資料NNN/` に `v.info.json`（題名・長さ・章・説明欄）、`v.<言語>.vtt`（原語の自動字幕＋手動の ja/en）、再生リストなら `playlist.json`（動画の並び）を置く。`done.txt` があれば飛ばす（再実行可）。
   - 理由：Codex が叩いた yt-dlp（既定クライアント android_vr）は字幕 URL が **HTTP 429** で落ち、v01 の最初の 4 件は章題だけの抽出になった。web / mweb は PO Token 必須で字幕が捨てられる。tv は字幕 URL は通るが `--list-subs` に自動字幕が出ず、全件 `subs=none` になった。**`--extractor-args "youtube:player_client=ios"`** が確実（info と字幕の 2 段階で取る）。
   - 雛形も「cache を先に読む → 無ければ ios クライアントで yt-dlp → それも駄目ならブラウザー」に直した。
   - 字幕は著作物なので `codex/cache/` と `codex/tmp/` は `codex/.gitignore` で除外し commit しない。

## 3. 実行

```
python scripts/kai2_run_codex_batch.py v01        # 動画バッチを 1 本
python scripts/kai2_run_codex_batch.py p01        # 文書バッチを 1 本（別のシェルで並列可）
python scripts/kai2_run_codex_batch.py --list     # バッチごとの結果ファイル数
```

スクリプトがやること：
1. 雛形にバッチ表を差し込み `codex/prompts/batch_<id>_prompt.md` に保存（実際に渡したプロンプトの記録）。
2. 次を実行（標準入力でプロンプトを渡す）。
   ```
   codex exec -m gpt-6-astra -c model_reasoning_effort=high --dangerously-bypass-approvals-and-sandbox -C . --skip-git-repo-check -o codex/logs/batch_<id>_last_message.md -
   ```
   標準出力は `codex/logs/batch_<id>_stdout.log`。制限時間 90 分。
3. 終了後、親を失った `codex*.exe`（code-mode-host、computer-use-swift など）だけを止める（並列中の別バッチは止めない）。
4. バッチ内の No. ごとに `codex/results/資料NNN.md` の有無を数えて表示する。

Codex 側の 1 件あたりの操作（雛形で指示）：
- 文書：Chrome で開く → 見出しを読む → 長い PDF は `curl -L` で `codex/tmp/` に保存し PyMuPDF（`python -I`）で見出し抽出 → 読了後に削除。
- 動画：`codex/cache/資料NNN/` の info.json（題名・長さ・章）と VTT 字幕を `python -I` で読み、時刻付きで話題の流れを拾う。cache が無いときだけ `yt-dlp ... --extractor-args "youtube:player_client=ios"`、それも失敗したときだけ Chrome で動画ページを開く。動画は再生しない。
- 1 件ごとに結果ファイルを書き、`codex/logs/batch_<id>_操作ログ.md` に「開いた URL／使ったツール／コマンド／問題」を追記。

## 4. 並列と資源

- 当初は 2 本まで（動画 1 本＋文書 1 本）としたが、00:30 にメモリ不足で停止されたため **以後は 1 本ずつ**。PowerPoint COM の書き出しや字幕先取りとも同時に走らせない（メモリ 16 GB、常駐アプリで 9 GB 超）。
- Chrome は Codex がユーザーの Chrome を使う（`browser_use_external`）。実行中は Chrome を手で触らない。

## 5. 結果の確認と後始末

1. `python scripts/kai2_run_codex_batch.py --list` で欠けを確認し、欠けた No. だけを含む小バッチを作って再実行する（`codex/batches/batch_r01.md` のように手で作ってよい）。
2. `codex/tmp/` が空であること、`git status` に Codex の index 変更や worklog 追記が無いことを確認する。
3. 結果の統合は手順書 03（Sonnet サブエージェントで `02_各資料の構成抽出.md` に集約）。

## 6. 実行記録

| バッチ | 開始〜終了 | 結果 | 備考 |
| --- | --- | --- | --- |
| p01 | 10-21 23:58〜10-22 00:17 | 10/10（NG 3：No.1〜3 の PSU GEOG 862 は講座ルートごと 404） | 約 19 分 |
| v01 | 10-21 23:58〜10-22 00:16 | 10/10 だが No.29〜37 は字幕 429 で章題のみ → `logs/v01_first_run/` に退避し v01r で再実行 | 字幕先取りの対策を決めた回 |
| p02 | 00:17〜00:30（中断） | 8/10（No.19・20 未着手）。No.11 は MIT 12.215 の回違いで NG → 一覧を Lecture 2 の PDF に差し替え済み（r02 で再実行） | **Claude Code がメモリ不足を理由に停止**（下記） |
| v02 | 00:23〜00:30（中断） | 5/10（No.43〜47 未着手） | 同上 |
| 字幕先取り | 00:15〜00:30（中断） | cache 52 件まで（v02〜v05 の途中） | 同上。`done.txt` があるものは再実行時に飛ばす |
| 字幕先取り（再開） | 01:20 ごろ | cache 55 件で完了（044・045・056・108・109・110 は字幕なし → 説明欄・章で代用） | Codex を止めたまま単独で実行 |
| p02r | 02:35〜02:43 | 2/2（OK 2） | **以後すべて `--light`（省メモリモード）**。Codex のメモリは 0.25〜0.36 GB |
| p03 | 02:44〜02:54 | 10/10（NG 2：No.25 は 403、No.28 はボット検証画面） | 10 件で約 10 分。通常モードより速い |
| p04 | 02:59〜03:09 | 10/10（NG 6：No.65〜67・69 は接続タイムアウト、No.70 は別の書名の PDF、No.71 は 503 メンテナンス） | |
| p05 | 03:10〜03:24 | 10/10（NG 4：No.87・88 タイムアウト、No.90 は Moodle 404、No.94 は保守中 HTML） | |
| p06 | 03:25〜03:28 | 2/2（NG 1：No.107 はホスト名が解決できない） | |
| v02r | 03:28〜03:35 | 5/5（OK 5） | 動画は cache の字幕を読むだけなので速い |
| v03 | 03:36〜03:48 | 10/10（OK 10） | |
| v04 | 03:48〜03:58 | 10/10（OK 10。No.81 は字幕なしで順序を抽出できず、その旨を記録） | |
| v05 | 03:58〜04:11 | 10/10（OK 10） | |
| v06 | 04:11〜04:22 | 8/8（NG 2：No.109・110 は字幕・説明欄とも無し） | |
| v01r | 04:22〜04:31 | 9/9（OK 9） | 字幕 429 で章題だけだった No.29〜37 を cache から取り直した |
| r02 | 04:32〜04:42 | 10/10（OK 1：No.11 の MIT Lecture 2。NG 9：No.65〜67・69・71・87・88・94・107 は再試行でも同じ失敗） | 再試行バッチは `batch_r02.md` に理由付きで作成 |

最終：110 件すべてに `codex/results/資料NNN.md` がある。実在確認 OK 92 件、NG 18 件（PSU の 404、403・ボット検証、接続タイムアウト、メンテナンス中・404、ホスト名解決不可、書名違い、字幕・説明欄なし など。回違いの 1 件は差し替え済）。NG の内訳は `02_各資料の構成抽出.md` の一覧表を参照（件数もそちらが正）。

### メモリ不足による停止（2026-10-22 00:30）

- Codex 2 本（p02・v02）＋字幕先取りを同時に走らせていたところ、PC の空きメモリが約 2 GB まで減り、Claude Code が背景タスク 3 本をまとめて停止した。
  停止時の内訳：Chrome 約 2.1 GB（Codex が開いたタブを含む）、Notion 1.6 GB、Claude Code 0.9 GB、Cursor 0.9 GB、ChatGPT 0.4 GB など、Codex 以外の常駐アプリで 9 GB 超。
- Codex は 1 件ずつ結果を書くので、途中までの結果はそのまま使える。未着手分は `python -I scripts/kai2_make_rerun_batch.py p02 p02r` のように再実行バッチ（`batch_p02r.md` = No.19・20、`batch_v02r.md` = No.43〜47）を作った。
- 再開時の方針：**Codex は 1 本ずつ**（並列しない）、字幕先取りは Codex と同時に走らせない。Codex が開いた Chrome のタブは Codex 側で閉じないため、バッチの合間に手で閉じる。
- 残り：p02r・p03〜p06・v02r・v03〜v06・v01r・r02（順不同、1 本 13〜19 分）。

### 省メモリモード `--light`（2026-10-22 02:30 に追加）

- 停止後も常駐アプリで空きメモリが 0.4〜2.2 GB しかなく、Chrome を使う通常モード（Codex＋Chrome で 0.7〜1 GB）を安全に再開できなかった。
- そこで雛形の別版 [`codex/batch_prompt_template_light.md`](../codex/batch_prompt_template_light.md) を作り、`python -I scripts/kai2_run_codex_batch.py --light <id>` で使えるようにした。通常版との違いは 3 点。
  1. まず `curl -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o codex/tmp/<id>_<No>.<pdf|html>` で取得し、PDF は PyMuPDF、HTML は html.parser（h1〜h4＋段落）で読む。取得できない・JavaScript 描画のときだけ `cua.createBrowserTab("chrome", url)` で開き、読み終えたらタブを閉じる。
  2. スライド・PDF は全ページの先頭 2〜3 行と目次ページを取って順番を把握する。
  3. 解説ページは HTML の見出しと段落で読み、図は alt 属性や図番号の文で代用する。
- 動画バッチは元から cache（字幕先取り）中心なので、`--light` でも手順は変わらない（ブラウザーは最後の手段のまま）。
- 省メモリモードの欠点：JavaScript で描画されるページ（LMS、Google Slides、SlideShare 等）は本文が取れず NG になりやすい。NG の行は通常モードの再実行バッチ（r02 など）に回す。

## 7. 再開手順（メモリ停止後）

```
cd Surveying
python -I scripts/kai2_make_rerun_batch.py --status          # 欠けの確認
python -I scripts/kai2_prefetch_subs.py v05 v06 v01           # 字幕の残り（Codex を走らせる前に）
python -I scripts/kai2_run_codex_batch.py --light p02r         # 以後 1 本ずつ（空きメモリ 2.5 GB 未満なら --light）
python -I scripts/kai2_run_codex_batch.py --light p03   # ... p04 p05 p06 v02r v03 v04 v05 v06 v01r r02
```
