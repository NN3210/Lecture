# batch_p04 操作ログ

## 資料062（2026-10-22）
- 開いたURL：https://www.gsi.go.jp/LAW/heimencho.html
- 使用ツール：PowerShell、curl.exe、Python標準html.parser。ブラウザー不使用。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_62.html "https://www.gsi.go.jp/LAW/heimencho.html"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_62.html`。h1〜h4、本文、図altを抽出。
- 問題：初回の端末出力が文字化けしたためPython標準出力をUTF-8に設定して再読。本文は取得できた。保存用結果では個人名・連絡先を除外。

## 資料063（2026-10-22）
- 開いたURL：https://www.gsi.go.jp/LAW/jgd2000-AboutJGD2000.htm
- 使用ツール：PowerShell、curl.exe、Python標準html.parser。ブラウザー不使用。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_63.html "https://www.gsi.go.jp/LAW/jgd2000-AboutJGD2000.htm"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_63.html`。
- 問題：アクセス障害なし。実題は「世界測地系の導入に関して」。リンク先へは進まず、本文の案内順を記録。

## 資料064（2026-10-22）
- 開いたURL：https://www.kinomise.com/sokuryo/shiho/jyuuyou/chizu/chizu04-heimentyokukaku.pdf
- 使用ツール：PowerShell、curl.exe、Python・PyMuPDF。ブラウザー不使用。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_64.pdf "https://www.kinomise.com/sokuryo/shiho/jyuuyou/chizu/chizu04-heimentyokukaku.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_64.pdf`。11ページの先頭3行・全抽出本文を確認。
- 問題：暗号化障害は再現せず。画像内の細字は一部のみ。本文内の数値不整合を結果に記録。読了後PDFを削除。

## 資料065（2026-10-22）
- 開いたURL：https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo9.pdf
- 使用ツール：PowerShell、curl.exe、cua_repl／Chrome。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_65.pdf "https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo9.pdf"` → HTTP 000、curl (28)、約15秒で接続タイムアウト。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 座標系資料確認"})` → ナビゲーションタイムアウト。`cua.listTabs`、`cua.getTab("552231557", {browser:"chrome"})`でエラー画面を確認、`failed65.close()`で閉じた。
- 問題：ChromeでもERR_CONNECTION_TIMED_OUT。タブ作成時の変数未定義はvarで再取得して処理。PDFは取得されず、本文分析不可・NG。代替URLは探索しない。

## 資料066（2026-10-22）
- 開いたURL：https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo7new.pdf
- 使用ツール：PowerShell、curl.exe、cua_repl／Chrome。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_66.pdf "https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo7new.pdf"` → HTTP 000、curl (28)、約15秒で接続タイムアウト。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 座標系資料確認"})`、`cua.listTabs`、`cua.getTab("552231561", {browser:"chrome"})`でERR_CONNECTION_TIMED_OUTを確認、`failed66.close()`で閉じた。
- 問題：ブラウザーでも取得不可。PDFは取得されず、本文分析不可・NG。代替URLは探索しない。

## 資料067（2026-10-22）
- 開いたURL：https://home.hiroshima-u.ac.jp/teragai/mercator.pdf
- 使用ツール：PowerShell、curl.exe、cua_repl／Chrome。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_67.pdf "https://home.hiroshima-u.ac.jp/teragai/mercator.pdf"` → HTTP 000、curl (28)、約15秒で接続タイムアウト。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 座標系資料確認"})`、`cua.listTabs`、`cua.getTab("552231565", {browser:"chrome"})`でERR_CONNECTION_TIMED_OUTを確認、`failed67.close()`で閉じた。
- 問題：Chromeでも本文を取得できず、NG。PDFは取得されていない。代替URLは探索しない。

## 資料068（2026-10-22）
- 開いたURL：https://style.kugi.kyoto-u.ac.jp/education/undergraduate/syllabus/4401.pdf
- 使用ツール：PowerShell、curl.exe、Python・PyMuPDF。ブラウザー不使用。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_68.pdf "https://style.kugi.kyoto-u.ac.jp/education/undergraduate/syllabus/4401.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_68.pdf`。全2ページ先頭3行・本文・授業計画全10項目を確認。
- 問題：圧縮による読取障害なし。2025年度のシラバスで講義本文はない。教員・参考書著者の個人名を成果物から除外。読了後PDFを削除。

## 資料069（2026-10-22）
- 開いたURL：https://catalog.sp.omu.ac.jp/en/detail/20261AHE010100
- 使用ツール：PowerShell、curl.exe、cua_repl／Chrome。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_69.html "https://catalog.sp.omu.ac.jp/en/detail/20261AHE010100"` → HTTP 000、curl (28)、約15秒で接続タイムアウト。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 座標系資料確認"})`、`cua.listTabs`、`cua.getTab("552231569", {browser:"chrome"})`でERR_CONNECTION_TIMED_OUTを確認、`failed69.close()`で閉じた。
- 問題：Chromeでも本文を取得できず、NG。HTMLは取得されていない。代替URLは探索しない。

## 資料070（2026-10-22）
- 開いたURL：https://www.coronasha.co.jp/np/data/tachiyomi/978-4-339-05238-1.pdf
- 使用ツール：PowerShell、curl.exe、Python・PyMuPDF。ブラウザー不使用。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_70.pdf "https://www.coronasha.co.jp/np/data/tachiyomi/978-4-339-05238-1.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_70.pdf`。19ページを抽出したが出力上限で一部省略。追加の`python -I -c`で全ページの先頭3行のみ再出力して構成を確認。
- 問題：PDF p.19の奥付が一覧とは別書籍。目次全文を含む抽出出力には省略が生じたが、別書籍と判明したため分析を中止しNG。代替URLの探索・別資料の追加はせず、PDFは削除。

## 資料071（2026-10-22）
- 開いたURL：https://smtrc.jp/useful/knowledge/kyokai-hikai/2023_12.html
- 使用ツール：PowerShell、curl.exe、Python標準html.parser、cua_repl／Chrome。
- 取得・読取コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 15 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p04_71.html "https://smtrc.jp/useful/knowledge/kyokai-hikai/2023_12.html"` → HTTP 503。`python -I -c "import runpy;runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p04_read.py',run_name='__main__')" notes/session03_kai2_20261021/codex/tmp/batch_p04_71.html`でメンテナンス本文を確認。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 座標系資料確認"})`で同じメンテナンス画面を確認、`tab71.close()`でタブ552231573を閉じた。
- 問題：対象コラム本文は非表示。NGとして記録し、代替URLの探索はせず、保存HTMLを削除。

## 後片付け・確認（2026-10-22）
- 読了した取得物は各件の終了時に`Remove-Item -LiteralPath`で削除。接続タイムアウトの4件はファイルが作成されなかった。
- 最後に`batch_p04_71.html`と補助スクリプト`batch_p04_read.py`を削除し、今回の`batch_p04_*`一時ファイルが残っていないことを確認。
- 結果10件の必須見出しとOK／NGをPythonで点検。今回作成したChromeタブは全件閉じた。既存の別タブには操作していない。
- git操作、cacheの変更、notes/worklog.md・AGENTS.md・README.mdへの書き込みは行っていない。
- 点検時の問題：PowerShellからPythonへのパイプで日本語ファイル名が`??`に置換され初回点検が失敗したため、ASCIIのみのコードで番号をglob検索する方式に変更。再点検で10件・OK 4件・NG 6件・一時ファイル0件を確認。`cua.listTabs({browser:"chrome"})`でも今回のタブが残っていないことを確認した。
