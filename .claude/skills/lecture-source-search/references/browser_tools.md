# 検索・閲覧の道具の使い分け（Windows、この PC）

参考として渡された `chrome-cdp`（Chrome DevTools Protocol のラッパー。Chrome をリモートデバッグ付きで起動し、URL を開いて本文テキストやスクリーンショットを取る小さなスクリプト集）は macOS 向けで、Windows ではそのまま動かない。
この手順で必要な「開いて、見出しと本文を読む」は、下の道具でまかなえる。目的別に選ぶ。

| 目的 | 統括・サブエージェント（Claude Code） | Codex（計算機操作、lecture-structure-extract） | 備考 |
| --- | --- | --- | --- |
| 検索 | WebSearch（standard。薄いときだけ extended） | — | Codex に検索はさせない（一覧にない資料を足さない） |
| ページの実在と内容の確認 | WebFetch（1 URL 1 回） | シェルで `curl -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o <tmp> "<URL>"` | 403 は bot 確認の可能性。深追いしない |
| PDF の見出し抽出 | WebFetch（本文が取れることが多い） | `curl -L` で保存 → `python -I -c` から PyMuPDF（fitz）で各ページ先頭行 | ブラウザーの PDF ビューアーで読むより速い |
| HTML の見出し抽出 | WebFetch | `python -I -c` の html.parser で h1〜h4 と本文段落 | 図は alt 属性や図番号で代用 |
| JS 描画のページ（Google Slides、SlideShare、LMS） | claude-in-chrome：`navigate` → `get_page_text` / `read_page`（ToolSearch で先に読み込む） | `cua.createBrowserTab("chrome", url)` → playwright で `document.body.innerText` | 省メモリ版では最後の手段。読み終えたらタブを閉じる |
| YouTube の構成 | — | 先取りした `codex/cache/資料NNN/`（info.json・字幕 vtt）。無ければ `yt-dlp --extractor-args "youtube:player_client=ios"` | 動画は再生しない。`player_client=ios` 以外は 429 か PO Token 要求で落ちる |

## claude-in-chrome を使うとき

1. `ToolSearch` で `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp` を 1 回で読み込む。
2. `tabs_context_mcp` → `tabs_create_mcp` で新しいタブ → `navigate` → `get_page_text`。
3. 読み終えたら `tabs_close_mcp`。タブを残すとメモリを食う（16 GB の PC では Codex のバッチを止める原因になる）。

## 収集の段階での原則

- 検索と実在確認は WebSearch／WebFetch で済ませる。ブラウザーを使う判断は後段の Codex に任せる。
- 開けないものは「未確認」と書いて先へ進む。1 件に 2 分以上かけない。
