# batch_p02 操作ログ（2026-10-22）

## 資料011
- 開いたURL：https://ocw.mit.edu/courses/earth-atmospheric-and-planetary-sciences/12-215-modern-navigation-fall-2006/lecture-notes/12_215_lec07.pdf
- 使用ツール：mcp__cua_repl（Chrome createBrowserTab、初期アクセシビリティ表示）、apply_patch（記録）。
- 実行したコマンド：教材取得用シェルコマンドなし。
- 起きた問題：resources/index.html へ転送後、Page Not Found。実在確認NGとして打ち切り、代替URL探索なし。

## 資料012
- 開いたURL：https://mitocw.ups.edu.ec/courses/earth-atmospheric-and-planetary-sciences/12-215-modern-navigation-fall-2006/lecture-notes/12_215_lec03.pdf
- 使用ツール：mcp__cua_repl（Chrome、AX、スクロール、冒頭画像）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：`curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p02_12.pdf "指定URL"`。証明書エラー後、`C:/Windows/System32/curl.exe -L --max-time 45 -o "同保存先" "同URL"`で取得。
- 本文抽出：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p02_12.pdf'); [print('PAGE',i+1,p.get_text()) for i,p in enumerate(d)]"`。
- 起きた問題：初回ナビゲーションは時間切れだがPDFは表示済み。通常curlの証明書エラーはWindows標準curlで解消（検証無効化なし）。標準出力の文字コードエラーはUTF-8指定で解消。全19ページの本文を読取。
- 後処理：`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02_12.pdf'`で取得PDFを削除。

## 資料013
- 開いたURL：https://ocw.mit.edu/courses/12-215-modern-navigation-fall-2006/resources/12_215_lec10 （末尾スラッシュへ転送）。掲載リンクから https://ocw.mit.edu/courses/12-215-modern-navigation-fall-2006/a33cd6304e0e43da9b763fe8c762fde2_12_215_lec10.pdf を開いた。
- 使用ツール：mcp__cua_repl（Chrome、AX、PDF冒頭表示・スクロール）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：`C:/Windows/System32/curl.exe -L --max-time 45 -o notes/session03_kai2_20261021/codex/tmp/batch_p02_13.pdf "上記掲載PDFのURL"`。
- 本文抽出：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p02_13.pdf'); [print('PAGE',i+1,p.get_text()) for i,p in enumerate(d)]"`。
- 起きた問題：PDFへの移動は時間切れ表示だったが、ビューアーで全21ページのPDF表示を確認。ファイル名lec10と本文Lec 11が異なる。本文読取後、`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02_13.pdf'`で削除。

## 資料014
- 開いたURL：https://web.mit.edu/11.520/www/lectures/lecture3.html
- 使用ツール：mcp__cua_repl（Chrome goto、AX、`playwright.evaluate(()=>document.body.innerText)`、画像の表示寸法確認、座標スクロール、スクリーンショット）、apply_patch。
- 実行したコマンド：教材取得用シェルコマンドなし。ページ全体5886 pxを末尾までスクロールし、全文を読取。
- 起きた問題：埋め込み画像20点のnaturalWidth/naturalHeightが0。図は表示できず、一部のみと明記。本文は正常。外部教材の追加調査なし。

## 資料015
- 開いたURL：https://courses.washington.edu/esrm304a/Modules/Surveying/MapBasics-Datums,LandDivision,etc_au2015.pdf
- 使用ツール：mcp__cua_repl（Chrome、冒頭表示とスクロール）、exec_command、PyMuPDF、view_image、apply_patch。
- 実行したコマンド：`C:/Windows/System32/curl.exe -L --max-time 45 -o notes/session03_kai2_20261021/codex/tmp/batch_p02_15.pdf "指定URL"`。`python -I -c`でfitzによる全26ページのテキスト抽出（標準出力UTF-8）と、PDFの6・13・15・17・24・25ページの画像化・結合を実行。
- 起きた問題：ナビゲーション時間切れ後にPDF表示を確認。PDFは26ページだが内部番号は1、15～39なので、結果にはPDF順を使用。主要図の比較も確認。
- 後処理：`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02_15.pdf','notes/session03_kai2_20261021/codex/tmp/batch_p02_15_figures.jpg'`で読取用ファイルを削除。

## 資料016
- 開いたURL：https://geodesy.noaa.gov/INFO/facts/datum.shtml
- 使用ツール：mcp__cua_repl（Chrome goto、AX、`playwright.evaluate(()=>document.body.innerText)`、スクロール、写真・グラフのスクリーンショット確認）、apply_patch。
- 実行したコマンド：教材取得用シェルコマンドなし。全本文と図を読取し、ページ末尾（高さ1274 px）まで確認。
- 起きた問題：初回ナビゲーションは時間切れ表示だったが、その後ページの正常表示を確認。本文・図の欠落なし。

## 資料017
- 開いたURL：https://repository.library.noaa.gov/view/noaa/66401 。書誌に実際に掲載された https://repository.library.noaa.gov/view/noaa/66401/noaa_66401_DS1.pdf もブラウザーで開く操作を実行。
- 使用ツール：mcp__cua_repl（Chrome、書誌AX）、exec_command、PyMuPDF、view_image、apply_patch。
- 実行したコマンド：`C:/Windows/System32/curl.exe -L --max-time 45 -o notes/session03_kai2_20261021/codex/tmp/batch_p02_17.pdf "上記掲載PDFのURL"`。`python -I -c`でfitzによる各ページ先頭1700文字の抽出、出力省略後にp.19～80の先頭9行を再抽出し、p.3・5・14を画像化して確認。
- 起きた問題：ブラウザーのPDF表示はERR_BLOCKED_BY_CLIENT。指定ページは正常、掲載PDFはcurlで取得成功（97ページ、約21.4MB）。全体の本文出力が長く省略されたため見出し中心に再抽出。5分上限に従い一部のみと記録。
- 後処理：`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02_17.pdf','notes/session03_kai2_20261021/codex/tmp/batch_p02_17_preview.jpg'`で読取用ファイルを削除。

## 資料018
- 開いたURL：https://gge.ext.unb.ca/Pubs/LN37.pdf
- 使用ツール：mcp__cua_repl（Chrome、表題画像・冒頭スクロール）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：`C:/Windows/System32/curl.exe -L --max-time 45 -o notes/session03_kai2_20261021/codex/tmp/batch_p02_18.pdf "指定URL"`。`python -I -c`でfitzによる冒頭10ページの全文・残り全ページの先頭5行を抽出（標準出力UTF-8）。追加でPDF p.12、119～122、126、138の本文を抽出。
- 起きた問題：ブラウザーの移動は時間切れ後にPDF表示を確認。153ページのため5分上限内で目次・章の導入を優先し一部のみと記録。スキャンだが文字抽出できた（序文の検索不能という記述と現ファイルの状態が異なる）。
- 後処理：`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02_18.pdf'`で読取用PDFを削除。
