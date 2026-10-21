# batch_v01r 操作ログ

## 資料029（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=5MVfc33PGMk
- ツール・取得コマンド：PowerShellで `curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_29.html "https://www.youtube.com/watch?v=5MVfc33PGMk"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','29']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser、json、VTTの2分区間抽出を使用。
- 確認範囲・問題：HTMLはタイトルと共通部分のみ。キャッシュのID・メタデータ・英語字幕で全編確認。初回はcp932出力でUnicodeEncodeErrorが出たため、標準出力をUTF-8にして再実行。ブラウザー・動画再生・yt-dlp再取得は不要。
- 保存・後処理：`results/資料029.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料030（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Bx4RLXRWpgA
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_30.html "https://www.youtube.com/watch?v=Bx4RLXRWpgA"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','30']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parserとJSON、VTTの2分区間抽出を使用。
- 確認範囲・問題：HTML本文は共通部分のみ。既存キャッシュのメタデータ・チャプター・英語字幕で全編確認できた。ブラウザー・動画再生・再取得なし。
- 保存・後処理：`results/資料030.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料031（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=dgMAuuuJ6r4
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_31.html "https://www.youtube.com/watch?v=dgMAuuuJ6r4"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','31']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・英語VTTの2分区間抽出を使用。
- 確認範囲・問題：全編の話題順を確認。数式と数字の自動字幕は一部不鮮明なため厳密転記を避け、説明欄の扁平率の訂正を記載。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料031.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料032（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Z41Dt7_R180
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_32.html "https://www.youtube.com/watch?v=Z41Dt7_R180"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','32']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・VTTの2分区間抽出を使用。
- 確認範囲・問題：説明欄の時刻目次と英語字幕で全編確認。HTML本文は共通部分のみだがキャッシュが有効。ブラウザー・動画再生・再取得なし。
- 保存・後処理：`results/資料032.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料033（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=iagP0CqBAAg
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_33.html "https://www.youtube.com/watch?v=iagP0CqBAAg"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','33']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・英語VTTの2分区間抽出を使用。
- 確認範囲・問題：全編の話題順を確認。ジオイド・楕円体・測地基準系の用語を大まかに扱う箇所を注記。HTML本文は共通部分のみ。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料033.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料034（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=dX6a6kCk3Po
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_34.html "https://www.youtube.com/watch?v=dX6a6kCk3Po"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','34']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・VTTの2分区間抽出を使用。
- 確認範囲・問題：全編の話題順を確認。比較表の細かい数値は字幕が崩れるため一部のみ。モデルと製品の説明は公開当時のものと明記。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料034.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料035（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=rUObSHQ6WiY
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_35.html "https://www.youtube.com/watch?v=rUObSHQ6WiY"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','35']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・VTTの2分区間抽出を使用。
- 確認範囲・問題：全編確認。絶対・相対精度、設定忘れの2地域比較まで記録。モデルの説明は公開当時の発話として扱った。HTML本文は共通部分のみ。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料035.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料036（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=y33_I5xRynQ
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_36.html "https://www.youtube.com/watch?v=y33_I5xRynQ"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','36']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・VTTの2分区間抽出を使用。
- 確認範囲・問題：全編確認。題名・章名と実際の説明範囲を区別し、最後は問いのみであると記録。HTML本文は共通部分のみ。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料036.md`を保存。取得HTMLを削除し、キャッシュは保持。

## 資料037（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=FPKz-kMKX3Y
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v01r_37.html "https://www.youtube.com/watch?v=FPKz-kMKX3Y"`。HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['reader','37']; exec(open('notes/session03_kai2_20261021/codex/tmp/batch_v01r_read.py',encoding='utf-8').read())"`。html.parser・JSON・VTTの2分区間抽出を使用。
- 確認範囲・問題：全編確認。章境界と発話の開始がずれる箇所は字幕を優先し、NGS公式ではないことを明記。HTML本文は共通部分のみ。ブラウザー・再生・再取得なし。
- 保存・後処理：`results/資料037.md`を保存。取得HTMLと共通の一時読取スクリプトを削除し、キャッシュは保持。
