# batch_r02 操作ログ

## 資料011（2026-10-22）
- 開いた URL：https://ocw.mit.edu/courses/12-215-modern-navigation-fall-2006/10ed0c71305cd32af8b44720195d31b5_12_215_lec02.pdf
- ツール・取得コマンド：PowerShell で `curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_11.pdf "上記URL"`。HTTP 200。
- 読取コマンド：`python -I -c "import fitz,sys; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_r02_11.pdf'); print('PAGES',len(d)); [(print('PAGE',i+1,'HEAD',p.get_text().splitlines()[:3]),print(p.get_text())) for i,p in enumerate(d)]"`。21ページの冒頭と本文、p.2 の目次全文を確認。
- 起きた問題：初回の標準出力が cp932 で UnicodeEncodeError。UTF-8 に指定して再読取。p.12 の画像内の式は未抽出のため一部のみと明記。ブラウザー不使用。
- 保存・後処理：資料011.md を保存。取得 PDF は読取後に削除する。
 
## 資料065（2026-10-22）
- 開いた URL：https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo9.pdf
- ツール・取得コマンド：PowerShell で `curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_65.pdf "https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo9.pdf"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` → Page.navigate タイムアウト。`cua.getTab("552231649", {browser:"chrome"})` も Page.getFrameTree タイムアウト。
- 起きた問題：PDF を取得できず、Chrome の作成タブも about:blank のまま。内容と実タイトルは未確認のため NG とした。
- 保存・後処理：資料065.md を保存。`researchBrowser.tabs.get("552231649")` → `close()` で閉じ、タブ一覧が空と確認。PDF ファイルは生成されていない。

## 資料066（2026-10-22）
- 開いた URL：https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo7new.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_66.pdf "https://home.hiroshima-u.ac.jp/sakuno/Jugyo/sokuryo/jugyo7new.pdf"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` は Page.navigate タイムアウト。作成されたタブ552231655を取得し、`playwright.domSnapshot()` でエラー画面を確認。
- 起きた問題：Chrome に「このサイトにアクセスできません」「ERR_CONNECTION_TIMED_OUT」。本文・実タイトルとも未確認で NG。
- 保存・後処理：資料066.md を保存。`close()` 後のタブ一覧は空。PDF ファイルは生成されていない。

## 資料067（2026-10-22）
- 開いた URL：https://home.hiroshima-u.ac.jp/teragai/mercator.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_67.pdf "https://home.hiroshima-u.ac.jp/teragai/mercator.pdf"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` は Page.navigate タイムアウト。タブ552231661の `playwright.domSnapshot()` も Emulation.setFocusEmulationEnabled のタイムアウト。
- 起きた問題：取得・ブラウザー双方で教材本文が読めず NG。実タイトルは未確認。
- 保存・後処理：資料067.md を保存。`close()` 後のタブ一覧は空。PDF ファイルは生成されていない。

## 資料069（2026-10-22）
- 開いた URL：https://catalog.sp.omu.ac.jp/en/detail/20261AHE010100
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_69.html "https://catalog.sp.omu.ac.jp/en/detail/20261AHE010100"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` は Page.navigate タイムアウト。タブ552231667の `playwright.domSnapshot()` も Emulation.setFocusEmulationEnabled のタイムアウト。
- 起きた問題：本文と実タイトルを確認できず NG。URL の /en/ と一覧の言語表記との対応も確認できないため、言語は一覧由来と明記。
- 保存・後処理：資料069.md を保存。`close()` 後のタブ一覧は空。HTML ファイルは生成されていない。

## 資料071（2026-10-22）
- 開いた URL：https://smtrc.jp/useful/knowledge/kyokai-hikai/2023_12.html
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_71.html "https://smtrc.jp/useful/knowledge/kyokai-hikai/2023_12.html"`。HTTP 503。
- 読取コマンド：`python -I -c "exec(open('notes/session03_kai2_20261021/codex/tmp/batch_r02_html.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_r02_71.html`。html.parser で title・h1〜h4・本文・図altを抽出。
- 起きた問題：記事ではなく「システムメンテナンス」、停止期間「10月21日(水) 18：00 ～」という案内。`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` でも同じ内容を確認して NG。
- 保存・後処理：資料071.md を保存。`tab71.close()` 後のタブ一覧は空。取得 HTML は読取後に削除。

## 資料087（2026-10-22）
- 開いた URL：https://gwb.schule.at/pluginfile.php/366833/mod_resource/content/2/04-28102025_Geoinfo_Geokomm_2025_Landeskoordinaten.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_87.pdf "https://gwb.schule.at/pluginfile.php/366833/mod_resource/content/2/04-28102025_Geoinfo_Geokomm_2025_Landeskoordinaten.pdf"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` は Page.navigate タイムアウト。タブ552231679の `playwright.domSnapshot()` も Emulation.setFocusEmulationEnabled のタイムアウト。
- 起きた問題：本文と実タイトルを確認できず NG。言語・種別は一覧の情報と明記。
- 保存・後処理：資料087.md を保存。`close()` 後のタブ一覧は空。PDF ファイルは生成されていない。

## 資料088（2026-10-22）
- 開いた URL：https://wuecampus.uni-wuerzburg.de/moodle/pluginfile.php/2868527/mod_resource/content/1/01b-bezugssysteme.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_88.pdf "https://wuecampus.uni-wuerzburg.de/moodle/pluginfile.php/2868527/mod_resource/content/1/01b-bezugssysteme.pdf"`。HTTP 000、curl (28)、接続20秒でタイムアウト。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` は Page.navigate タイムアウト。タブ552231685の `playwright.domSnapshot()` も Emulation.setFocusEmulationEnabled のタイムアウト。
- 起きた問題：本文・実タイトルとも確認できず NG。認証の要否も未確認。
- 保存・後処理：資料088.md を保存。`close()` 後のタブ一覧は空。PDF ファイルは生成されていない。

## 資料094（2026-10-22）
- 開いた URL：https://piles.cerema.fr/IMG/pdf/Lambert_93_cle7498e8.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_94.pdf "https://piles.cerema.fr/IMG/pdf/Lambert_93_cle7498e8.pdf"`。HTTP 200、36,545 bytes、先頭は `<!doctype html>`。
- 読取コマンド：`python -I -c "from pathlib import Path; import sys; sys.stdout.reconfigure(encoding='utf-8'); p=Path('notes/session03_kai2_20261021/codex/tmp/batch_r02_94.pdf'); print('BYTES',p.stat().st_size,'SIGNATURE',p.read_bytes()[:80]); import fitz; d=fitz.open(p); print('PAGES',len(d)); [(print('PAGE',i+1,'HEAD',pg.get_text().splitlines()[:3]),print(pg.get_text())) for i,pg in enumerate(d)]"`。続けて `python -I -c "exec(open('notes/session03_kai2_20261021/codex/tmp/batch_r02_html.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_r02_94.pdf` でHTMLを解析。
- 起きた問題：title・h1 は「Maintenance en cours」、本文はサービス更新中の案内。fitz の表示上の2ページはHTMLの再構成であり、スライド枚数として採用しない。`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` でも同じ案内のため NG。
- 保存・後処理：資料094.md を保存。`tab94.close()` 後のタブ一覧は空。取得したPDF拡張子のHTMLは削除。

## 資料107（2026-10-22）
- 開いた URL：https://avys.omu.edu.tr/storage/app/public/asisman/134303/BDH_Hafta_2.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" --connect-timeout 20 --max-time 45 -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_r02_107.pdf "https://avys.omu.edu.tr/storage/app/public/asisman/134303/BDH_Hafta_2.pdf"`。HTTP 000、curl (6)、Could not resolve host。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 座標系資料確認"})` で net::ERR_NAME_NOT_RESOLVED。タブ552231697の `playwright.domSnapshot()` は Runtime.evaluate のタイムアウト。
- 起きた問題：ホスト名解決失敗により本文・実タイトルとも確認できず NG。
- 保存・後処理：資料107.md を保存。`close()` 後のタブ一覧は空。PDF ファイルは生成されていない。
