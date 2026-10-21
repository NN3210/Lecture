# batch_p03 操作ログ

## 資料022（2026-10-22）
- 開いたURL：https://archive.nptel.ac.in/content/syllabus_pdf/105104101.pdf
- 使用ツール：PowerShell、curl.exe、Python（PyMuPDF）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_22.pdf" "https://archive.nptel.ac.in/content/syllabus_pdf/105104101.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p03_22.pdf'); [(print('PAGE',i+1,'HEAD',p.get_text().splitlines()[:3]),print(p.get_text())) for i,p in enumerate(d)]"`。全ページの先頭3行と全文を取得。
- 問題：初回は標準出力cp932によるUnicodeEncodeError。UTF-8に切り替えて再読取。全1ページのシラバスであることを確認し、取得PDFを削除。

## 資料023（2026-10-22）
- 開いたURL：https://docs.os.uk/more-than-maps/a-guide-to-coordinate-systems-in-great-britain/from-one-coordinate-system-to-another-geodetic-transformations/national-grid-transformation-ostn15-etrs89-osgb36
- 使用ツール：PowerShell、curl.exe、Python（html.parser）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_23.html" "https://docs.os.uk/more-than-maps/a-guide-to-coordinate-systems-in-great-britain/from-one-coordinate-system-to-another-geodetic-transformations/national-grid-transformation-ostn15-etrs89-osgb36"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_23.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"`。h1〜h4、本文、画像altを抽出。
- 問題：なし。サイドバー目次と本文を区別し、本文全4段落を確認。取得HTMLと抽出用一時テキストを削除。

## 資料024（2026-10-22）
- 開いたURL：https://www.oc.nps.edu/oc2902w/c_mtutor/height/height2.htm
- 使用ツール：PowerShell、curl.exe、Python（html.parser）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_24.html" "https://www.oc.nps.edu/oc2902w/c_mtutor/height/height2.htm"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_24.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"`。見出し・本文・altを抽出。
- 問題：本文取得に問題なし。図は本文の図説明で代用。取得HTML・抽出テキストを削除。

## 資料025（2026-10-22）
- 開いたURL：https://www.webpages.uidaho.edu/nrgis/secure/pdf_slides/lesson3.pdf（Chrome最終表示先：https://www.uidaho.edu/404.htm）。
- 使用ツール：PowerShell、curl.exe、Python（PyMuPDF）、cua_repl（Chrome）。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_25.pdf" "https://www.webpages.uidaho.edu/nrgis/secure/pdf_slides/lesson3.pdf"` → HTTP 403。
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p03_25.pdf'); print('PAGES',len(d)); [(print('PAGE',i+1,'HEAD',p.get_text().splitlines()[:3]),print(p.get_text())) for i,p in enumerate(d)]"` → PDFではなくFileDataError。
- ブラウザー操作：`cua.createBrowserTab("chrome", 指定URL, {sessionName:"📚 座標系資料確認"})` の表示で403 FORBIDDENを確認し、`tab25.close()` で直ちに閉じた。
- 問題：シェル・ブラウザーともアクセス拒否。NGとして記録し、保存したエラー応答を削除。代替URLは探していない。

## 資料026（2026-10-22）
- 開いたURL：https://www.slideshare.net/slideshow/lecture-11-traverse-computations/137827094
- 使用ツール：PowerShell、curl.exe、Python（html.parser）、cua_repl（Chrome）。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_26.html" "https://www.slideshare.net/slideshow/lecture-11-traverse-computations/137827094"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_26.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"` → Client Challengeのみ。
- ブラウザー操作：`cua.createBrowserTab("chrome", 指定URL, {sessionName:"📚 座標系資料確認"})` でスライド番号付き本文・altと導入工程表全文を読み、`tab26.close()` で閉じた。
- 問題：curlでは本文なし。Chromeでは全26枚中23枚の文字を取得、p.15・20・23と図表の詳細は未取得のため「一部のみ」と記録。HTML・抽出テキストを削除。

## 資料027（2026-10-22）
- 開いたURL：https://www.slideshare.net/slideshow/traversing-lecture-notes-for-geomatics-engineering/278732174
- 使用ツール：PowerShell、curl.exe、Python（html.parser）、cua_repl（Chrome）。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_27.html" "https://www.slideshare.net/slideshow/traversing-lecture-notes-for-geomatics-engineering/278732174"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_27.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"` → Client Challengeのみ。
- ブラウザー操作：`cua.createBrowserTab("chrome", 指定URL, {sessionName:"📚 座標系資料確認"})` で49枚すべてのalt・見出し、p.28の計算工程表全文を読み、`tab27.close()` で閉じた。
- 問題：curlでは本文なし。図だけのページや数式配置はaltで確認できず「一部のみ」と記録。HTML・抽出テキストを削除。

## 資料028（2026-10-22）
- 開いたURL：https://rpls.com/wp-content/uploads/converted_files/401705=6997-Working with Grid Coordinates.pdf（空白を%20に符号化して同一URLへ再試行）。
- 使用ツール：PowerShell、curl.exe、Python（PyMuPDF）、cua_repl（Chrome）。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_28.pdf" "https://rpls.com/wp-content/uploads/converted_files/401705=6997-Working with Grid Coordinates.pdf"` → 空白でcurlエラー3／HTTP 000。同コマンドのURLを%20表記にして再実行 → HTTP 403。
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p03_28.pdf'); print('PAGES',len(d)); [(print('PAGE',i+1,'HEAD',p.get_text().splitlines()[:3]),print(p.get_text())) for i,p in enumerate(d)]"` → Enable JavaScript and cookies to continueのみで教材ではない。
- ブラウザー操作：`cua.createBrowserTab("chrome", 空白符号化済み指定URL, {sessionName:"📚 座標系資料確認"})`、`tab28.getAXState()` でもセキュリティ検証画面。操作による検証解除は行わず、`tab28.close()` で閉じた。
- 問題：教材本文を取得できずNG。保存したエラー応答を削除。代替URLは検索していない。

## 資料059（2026-10-22）
- 開いたURL：https://www.gsi.go.jp/sokuchikijun/datum-main.html
- 使用ツール：PowerShell、curl.exe、Python（html.parser）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_59.html" "https://www.gsi.go.jp/sokuchikijun/datum-main.html"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_59.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"`。全見出し・目次全文・本文・画像altを抽出。
- 問題：なし。ナビゲーションと本文を区別し、JGD2024対応の本文を確認。図はalt・周辺文で代用し、HTML・抽出テキストを削除。

## 資料060（2026-10-22）
- 開いたURL：https://www.gsi.go.jp/sokuchikijun/hyoko2024rev.html
- 使用ツール：PowerShell、curl.exe、Python（html.parser）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_60.html" "https://www.gsi.go.jp/sokuchikijun/hyoko2024rev.html"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_60.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"`。全見出し・目次・本文・画像altを抽出。
- 問題：なし。2026年9月追記を含む末尾まで確認。図はalt・図題・本文で代用し、リンク先には進まず、HTML・抽出テキストを削除。

## 資料061（2026-10-22）
- 開いたURL：https://www.gsi.go.jp/buturisokuchi/grageo_geoidmodeling.html
- 使用ツール：PowerShell、curl.exe、Python（html.parser）。ブラウザー不使用。
- 実行コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o "notes/session03_kai2_20261021/codex/tmp/batch_p03_61.html" "https://www.gsi.go.jp/buturisokuchi/grageo_geoidmodeling.html"` → HTTP 200。
- 読取コマンド：`python -I -c "import runpy,sys; sys.argv=['batch_p03_parse.py','notes/session03_kai2_20261021/codex/tmp/batch_p03_61.html']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_p03_parse.py',run_name='__main__')"`。全見出し・本文・画像altを抽出。
- 問題：現在のページ名は「ジオイド・モデルの概要」だが作成方法を含み対象主題に一致。図はalt・図題・本文で代用。HTML・抽出テキストを削除。
