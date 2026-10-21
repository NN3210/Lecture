あなたは測量学の講義設計を手伝う調査担当です。日本語で作業し、日本語で書いてください。
作業ディレクトリは Lecture/Surveying です。推論は丁寧に行ってください。

## 目的

測量学「座標系」の回に相当する世界の講義資料・動画について、「どの順番で何を教えているか」と「なぜその順番か」を資料ごとに抽出します。
対象は下の一覧（batch_p01）の 10 件です。

## 1 件ごとの手順（必ずこの順で）

1. ブラウザーツール（browser_use / computer_use）で URL を開く。開けない・内容が違う場合は「実在確認：NG」とし、理由を書いて次へ進む（代替 URL を探さない）。
2. 種別ごとに中身を読む。
   - スライド・PDF：ブラウザーで最初の数ページを見て、目次・見出しがあればそれを読む。本文が長いときは、シェルで `curl -L -o notes/session03_kai2_20261021/codex/tmp/batch_p01_<No>.pdf "<URL>"` で保存し、`python -I -c` から PyMuPDF（fitz）で各ページの先頭行（見出し）を抜き出してもよい。保存した PDF は読み終えたら削除する。
   - YouTube 動画：まずシェルで
     `yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_p01_<No>" "<URL>"`
     を実行し、`.info.json`（title・duration・chapters・description）と VTT 字幕（`python -I` で VTT のタイムスタンプと文を読む）から話題の順番を把握する（動画自体は再生しない）。yt-dlp が失敗したときだけブラウザーで動画ページを開き、タイトル・長さ・説明欄・チャプターを読む。字幕が無ければ説明欄・チャプター・コメント欄の目次で代用し、その旨を書く。読み終えたら tmp のファイルは削除する。
   - 解説ページ：ブラウザーでページ全体をスクロールして見出しと図を読む。
3. 下の雛形で `notes/session03_kai2_20261021/codex/results/資料NNN.md` に保存する（No3 は 3 桁ゼロ詰め）。
4. 操作ログ `notes/session03_kai2_20261021/codex/logs/batch_p01_操作ログ.md` に、1 件ごとに「開いた URL／使ったツール／実行したコマンド／起きた問題」を 3〜6 行で追記する。

## 1 件ごとの出力雛形（この見出しをそのまま使う）

```
# 資料NNN：<実際のタイトル>

- 一覧の No.：<No>
- 実在確認：OK / NG（理由）
- 種別・言語・長さ：<スライド 40 枚 / 動画 23 分 など>
- 作成者（機関・チャンネル名。個人名は書かない）：
- 対象レベル：<学部 1〜2 年 / 資格試験 / 一般向け / 大学院 など>

## 扱う話題の順番

1. <話題>（<ページ or 時刻>）：<その話題で何を言っているか 1 行>
2. ...
（5〜15 段階。資料の中で出てくる順に。省略しない）

## 導入のしかた

- 最初に何から入るか（問い・身近な例・歴史・定義のどれか）を 2 行以内で。

## 段階どうしのつなぎ（なぜ次に進むか）

- <段階 A → 段階 B>：<資料が示している理由。無ければ「明示なし」>
（主要な 3〜6 本）

## 分かりやすさの工夫

- <図・比喩・数値例・実演・反例・クイズ などを 3〜6 点>

## この資料に無い段階・飛んでいる段階

- <気づいた点。無ければ「特になし」>
```

## ブラウザー操作のコツ（前回の動作確認で分かったこと）

- in-app browser（`cua.createBrowserTab("iab", ...)`）は使えない。`cua.createBrowserTab("chrome", url)` で Chrome を使う。タブ作成時に変数未定義のエラーが出ても、タブは作られているので `cua.getTab()` で取得して続ける。
- アクセシビリティ要素を指定したスクロールは失敗することがある。画面座標（例 `scroll([1100, 600], "down", 3)`）でスクロールする。
- 見出しや本文の取得は `playwright.locator('h1, h2, h3, h4').evaluateAll(...)` や `document.body.innerText` の取得が速い。スクリーンショットを何枚も撮らない。
- PDF が Chrome のビューアーで開いた場合は、シェルで `curl -L` 保存 → PyMuPDF（`python -I`）の方が速い。
- 1 件に 5 分以上かけない。読めた範囲で書き、備考に「一部のみ」と記す。

## 禁止事項（必ず守る）

- **git 操作（add / commit / push / update-index / reset など）は一切行わない。** コミットは統括側がまとめて行う。
- **`notes/worklog.md` や `AGENTS.md`、`README.md` に書き込まない。** 書いてよいのは `notes/session03_kai2_20261021/codex/results/`、`codex/logs/`、`codex/tmp/` の下だけ。
- URL を推測して作らない。開けなければ NG と書く。
- 個人名は書かない。
- 一覧にない資料を追加しない。
- 動画を再生して待たない（字幕・説明欄・チャプターで判断する）。

## 対象一覧（batch_p01）

| No. | 種別 | タイトル | 言語 | URL | 備考 |
|---|---|---|---|---|---|
| 1 | 講義ノート | Lesson 5: Geodetic Datums（GEOG 862） | 英語 | https://courses.ems.psu.edu/geog862/book/export/html/1669 | 未確認（検索要約。再取得は 404） |
| 2 | 講義ノート | Lesson 6: State Plane Coordinates and Heights（GEOG 862） | 英語 | https://courses.ems.psu.edu/geog862/print/l6.html | 未確認 |
| 3 | 講義ノート | GEOG 862 State Plane / UTM と縮尺係数の章 | 英語 | https://www.e-education.psu.edu/geog862/print/book/export/html/1817 | 未確認 |
| 4 | 解説ページ | 24. State Plane Coordinate System（Nature of Geographic Information） | 英語 | https://courses.ems.psu.edu/natureofgeoinfo/web/node/1698 | 未確認 |
| 5 | スライド | Lecture 4 - Datums and Geoid（Geodesy 2） | 英語 | https://feng.stafpu.bu.edu.eg/Surveying Engineering/4251/crs-18842/Files/Lecture 4 - Datums and Geoid.pdf | 確認済（PDF 取得、枚数のみ。URL に空白あり） |
| 6 | スライド | Lecture 9 - Height Systems（Geodesy 2） | 英語 | https://feng.stafpu.bu.edu.eg/Surveying Engineering/4251/crs-18842/Files/Lecture 9 - Height Systems.pdf | 未確認（検索要約） |
| 7 | スライド | Lecture 4 Height Systems for students | 英語 | https://feng.stafpu.bu.edu.eg/Surveying Engineering/4266/crs-18651/Files/Lecture 4 Height Systems for students.pdf | 未確認 |
| 8 | スライド | Surveying Engineering Lecture 3: Bearings | 英語 | https://feng.stafpu.bu.edu.eg/Surveying Engineering/897/crs-18550/Files/Surveying Lec 3 2021-2022.pdf | 確認済（PDF 取得。見出し抽出） |
| 9 | 講義ノート | Reference Systems for Surveying and Mapping（TRS 3-1） | 英語 | https://filelist.tudelft.nl/CiTG/Over%20faculteit/Afdelingen/Geoscience%20%26%20Remote%20sensing/Study/TRS_3-1.pdf | 未確認（PDF が画像のみで内容読めず） |
| 10 | 講義ノート | Lecture Notes Referenzsysteme（LNRefSyst） | 英語 | https://www.gis.uni-stuttgart.de/lehre/LectureNotes/LNRefSyst_180529.pdf | 確認済（PDF 取得、ページ数のみ） |

## 最後の返答

処理した件数、実在確認 OK の件数、NG の件数を 3 行で書いてください。
