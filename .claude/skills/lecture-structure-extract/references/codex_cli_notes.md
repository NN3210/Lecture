# Codex CLI で計算機操作をさせるときの覚え書き（Windows、この PC、2026-10 時点）

## 1. 起動方法

`run_codex_batch.py` が使うコマンド（Codex CLI 0.162.1、`~/.codex/config.toml` にモデルと推論強度を設定済み）：

```
codex exec -m gpt-6-astra -c model_reasoning_effort=high --dangerously-bypass-approvals-and-sandbox -C . --skip-git-repo-check -o <last_message.md> -
```

プロンプトは標準入力から渡す（`-`）。`-o` は最後の返答をファイルに書く。

| 起動の選択肢 | 結果 |
| --- | --- |
| `-s workspace-write -c approval_policy=never` | **動かない**。Chrome のタブ作成が拒否され、シェルも失敗する |
| `--dangerously-bypass-approvals-and-sandbox` | 動く。ただし Codex はリポジトリの `AGENTS.md` を読んで、頼んでいない commit・push をしたことがある（第 3 回で 1 回）。雛形で git 操作を禁止する |
| MCP サーバー `codex`（Claude Code から） | 接続失敗（CONNECTION_CLOSED）。CLI だけ使う |

Codex 側の道具の名前：ブラウザーは `cua.createBrowserTab("chrome", url)`（in-app browser `"iab"` は使えない）、ページ操作は playwright、シェルは通常の PowerShell／bash。タブ作成時に変数未定義のエラーが出てもタブは作られているので `cua.getTab()` で続ける。アクセシビリティ要素指定のスクロールは失敗することがあるので画面座標でスクロールする。

## 2. メモリ（最重要）

- この PC は 16 GB。常駐アプリ（Chrome 約 2 GB、Notion 1.6、Claude Code 0.9、Cursor 0.9 など）で 9 GB 前後が埋まる。
- Codex 通常版 1 本で 1 GB 超、Chrome のタブが増えるとさらに増える。**2 本同時＋字幕先取りで空き 2 GB を切り、バッチごと停止した**（第 3 回 00:30）。
- 対策：1 本ずつ。空きが 2.5 GB を切ったら `--light`（省メモリ版雛形。Codex の常駐 0.25〜0.36 GB）。Codex が残した Chrome タブはバッチの合間に手で閉じる。
- PowerPoint COM の書き出し（lecture-deck-build）は Codex と同時にしない。

空きメモリの確認（PowerShell）：

```
Get-CimInstance Win32_OperatingSystem | Select-Object @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}}
```

## 3. 所要時間の目安

| 種別 | 1 件 | 10 件バッチ |
| --- | --- | --- |
| 動画（字幕先取り済み） | 1〜2 分 | 10〜15 分 |
| PDF・解説ページ（通常版） | 1〜2 分 | 10〜19 分 |
| 省メモリ版 | 同程度（JS 描画ページは早く NG になる） | 10〜15 分 |

`run_codex_batch.py` のタイムアウトは 90 分。超えたら kill して欠けを再実行バッチで埋める。

## 4. NG の原因（第 3 回の 18 件）

| 原因 | 件数の目安 | 扱い |
| --- | --- | --- |
| 404・ページ消滅 | 多 | NG のまま |
| 403・bot 確認（Cloudflare など） | 中 | 通常版で再実行しても同じことが多い。NG |
| タイムアウト（巨大 PDF、遅いサーバー） | 中 | 再実行バッチで 1 回だけ試す |
| サイト保守中 | 少 | 翌日に再実行 |
| URL の先が別の PDF（収集時の取り違え） | 少 | NG（一覧を直さない。番号を保つ） |
| 字幕なし（説明欄・チャプターも無い） | 中 | NG。`prefetch_subs.py` の `done.txt` が `subs=none` の件は事前に分かる |
| 省メモリ版で JS 描画ページ | 中 | 通常版で再実行 |

## 5. 再開手順（止まったとき）

1. `make_rerun_batch.py --root <root> --status` で欠けを見る。
2. 動画の欠けがあれば `prefetch_subs.py --root <root> <id>` で先取りを済ませる（done.txt がある件は飛ばす）。
3. `make_rerun_batch.py --root <root> <id> <id>r` で再実行バッチを作る。
4. 空きメモリを見て、`run_codex_batch.py --root <root> [--light] <id>r` を 1 本。
5. 終わったら `codex/tmp/` を空にし、`git status` で Codex の変更が無いことを確認する。

## 6. yt-dlp（字幕）

- `--extractor-args "youtube:player_client=ios"` が必須。android_vr は 429、web/mweb は PO Token 要求、tv は自動字幕が一覧に出ない。
- 2 段階（`-J` で情報 → 言語を選んで字幕）。言語は `<原語>-orig` の自動字幕を優先し、手動字幕は ja・en を最大 2 つ。
- 1 件ごとに 2 秒、字幕取得に `--sleep-subtitles 2`。連続で 50 件以上取ると 429 が出ることがある。出たら 10 分待つ。
- キャッシュは `codex/cache/資料NNN/`。著作物なので commit しない。

## 7. 雛形の禁止事項（消さないこと）

- git 操作（add / commit / push / update-index / reset）をしない。
- `notes/worklog.md`、`AGENTS.md`、`README.md` に書かない。書いてよいのは `codex/results/`、`codex/logs/`、`codex/tmp/` だけ。
- URL を推測しない。一覧にない資料を足さない。個人名を書かない。動画を再生して待たない。
- 1 件読み終えたら Chrome のタブを閉じる。1 件に 5 分以上かけない。
