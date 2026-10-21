# batch_v04 操作ログ

## 資料058（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=6mEUiRqeB6U
- ツール・コマンド：PowerShellで `curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_58.html "https://www.youtube.com/watch?v=6mEUiRqeB6U"` を実行。HTTP 200。
- キャッシュなし。指定の `yt-dlp --no-update --no-playlist --skip-download --ignore-no-formats-error --write-info-json --write-auto-sub --write-sub --sub-langs ".*-orig,ja,en" --sub-format "vtt/srv3/best" --extractor-args "youtube:player_client=ios" --sleep-subtitles 3 -o "notes/session03_kai2_20261021/codex/tmp/batch_v04_58" "https://www.youtube.com/watch?v=6mEUiRqeB6U"` を実行。
- 問題：英語原語字幕は成功、日本語字幕がHTTP 429で停止。続けて `yt-dlp --no-update --no-playlist --skip-download --ignore-no-formats-error --write-info-json --extractor-args "youtube:player_client=ios" -o "notes/session03_kai2_20261021/codex/tmp/batch_v04_58" "https://www.youtube.com/watch?v=6mEUiRqeB6U"` で情報JSONを補完。PO Token・映像形式の警告はあったが、映像取得は不要。
- 読解：`python -I -c "import sys; sys.argv=['reader','58']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でhtml.parserの本文、JSON、重複除去した英語字幕を1分区切りで確認。結果を資料058.mdに保存。ブラウザー不使用、当該tmp取得ファイルは読了後削除。
## 資料073（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=hRLWfqd4xxM
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_73.html "https://www.youtube.com/watch?v=hRLWfqd4xxM"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','73']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTML本文、cache/資料073/v.info.json・v.ja-orig.vttを読み、字幕全文を1分区切りで確認。
- 問題：字幕に座標値・用語の誤認あり。図は発話のみで確認。ブラウザー・再取得なし。資料073.md保存後、当該tmp HTMLを削除し、cacheは保持。
## 資料074（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=obo2M22L7MM
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_74.html "https://www.youtube.com/watch?v=obo2M22L7MM"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','74']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTML本文とcache/資料074の情報JSON・日本語原語字幕を1分刻みで全編確認。
- 問題：縮尺係数等の数値に字幕誤認あり。本文で確定値と扱わない旨を明記。ブラウザー不使用。資料074.md保存後にtmp HTMLを削除、cache保持。
## 資料075（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=oPdlf1VpozY
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_75.html "https://www.youtube.com/watch?v=oPdlf1VpozY"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','75']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTML・cache/資料075のJSON・日本語字幕全編を1分区切りで確認。
- 問題：題名のUTMは本編字幕では扱われず、係数・距離にも字幕誤認あり。動画自体は一致するのでOK、範囲差を結果に明記。ブラウザー不使用、資料075.md保存後にtmp HTML削除、cache保持。
## 資料076（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=_KrxebZ-ymk
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_76.html "https://www.youtube.com/watch?v=_KrxebZ-ymk"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','76']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTMLとcache/資料076のJSON・日本語原語字幕を1分区切りで全編確認。
- 問題：一覧と現在の題名表記が異なるが主題・File番号・動画IDは一致。チャンネル名の個人名部分は結果で省略。ブラウザー不使用。資料076.md保存後、tmp HTML削除、cache保持。
## 資料077（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=TfdM2nsbtHE
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_77.html "https://www.youtube.com/watch?v=TfdM2nsbtHE"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','77']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTMLとcache/資料077の情報JSON・日本語字幕を1分ごとに全編確認。
- 問題：題名表記変更、字幕の分数式欠落あり。内容の一致と数値例の順序は確認。ブラウザー不使用。資料077.md保存後にtmp HTML削除、cache保持。
## 資料078（2026-10-22）
- 開いたURL：https://youtube.com/watch?pp=0gcJCdgAo7VqN5tD&v=omtCNTeinzY（指定のクエリを保持）
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_78.html "https://youtube.com/watch?pp=0gcJCdgAo7VqN5tD&v=omtCNTeinzY"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','78']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTMLとcache/資料078のJSON・全チャプター・説明欄・字幕を1分区切りで確認。
- 問題：1～3分台等の字幕欠落、数値・式の誤認が大きい。全体順序は章立てと終盤の復習で確認し、数値詳細は「一部のみ」と明記。ブラウザー不使用、資料078.md保存後tmp HTML削除、cache保持。
## 資料079（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=ajaP_dadoMQ
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_79.html "https://www.youtube.com/watch?v=ajaP_dadoMQ"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','79']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTMLとcache/資料079のJSON・日本語字幕を1分刻みで22分間全編確認。
- 問題：専門語の字幕誤認あり、文脈で読める概念・順序を抽出。図は発話に基づく。ブラウザー不使用。資料079.md保存後にtmp HTML削除、cache保持。
## 資料080（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=ySoQCbrDlSE
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_80.html "https://www.youtube.com/watch?v=ySoQCbrDlSE"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','80']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTMLとcache/資料080のJSON・日本語字幕を1分区切りで確認。
- 問題：数式箇所に字幕欠落・異常数列・不整合あり。解法の順序を記録し数値詳細は「一部のみ」とした。ブラウザー不使用。資料080.md保存後tmp HTML削除、cache保持。
## 資料081（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=3433T6L0V3k
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v04_81.html "https://www.youtube.com/watch?v=3433T6L0V3k"`。HTTP 200。
- 読解：`python -I -c "import sys; sys.argv=['reader','81']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v04_read.py',encoding='utf-8').read())"` でHTML・cache/資料081/v.info.json・v.es-orig.vttを確認。字幕を1分区切りで読んだが内容判別不能。cacheは非空のためyt-dlp再取得なし。
- ブラウザー：`cua.createBrowserTab('chrome', URL, {sessionName:'📐 資料081確認'})`、Playwrightの一時停止・もっと見る・文字起こしを表示、`getAXState()`・`domSnapshot()`・`locator('body').innerText()`で説明欄・コメント・文字起こしを確認。自動再生は最初の操作で停止（停止時0:13）。再生待ちによる分析なし。
- 問題：字幕利用不可、文字起こし本文なし、説明欄・表示コメントに目次なし。実在はOKだが講義順序は抽出不能と記載。`await tab81.close()`成功、資料081.md保存後にtmp HTML削除、cache保持。
