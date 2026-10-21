# batch_p01 操作ログ（2026-10-22）

## No.1
- 開いたURL：https://courses.ems.psu.edu/geog862/book/export/html/1669
- 使ったツール：mcp__cua_repl（Chrome の createBrowserTab、body.innerText）、apply_patch（結果保存）。
- 実行したコマンド：対象資料取得用のシェルコマンドなし。
- 起きた問題：ページタイトルが「Page not found | Course Template」、本文はスキップリンクのみ。実在確認NGとして記録し、代替URLは探していない。

## No.2
- 開いたURL：https://courses.ems.psu.edu/geog862/print/l6.html
- 使ったツール：mcp__cua_repl（Chrome の goto、getAXState、body.innerText）、exec_command、apply_patch（結果保存）。
- 実行したコマンド：PowerShell の here-string を python -I - に渡して結果作成を試行。文字化けで失敗したため apply_patch で保存。資料取得用コマンドなし。
- 起きた問題：ページタイトルが「Page not found | Course Template」、本文はスキップリンクのみ。実在確認NG。代替URL探索なし。

## No.3
- 開いたURL：https://www.e-education.psu.edu/geog862/print/book/export/html/1817
- 使ったツール：mcp__cua_repl（Chrome の goto、getAXState、body.innerText）、apply_patch（結果保存）。
- 実行したコマンド：対象資料取得用のシェルコマンドなし。
- 起きた問題：courses.ems.psu.edu の同じパスへ自動転送され「Page not found | Course Template」を表示。本文はスキップリンクのみ。実在確認NG、代替URL探索なし。

## No.4
- 開いたURL：https://courses.ems.psu.edu/natureofgeoinfo/web/node/1698
- 使ったツール：mcp__cua_repl（Chrome の goto、body.innerText、座標指定scroll、getAXState、図のスクリーンショット）、apply_patch。
- 実行したコマンド：対象資料取得用のシェルコマンドなし。
- 起きた問題：なし。指定ページ全文と地形図を確認し、末尾までスクロール。隣接ページへは移動していない。

## No.5
- 開いたURL：https://feng.stafpu.bu.edu.eg/Surveying%20Engineering/4251/crs-18842/Files/Lecture%204%20-%20Datums%20and%20Geoid.pdf（指定URLの空白をURL符号化）
- 使ったツール：mcp__cua_repl（Chrome PDF表示・ページ移動・視認）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_5.pdf "上記URL"。python -I -c で fitz.open と各ページの get_text() を実行。
- 起きた問題：初回ナビゲーションはタイムアウトしたが、直後の画面取得で正常表示を確認。本文出力がcp932の記号で失敗したためASCIIエスケープ表示に変更して全19ページを確認。
- 後処理：読了後、Remove-Item -LiteralPath で当該PDFのみ削除。図の精読は一部のみと結果に明記。

## No.6
- 開いたURL：https://feng.stafpu.bu.edu.eg/Surveying%20Engineering/4251/crs-18842/Files/Lecture%209%20-%20Height%20Systems.pdf
- 使ったツール：mcp__cua_repl（Chrome PDF表示・冒頭目次視認）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_6.pdf "上記URL"。python -I -c で fitz.open と全ページの get_text()、ASCIIエスケープ表示を実行。
- 起きた問題：初回ナビゲーションはタイムアウトしたが、その後の画面取得でPDFの正常表示を確認。p.18の見出しと本文の不一致を結果に記録。
- 後処理：読了後、Remove-Item -LiteralPath で当該PDFのみ削除。画像の精読は一部のみ。

## No.7
- 開いたURL：https://feng.stafpu.bu.edu.eg/Surveying%20Engineering/4266/crs-18651/Files/Lecture%204%20Height%20Systems%20for%20students.pdf
- 使ったツール：mcp__cua_repl（Chrome PDF・目次視認）、exec_command、PyMuPDF、Pillow、view_image、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_7.pdf "上記URL"。python -I -c で全43ページのget_text()と、画像ページのget_pixmap()による確認用一覧PNG作成。
- 起きた問題：ナビゲーションのタイムアウト後に正常表示を確認。pp.3–10・42はテキストが空のため画像で補完。表紙と内部タイトルの講義番号不一致を記録。
- 後処理：Remove-Item -LiteralPath で当該PDFと確認用PNGのみ削除。

## No.8
- 開いたURL：https://feng.stafpu.bu.edu.eg/Surveying%20Engineering/897/crs-18550/Files/Surveying%20Lec%203%202021-2022.pdf
- 使ったツール：mcp__cua_repl（Chrome PDF表紙・目次）、exec_command、PyMuPDF、Pillow、view_image、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_8.pdf "上記URL"。python -I -c で全10ページのget_text()とpp.3–9のget_pixmap()による図・式の一覧PNG作成。
- 起きた問題：ナビゲーションのタイムアウト後に正常表示を確認。内部タイトルは別講義名だが表紙・本文の一致を確認。p.6の演算記号不整合を記録。補助動画は開いていない。
- 後処理：Remove-Item -LiteralPath で当該PDFと確認用PNGのみ削除。

## No.9
- 開いたURL：https://filelist.tudelft.nl/CiTG/Over%20faculteit/Afdelingen/Geoscience%20%26%20Remote%20sensing/Study/TRS_3-1.pdf
- 使ったツール：mcp__cua_repl（Chrome表紙・目次）、exec_command、PyMuPDF、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_9.pdf "上記URL"。python -I -c で全ページ先頭行、序文・目次・主要章冒頭のget_text()を取得。
- 起きた問題：初回ナビゲーションのタイムアウト後に正常表示を確認。文字出力のcp932エラーをASCIIエスケープで解消。今回のPDFはテキスト抽出可能で、予定した画像化は不要。5分上限に合わせ精読は一部のみと明記。
- 後処理：Remove-Item -LiteralPath で当該PDFのみ削除。

## No.10
- 開いたURL：https://www.gis.uni-stuttgart.de/lehre/LectureNotes/LNRefSyst_180529.pdf
- 使ったツール：mcp__cua_repl（Chrome表紙・目次）、exec_command、PyMuPDF、view_image、apply_patch。
- 実行したコマンド：curl.exe -L --max-time 60 -o notes/session03_kai2_20261021/codex/tmp/batch_p01_10.pdf "上記URL"。python -I -c で目次、全ページ先頭行、主要節の本文を取得し、p.5をget_pixmap()でPNG化。
- 起きた問題：初回ナビゲーションのタイムアウト後にPDF表示を確認。数式・特殊文字はASCIIエスケープ表示で読み、冒頭の関係図は画像で確認。長い導出の精読は一部のみと明記。
- 後処理：Remove-Item -LiteralPath で当該PDFと確認用PNGのみ削除。
