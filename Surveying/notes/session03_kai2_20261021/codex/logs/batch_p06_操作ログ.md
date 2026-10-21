# batch_p06 操作ログ

## 資料106（2026-10-22）
- 開いたURL：https://acikders.ankara.edu.tr/mod/resource/view.php?id=10758
- 使用ツール：PowerShell、curl.exe、Python（隔離モード）、PyMuPDF。ブラウザーは使用していない。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p06_106.html "https://acikders.ankara.edu.tr/mod/resource/view.php?id=10758"` → HTTP 200、773,270バイト。先頭バイトがPDFのため同じtmp内の `.pdf` に変更。
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p06_106.pdf'); print('PAGES',len(d)); [(print('PAGE',i+1,'HEAD:', ' | '.join([x.strip() for x in p.get_text().splitlines() if x.strip()][:3])),print(p.get_text())) for i,p in enumerate(d)]"`。全5ページの先頭3行・全文・p.1目次全文を取得。
- 起きた問題：初回の標準入力経由 `python -I -` はcp932でトルコ語を出力できず中断。指定の `python -I -c` とUTF-8標準出力に切り替えて解消。図・画面内文字は周辺本文で代用。本文後半のデータム／分帯の用語の曖昧さは結果に注記。
- 保存・削除：`results/資料106.md` を保存後、`Remove-Item -LiteralPath notes/session03_kai2_20261021/codex/tmp/batch_p06_106.pdf` で取得PDFを削除。

## 資料107（2026-10-22）
- 開いたURL：https://avys.omu.edu.tr/storage/app/public/asisman/134303/BDH_Hafta_2.pdf
- 使用ツール：PowerShell、curl.exe、Chrome（cua_repl）。取得失敗のためPyMuPDFでの読取は実行できなかった。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p06_107.pdf "https://avys.omu.edu.tr/storage/app/public/asisman/134303/BDH_Hafta_2.pdf"` → 終了コード6、HTTP表示000、`Could not resolve host: avys.omu.edu.tr`。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 測量資料107"})` → `net::ERR_NAME_NOT_RESOLVED`。`cua.getTab("552231593", {browser:"chrome"})` でエラー画面の `DNS_PROBE_FINISHED_NXDOMAIN` を確認し、`failed107.close()` でタブを閉じた。
- 起きた問題・判断：curlとChromeの双方で名前解決失敗。本文・実際のタイトル・ページ数は確認不能のため実在確認NGと記録し、代替URLは探索していない。
- 保存・後片付け：`results/資料107.md` を保存。`Test-Path` で取得先ファイルの残存を確認し、存在する場合のみ `Remove-Item -LiteralPath` で削除。cacheには触れていない。
