# batch_v03 操作ログ

## 資料048（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=s2RiPq9Y62g
- ツール・コマンド：PowerShellで `curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_48.html "https://www.youtube.com/watch?v=s2RiPq9Y62g"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','48']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。html.parserでHTML本文、jsonでメタデータ、VTTを1分区間で読取。
- 問題・対応：HTMLは題名以外の講義本文を含まないが、既存cacheの英語字幕・チャプターで確認できた。ブラウザー・動画再生・yt-dlpは使用せず。
- 保存・片付け：apply_patchで結果を保存。取得HTMLをRemove-Itemで削除し、cacheは保持。

## 資料049（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=ZGvKNkZQvJ4
- ツール・コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_49.html "https://www.youtube.com/watch?v=ZGvKNkZQvJ4"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','49']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。HTML、JSON、アラビア語VTTを読取。
- 問題・対応：90分の字幕出力が長いため重複を除き2分ごとの冒頭・中間・末尾を抽出。出力から欠けた30〜52分はpython -Iで範囲を絞って再読。一部のみの精読と明記。ブラウザー不使用。
- 保存・片付け：結果保存後に取得HTMLを削除。cache保持。

## 資料050（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=kXrAIGhjqW4
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_50.html "https://www.youtube.com/watch?v=kXrAIGhjqW4"` → HTTP 200。cacheなし。
- 字幕コマンド：`yt-dlp --no-update --no-playlist --skip-download --ignore-no-formats-error --write-info-json --write-auto-sub --write-sub --sub-langs ".*-orig,ja,en" --sub-format "vtt/srv3/best" --extractor-args "youtube:player_client=ios" --sleep-subtitles 3 -o "notes/session03_kai2_20261021/codex/tmp/batch_v03_50" "https://www.youtube.com/watch?v=kXrAIGhjqW4"`。
- 問題・対応：英語原語VTT取得後、日本語VTTがHTTP 429で終了コード1。info.json未出力。動画形式・PO Token警告あり。取得済み英語字幕は読めたため再取得・ブラウザーは不要と判断。
- 読取：`python -I -c "import sys; sys.argv=['reader','50']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。さらにpython -IでHTML中のytInitialPlayerResponseをjson.JSONDecoderで読み、題名・長さ・説明を補完。
- 保存・片付け：結果保存後、tmpの当該HTML・VTTをRemove-Itemで削除。動画再生なし。

## 資料051（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=VCDC78wpuJc
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_51.html "https://www.youtube.com/watch?v=VCDC78wpuJc"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','51']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。HTMLとcacheのJSON・英語VTTを確認。
- 問題・対応：字幕のない区間があり、数値計算の詳細は一部のみと明記。チャプターで構成を補完。ブラウザー・再生・追加取得なし。
- 保存・片付け：結果保存後に取得HTMLを削除。cache保持。

## 資料052（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=ABFGVdXPlXI
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_52.html "https://www.youtube.com/watch?v=ABFGVdXPlXI"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','52']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。cacheのJSON・英語VTTを1分単位で確認。
- 問題・対応：例題の最終数値に字幕上の不整合あり。直前の加算式と区別して記載。映像未確認。ブラウザー・再生なし。
- 保存・片付け：結果保存後に取得HTMLを削除。cache保持。

## 資料053（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=OKG87OvYS7U
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_53.html "https://www.youtube.com/watch?v=OKG87OvYS7U"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','53']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。cacheのJSON・VTTを1分単位で全編確認。
- 問題・対応：cacheにplaylist.jsonなし。前後回は未確認とし、追加URLは探さず。字幕に数値の揺れ、講義中に数式表示不具合への言及あり。ブラウザー・再生なし。
- 保存・片付け：結果保存後に取得HTMLを削除。個人名のチャンネル名は成果物に記載せず。cache保持。

## 資料054（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=fxiLCygDpLo
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_54.html "https://www.youtube.com/watch?v=fxiLCygDpLo"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','54']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。JSON・VTTを1分区間で確認。
- 問題・対応：チャプターなし。字幕から時刻区切りを推定。数値転記に揺れがあるため未確認部分を明記。ブラウザー・再生なし。
- 保存・片付け：結果保存後に取得HTMLを削除。cache保持。

## 資料055（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=wMfEdvf6_kw
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_55.html "https://www.youtube.com/watch?v=wMfEdvf6_kw"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','55']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。JSON・VTTの全編を1分区間で確認。
- 問題・対応：チャプターなし。第4象限の引き算の発言に不整合があり、説明欄と先行説明に照合して記録。ブラウザー・再生なし。
- 保存・片付け：結果保存後に取得HTMLを削除。チャンネル名の個人名部分は省略。cache保持。

## 資料056（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=yTTcMqsJ4CY（curlおよびChrome。外部リンクは開かず）。
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_56.html "https://www.youtube.com/watch?v=yTTcMqsJ4CY"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','56']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。cacheはJSONのみで字幕・チャプターなし。空cacheではないためyt-dlpを再実行せず。
- ブラウザー：`cua.createBrowserTab("chrome", URL, {sessionName:"📐 測量資料確認"})`、説明欄を展開、`playwright.locator('body').innerText()`、座標スクロールでコメントを確認。時刻付き目次なし。
- 問題・対応：ページが自動再生したため直ちに停止操作（停止時0:29）し、再生待ちや映像解析は行わず。説明欄の記述順で代用し、動画の教授順序は未確認・一部のみと明記。
- 保存・片付け：`t56.close()`で作成タブを閉じた。結果保存後に取得HTMLを削除。cache保持。

## 資料057（2026-10-22）
- 開いた URL：https://www.youtube.com/watch?v=RKfHmyCieQ8
- 取得：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v03_57.html "https://www.youtube.com/watch?v=RKfHmyCieQ8"` → HTTP 200。
- 読取：`python -I -c "import sys; sys.argv=['reader','57']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v03_read.py',encoding='utf-8').read())"`。JSON・英語VTT全編を1分区間で確認。追加のpython -Iでlanguageフィールドとヒンディー語VTT冒頭を照合。
- 問題・対応：チャプターなし。英語・ヒンディー語の字幕が併存し、音声言語は未確認と明記。専門用語の簡略化は資料の説明として記録し、事実確認済みとは扱わず。ブラウザー・再生なし。
- 保存・片付け：結果保存後に取得HTMLを削除。cache保持。共通読取スクリプトも最後に削除し、結果10件と操作ログの形式をpython -Iで点検。
