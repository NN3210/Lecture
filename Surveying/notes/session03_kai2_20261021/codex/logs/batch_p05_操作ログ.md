# batch_p05 操作ログ（2026-10-22）

## 資料072
- 開いたURL：https://desktop.arcgis.com/ja/arcmap/latest/map/projections/gauss-kruger.htm
- ツール・取得コマンド：PowerShell／curl.exe。`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_72.html "https://desktop.arcgis.com/ja/arcmap/latest/map/projections/gauss-kruger.htm"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_72.html`（html.parserで見出し・本文・図alt）。
- 問題：初回は標準出力cp932でUnicodeEncodeError。`-I`では環境変数が無効なため標準出力をUTF-8に再設定して解消。ブラウザー不使用。
- 後処理：結果保存後、取得HTMLを削除。

## 資料087
- 開いたURL：https://gwb.schule.at/pluginfile.php/366833/mod_resource/content/2/04-28102025_Geoinfo_Geokomm_2025_Landeskoordinaten.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_87.pdf "https://gwb.schule.at/pluginfile.php/366833/mod_resource/content/2/04-28102025_Geoinfo_Geokomm_2025_Landeskoordinaten.pdf"` → HTTP 000、curl (28)、約22秒で接続失敗。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 測量資料確認"})`。作成呼出しがタイムアウトしたため、`cua.getState()` → `cua.getTab("552231577", {browser:"chrome"})`で既存タブを取得。
- 問題・判定：Chromeも「このサイトにアクセスできません／ERR_CONNECTION_TIMED_OUT」。NGとして保存。代替URL探索なし。
- 後処理：`await t87.close()`で作成タブを閉鎖。取得ファイルなし。

## 資料088
- 開いたURL：https://wuecampus.uni-wuerzburg.de/moodle/pluginfile.php/2868527/mod_resource/content/1/01b-bezugssysteme.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_88.pdf "https://wuecampus.uni-wuerzburg.de/moodle/pluginfile.php/2868527/mod_resource/content/1/01b-bezugssysteme.pdf"` → HTTP 000、curl (28)、約22秒で接続失敗。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 測量資料確認"})` → ナビゲーションがタイムアウト。`cua.listTabs()`と`cua.getTab("552231581", {browser:"chrome"})`で確認。
- 問題・判定：ChromeでもERR_CONNECTION_TIMED_OUT。初回の変数束縛失敗は別変数で取得して対処。本文取得不可、NG。
- 後処理：`await close88.close()`で作成タブ閉鎖。取得ファイルなし。代替URL探索なし。

## 資料089
- 開いたURL：https://de.wikibooks.org/wiki/Mathematische_Geod%C3%A4sie
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_89.html "https://de.wikibooks.org/wiki/Mathematische_Geod%C3%A4sie"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_89.html`（html.parser）。
- 問題：本文がほぼ空の草案で、概要・見出し・2つの数値のみ。ページ実在はOK、講義内容の抽出は章立てに限定。ブラウザー不使用。
- 後処理：結果保存後、取得HTMLを削除。

## 資料090
- 開いたURL：https://moodle.upm.es/en-abierto/pluginfile.php/734/mod_label/intro/Sistemas_de_referencia0809.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_90.pdf "https://moodle.upm.es/en-abierto/pluginfile.php/734/mod_label/intro/Sistemas_de_referencia0809.pdf"` → HTTP 404。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_90.pdf`。PDF署名がないためhtml.parserで読み、Moodleのcontextテーブルのレコード不在エラーを確認。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 測量資料確認"})`。同じエラー本文を確認してNG。`await t90.close()`でタブ閉鎖。
- 後処理：PDF名で保存されたエラーHTMLを削除。代替URL探索なし。

## 資料093
- 開いたURL：https://ift-ik-84.webself.net/file/si123755/download/coursdetopographieettopometriegenerale-fi1917013.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_93.pdf "https://ift-ik-84.webself.net/file/si123755/download/coursdetopographieettopometriegenerale-fi1917013.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_93.pdf 1-21`（PyMuPDF、65ページの先頭行・目次・本文）。
- 追加読取：出力省略が生じたため、`python -I -c`内で`fitz.open(...)`し、全ページ先頭行と`d[0:13]`相当の本文を再出力、`print(d[49].get_text())`で第4章目次の全文を補完。第1章の全文と全4章の目次を確認。
- 問題・範囲：ファイルは第1章だけでなく全4章を含む。第1章を中心に分析し、後続章は目次の概観と明記。ブラウザー不使用。
- 後処理：結果保存後、取得PDFを削除。

## 資料094
- 開いたURL：https://piles.cerema.fr/IMG/pdf/Lambert_93_cle7498e8.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_94.pdf "https://piles.cerema.fr/IMG/pdf/Lambert_93_cle7498e8.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_94.pdf 1-50`。PDF署名なし。html.parserで保守中HTMLと確認。
- ブラウザー操作：`cua.createBrowserTab("chrome", URL, {sessionName:"📚 測量資料確認"})` → 同じ「Maintenance en cours」。HTTP成功でも資料本文がないためNG。
- 後処理：`await t94.close()`でタブ閉鎖。取得した保守中HTMLを削除。代替URL探索なし。

## 資料097
- 開いたURL：https://petecv.ufsc.br/wp-content/uploads/2023/04/Apostila-Topografia-I-Versao-Marco_2023.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_97.pdf "https://petecv.ufsc.br/wp-content/uploads/2023/04/Apostila-Topografia-I-Versao-Marco_2023.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_97.pdf`（PyMuPDF、全95ページ先頭行）。
- 追加読取：`python -I -c`内で`fitz.open(...)`、`get_text()`を使用。目次pp.3–6、導入pp.7–10、基礎pp.21–40、第4章pp.49–67を抽出。先頭が定型著者ヘッダーのため、5行を除いた本文冒頭も確認。出力が長い部分は範囲を狭めて再取得した。
- 問題・範囲：目次のページ番号と本文が不一致。PDF通し番号を採用。全体精読ではなく座標系関連を重点分析と明記。ブラウザー不使用。
- 後処理：結果保存後、取得PDFを削除。

## 資料100
- 開いたURL：https://www.its.ac.id/tgeomatika/wp-content/uploads/sites/32/2021/03/Sistem-Koordinat-dan-Proyeksi-Peta.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_100.pdf "https://www.its.ac.id/tgeomatika/wp-content/uploads/sites/32/2021/03/Sistem-Koordinat-dan-Proyeksi-Peta.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_100.pdf 1-20`（実際は全2ページ。先頭行・全文を取得）。
- 問題・範囲：修士課程のシラバスであり授業本文はない。概要と主要トピックの差を明記し、記載順と実施順を区別。科目コードは空欄。ブラウザー不使用。
- 後処理：結果保存後、取得PDFを削除。

## 資料102
- 開いたURL：https://lu.belstu.by/wp-content/uchebnaya-rabota/dnevnoe/lh/inzhenernaya-geodeziya/lekciya-3-ing-geod.pdf
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p05_102.pdf "https://lu.belstu.by/wp-content/uchebnaya-rabota/dnevnoe/lh/inzhenernaya-geodeziya/lekciya-3-ing-geod.pdf"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('notes/session03_kai2_20261021/codex/tmp/batch_p05_read.py',encoding='utf-8').read())" notes/session03_kai2_20261021/codex/tmp/batch_p05_102.pdf 1-30`（実際は7ページ。先頭行と全本文を取得、目次なし）。
- 問題・範囲：p.3の式(1)本体は文字抽出不可。前後の説明・変数定義で話題を把握。緯線・直交座標の説明の不整合を結果に記載。ブラウザー不使用。
- 後処理：結果保存後、取得PDFを削除。

## 完了確認
- 指定10件の結果ファイル、指定見出し5つ、OK資料の5〜15段階、各件の操作ログをPythonで確認。OK 6件、NG 4件。
- 本バッチが作成したChromeタブ4件は各件終了時に閉鎖済み。既存の他タブは変更していない。
- 取得PDF・HTMLと読取補助スクリプトを削除し、tmp内にbatch_p05の残存ファイルがないことを確認。cacheの変更、git操作、worklog・AGENTS・READMEへの書込みなし。
