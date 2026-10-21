# batch_v05 操作ログ

## 資料082（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=sE091TU8XCk
- ツール・取得コマンド：PowerShellで `curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_82.html "https://www.youtube.com/watch?v=sE091TU8XCk"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','82']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。html.parserでHTML本文、jsonで動画情報、VTTを90秒単位で重複除去して全編確認。
- 問題：HTMLはタイトルと共通フッターが中心。既存の日本語自動字幕で補完し、誤認識のある数値は慎重に扱った。ブラウザー・動画再生・yt-dlp再取得なし。
- 保存：`results/資料082.md`。読み終えた一時HTMLを削除、cacheは保持。
## 資料083（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=2Dq0VF3ItiI
- ツール・取得コマンド：PowerShellで `curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_83.html "https://www.youtube.com/watch?v=2Dq0VF3ItiI"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','83']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。HTML本文と既存JSON、日本語VTT全編を90秒単位で確認。
- 問題：HTMLに講義本文はなく、字幕に数値・専門語の誤認識あり。キャッシュで内容を確認できたためブラウザー・yt-dlp・再生なし。
- 保存：`results/資料083.md`。読み終えた一時HTMLを削除、cacheは保持。

## 資料084（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Vdqq7nSPuic
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_84.html "https://www.youtube.com/watch?v=Vdqq7nSPuic"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','84']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。HTML本文、既存JSONの説明・公式チャプター、日本語VTTを全編確認。
- 問題：HTMLに講義本文なし。自動字幕の専門語誤認識はチャプター・説明欄と照合。クレジット区間には字幕なし。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料084.md`。一時HTML削除、cache保持。個人名を成果物へ転記せず。

## 資料085（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=dMedzzDFgDM
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_85.html "https://www.youtube.com/watch?v=dMedzzDFgDM"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','85']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。HTML、既存JSON、全時間帯の日本語VTTを確認。
- 問題：HTML本文は共通UI中心、字幕に専門語誤認識あり。成立理由・外国の慣習は話者の推察と明示して記録。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料085.md`。一時HTML削除、cache保持。

## 資料086（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=9nUB_72lS1g
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_86.html "https://www.youtube.com/watch?v=9nUB_72lS1g"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','86']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。既存JSONと日本語VTT全時間帯を確認。
- 問題：約03:00〜06:00に字幕欠落・音楽誤認識が多く、歴史説明などは「一部のみ」。内容全体は判別できるためブラウザー・再生・yt-dlpなし。
- 保存：`results/資料086.md`。一時HTML削除、cache保持。個人名を含むチャンネル名称は省略。

## 資料091（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=_A9OHV_7rYg
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_91.html "https://www.youtube.com/watch?v=_A9OHV_7rYg"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','91']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。既存JSON、スペイン語VTT全編を90秒単位で読み、日本語化。
- 問題：HTML本文は共通UI中心。自動字幕の楕円体名・略語に誤認識があり、定数・厳密な同一性を断定せず。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料091.md`。一時HTML削除、cache保持。冒頭の個人名は転記せず。

## 資料092（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=srtm2H5TgdI
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_92.html "https://www.youtube.com/watch?v=srtm2H5TgdI"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','92']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。既存JSON、スペイン語VTT全時間帯を90秒単位で確認。
- 問題：HTMLは共通UI中心。字幕のひずみ上限・距離・桁数には留保を記し、図の細部は未評価。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料092.md`。一時HTML削除、cache保持。説明欄・自己紹介の個人名は転記せず。

## 資料095（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=L95lydcjLtE
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_95.html "https://www.youtube.com/watch?v=L95lydcjLtE"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','95']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。JSONの説明・チャプターとフランス語VTT全編を確認。
- 問題：登録チャプターが粗いため字幕から細分。略語の誤認識・基準系の互換性などの簡略説明に留保を付した。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料095.md`。一時HTML削除、cache保持。個人名のチャンネル名は省略。

## 資料096（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=lBc85Eb215U
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_96.html "https://www.youtube.com/watch?v=lBc85Eb215U"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','96']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。JSON・フランス語字幕を90秒単位で全編確認。
- 追加確認：初回出力の一部省略に対しStringIOへの再読を試みたが、`reconfigure`非対応で失敗。読解スクリプトに区間フィルターを追加し、同コマンドの引数を `['reader','96','fr-orig','18','24']` として18〜24分を再読、欠落を解消。
- 問題・保存：専門語・最終計算の自動字幕の揺れに留保し、`results/資料096.md` に保存。ブラウザー・再生・yt-dlpなし。一時HTML削除、cache保持。

## 資料098（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=SemhiumsyoA
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v05_98.html "https://www.youtube.com/watch?v=SemhiumsyoA"` → HTTP 200。
- 読解コマンド：`python -I -c "import runpy,sys; sys.argv=['reader','98']; runpy.run_path('notes/session03_kai2_20261021/codex/tmp/batch_v05_read.py',run_name='__main__')"`。既存JSONと英語VTTを90秒単位で全編読解。
- 問題：キャッシュは `v.en-US-orig.vtt` のみで、一覧のポルトガル語音声は未確認。「一部のみ」と字幕の条件を明記。UTMの境界値などの説明には留保を付す。ブラウザー・再生・yt-dlpなし。
- 保存：`results/資料098.md`。一時HTML削除、cache保持。バッチ終了時に共通の一時読解スクリプトも削除し、結果10件とログの見出し・件数を点検。
- 最終点検：PowerShellのパイプで日本語が置換され初回検査が失敗。`$OutputEncoding = New-Object System.Text.UTF8Encoding` と `python -I -X utf8 -c "import sys; exec(sys.stdin.read())"` で再実行し、10件の必須見出し・5〜15段階・つなぎと工夫の点数、ログ10件の順序、一時ファイル残存なしを確認。

