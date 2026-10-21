あなたは測量学の講義設計を手伝う調査担当です。日本語で作業し、日本語で書いてください。
作業ディレクトリは Lecture/Surveying です。推論は丁寧に行ってください。

## 目的

測量学「座標系」の回に相当する世界の講義資料・動画について、「どの順番で何を教えているか」と「なぜその順番か」を資料ごとに抽出します。
対象は下の一覧（batch_p05）の 10 件です。

## 1 件ごとの手順（必ずこの順で）

1. **省メモリモード（この PC はメモリが少ない）**：まずシェルで `curl -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_<No>.<pdf|html> "<URL>"` で取得し、HTTP ステータスを確認する。取得できたら `python -I -c` で読む（PDF は PyMuPDF（fitz）、HTML は html.parser で h1〜h4 と本文テキストを抜く）。取得できない・本文が判別できない（JavaScript 描画など）ときだけブラウザー（`cua.createBrowserTab("chrome", url)`）で開き、読み終えたら必ずそのタブを閉じる。それでも開けない・内容が違う場合は「実在確認：NG」とし、理由を書いて次へ進む（代替 URL を探さない）。
2. 種別ごとに中身を読む。
   - スライド・PDF：curl で保存した PDF を PyMuPDF で読む。各ページの先頭 2〜3 行（見出し）を全ページ分、目次ページがあればその全文を取り、順番を把握する。保存した PDF は読み終えたら削除する。
   - YouTube 動画：まず先取り済みの `notes/session03_kai2_20261021/codex/cache/資料<No3>/` を見る（`v.info.json`＝title・duration・chapters・description、字幕 `v.<言語>.vtt`、再生リストなら `playlist.json`＝動画の並び）。これらを `python -I` で読み、字幕はタイムスタンプ付きで 1〜2 分ごとに「何の話をしているか」を拾って話題の順番を把握する（動画自体は再生しない）。cache が無い・空のときだけシェルで
     `yt-dlp --no-update --no-playlist --skip-download --ignore-no-formats-error --write-info-json --write-auto-sub --write-sub --sub-langs ".*-orig,ja,en" --sub-format "vtt/srv3/best" --extractor-args "youtube:player_client=ios" --sleep-subtitles 3 -o "notes/session03_kai2_20261021/codex/tmp/batch_p05_<No>" "<URL>"`
     を実行する（`player_client=ios` 以外だと字幕が HTTP 429 か PO Token 要求で落ちる。tv は自動字幕が一覧に出ない）。それも失敗したときだけブラウザーで動画ページを開き、タイトル・長さ・説明欄・チャプターを読む。字幕が無ければ説明欄・チャプター・コメント欄の目次で代用し、その旨を書く。読み終えたら tmp のファイルは削除する（cache は消さない）。
   - 解説ページ：curl で保存した HTML から見出し（h1〜h4）と本文の段落を抜く。図は alt 属性や図番号の文で代用する。本文が取れないときだけブラウザーで開き、読み終えたらタブを閉じる。
3. 下の雛形で `notes/session03_kai2_20261021/codex/results/資料NNN.md` に保存する（No3 は 3 桁ゼロ詰め）。
4. 操作ログ `notes/session03_kai2_20261021/codex/logs/batch_p05_操作ログ.md` に、1 件ごとに「開いた URL／使ったツール／実行したコマンド／起きた問題」を 3〜6 行で追記する。

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

## ブラウザー操作のコツ（ブラウザーはやむを得ないときだけ。前回の動作確認で分かったこと）

- in-app browser（`cua.createBrowserTab("iab", ...)`）は使えない。`cua.createBrowserTab("chrome", url)` で Chrome を使う。タブ作成時に変数未定義のエラーが出ても、タブは作られているので `cua.getTab()` で取得して続ける。
- アクセシビリティ要素を指定したスクロールは失敗することがある。画面座標（例 `scroll([1100, 600], "down", 3)`）でスクロールする。
- 見出しや本文の取得は `playwright.locator('h1, h2, h3, h4').evaluateAll(...)` や `document.body.innerText` の取得が速い。スクリーンショットを何枚も撮らない。
- PDF が Chrome のビューアーで開いた場合は、シェルで `curl -L` 保存 → PyMuPDF（`python -I`）の方が速い。
- 1 件に 5 分以上かけない。読めた範囲で書き、備考に「一部のみ」と記す。
- **1 件読み終えたら、その件で開いた Chrome のタブを必ず閉じる**（`cua.closeTab` 系の API があればそれを、無ければ playwright の `page.close()`）。タブを開いたままにすると PC のメモリが足りなくなり、バッチごと停止される。

## 禁止事項（必ず守る）

- **git 操作（add / commit / push / update-index / reset など）は一切行わない。** コミットは統括側がまとめて行う。
- **`notes/worklog.md` や `AGENTS.md`、`README.md` に書き込まない。** 書いてよいのは `notes/session03_kai2_20261021/codex/results/`、`codex/logs/`、`codex/tmp/` の下だけ。
- URL を推測して作らない。開けなければ NG と書く。
- 個人名は書かない。
- 一覧にない資料を追加しない。
- 動画を再生して待たない（字幕・説明欄・チャプターで判断する）。

## 対象一覧（batch_p05）

| No. | 種別 | タイトル | 言語 | URL | 備考 |
|---|---|---|---|---|---|
| 72 | 解説ページ | ガウス・クリューゲル図法（投影の基礎） | 日本語 | https://desktop.arcgis.com/ja/arcmap/latest/map/projections/gauss-kruger.htm | 未確認。ソフトのヘルプだが投影の説明部分は有用 |
| 87 | スライド | 04 Geoinfo Geokomm 2025 Landeskoordinaten | ドイツ語 | https://gwb.schule.at/pluginfile.php/366833/mod_resource/content/2/04-28102025_Geoinfo_Geokomm_2025_Landeskoordinaten.pdf | 未確認（WebFetch が接続拒否） |
| 88 | スライド | 01b Bezugssysteme（Bezugssysteme und Kartenabbildungen） | ドイツ語 | https://wuecampus.uni-wuerzburg.de/moodle/pluginfile.php/2868527/mod_resource/content/1/01b-bezugssysteme.pdf | 未確認（WebFetch が接続拒否） |
| 89 | 教科書章 | Mathematische Geodäsie（Wikibooks） | ドイツ語 | https://de.wikibooks.org/wiki/Mathematische_Geod%C3%A4sie | 確認（見出しのみ。本文は未精査） |
| 90 | スライド | Sistemas de referencia 0809 | スペイン語 | https://moodle.upm.es/en-abierto/pluginfile.php/734/mod_label/intro/Sistemas_de_referencia0809.pdf | 未確認（WebFetch が 404） |
| 93 | 講義ノート | Cours de Topographie et Topométrie Générale, Chapitre 1 Notions géodésiques de base | フランス語 | https://ift-ik-84.webself.net/file/si123755/download/coursdetopographieettopometriegenerale-fi1917013.pdf | 確認（目次を取得） |
| 94 | スライド | Lambert 93（RGF93 と Lambert-93） | フランス語 | https://piles.cerema.fr/IMG/pdf/Lambert_93_cle7498e8.pdf | 未確認（WebFetch が 403） |
| 97 | 講義ノート | Topografia I: Conceitos Gerais e Planimetria（版 2023年3月） | ポルトガル語 | https://petecv.ufsc.br/wp-content/uploads/2023/04/Apostila-Topografia-I-Versao-Marco_2023.pdf | 確認（目次を取得） |
| 100 | 講義ノート | Silabus Sistem Koordinat dan Proyeksi Peta（CM235102 ほか） | インドネシア語 | https://www.its.ac.id/tgeomatika/wp-content/uploads/sites/32/2021/03/Sistem-Koordinat-dan-Proyeksi-Peta.pdf | 確認。シラバス（講義内容の一覧）で、スライド本体ではない |
| 102 | 講義ノート | Лекция 3. Системы координат, используемые в геодезии | ロシア語 | https://lu.belstu.by/wp-content/uchebnaya-rabota/dnevnoe/lh/inzhenernaya-geodeziya/lekciya-3-ing-geod.pdf | 確認（本文を取得） |

## 最後の返答

処理した件数、実在確認 OK の件数、NG の件数を 3 行で書いてください。
