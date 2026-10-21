# batch_v01 操作ログ

## No.21（2026-10-22）
- 開いたURL：https://fac.iitg.ac.in/abd/nptel1.html
- 使ったツール：cua_repl／Chrome。ページを開き、アクセシビリティ本文と座標スクロールで講義一覧を確認。
- 実行したコマンド：この資料の取得用シェルコマンドはなし（指定URLはYouTubeではなく講義一覧ページ）。
- 起きた問題：Module 2の講義題名3件のみ掲載。動画内部の順序・理由は取得できないため、一部のみと記録。別URLは開いていない。
- 保存先：results/資料021.md。実在確認OKは講義一覧の存在を意味し、動画本体の確認とは区別。

## No.29（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=5MVfc33PGMk
- 使ったツール：cua_repl／Chrome、exec_command。タイトル確認後にyt-dlpを実行し、失敗後に説明欄を展開。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_29" "https://www.youtube.com/watch?v=5MVfc33PGMk"`
- 起きた問題：字幕取得HTTP 429。旧バージョン・JS runtime未検出の警告あり。info.json未取得。広告が自動再生されたため一時停止し、本編は再生操作していない。
- 代用：説明欄と全10自動生成チャプター（最終照合で「すべて表示」を開き、21:41・23:31の2章を追記）。文字起こし表示を試したがパネルを取得できず。総尺未確認として保存。

## No.30（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Bx4RLXRWpgA
- 使ったツール：cua_repl／Chrome、exec_command。ページを開いて自動再生を停止、タイトル確認後にyt-dlp、失敗後に説明欄・コメントを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_30" "https://www.youtube.com/watch?v=Bx4RLXRWpgA"`
- 起きた問題：字幕HTTP 429、info.json未取得。旧版・JS runtime警告あり。字幕本文の代わりに5チャプターを使用。表示されたコメントから追加目次は取得できず。
- 確認結果：総尺9分52秒、実在確認OK。「すべて表示」で自動生成の全5章を照合。一部のみと明記して資料030.mdに保存。

## No.31（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=dgMAuuuJ6r4
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_31" "https://www.youtube.com/watch?v=dgMAuuuJ6r4"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：説明欄と「すべて表示」で全10自動生成チャプターを確認。折り畳み表示の8件より後に42:46・58:02の2章が存在。総尺59分56秒。 一部のみと明記し、results/資料031.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.32（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Z41Dt7_R180
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_32" "https://www.youtube.com/watch?v=Z41Dt7_R180"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：説明欄のMinute Markers全9項目を使用。「すべて表示」は存在せずクリック失敗。冒頭広告を一時停止。総尺未確認。 一部のみと明記し、results/資料032.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.33（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=iagP0CqBAAg
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_33" "https://www.youtube.com/watch?v=iagP0CqBAAg"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：全6自動生成チャプターと説明欄を確認。総尺21分32秒。 一部のみと明記し、results/資料033.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.34（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=dX6a6kCk3Po
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_34" "https://www.youtube.com/watch?v=dX6a6kCk3Po"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：全13自動生成チャプターを確認。折り畳みの8章以降に格子・短距離変化・経路・ソフト2件が続く。総尺16分16秒。 一部のみと明記し、results/資料034.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.35（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=rUObSHQ6WiY
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_35" "https://www.youtube.com/watch?v=rUObSHQ6WiY"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：作者説明欄の全8項目と全チャプターを照合。広告を停止し、総尺は確認できず最終章開始19:14を記録。 一部のみと明記し、results/資料035.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.36（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=y33_I5xRynQ
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_36" "https://www.youtube.com/watch?v=y33_I5xRynQ"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：作者目次9項目と全章を照合。最後の航空・MSLの章は3:00。総尺3分19秒。 一部のみと明記し、results/資料036.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。

## No.37（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=FPKz-kMKX3Y
- 使ったツール：cua_repl／Chrome、exec_command。ブラウザーで実在確認、自動再生を停止し、yt-dlp失敗後に説明欄・チャプターを確認。
- 実行したコマンド：`yt-dlp --skip-download --write-info-json --write-auto-sub --write-sub --sub-lang "ja,en,en-US,en-GB,de,es,fr,pt,id,ru,uk,tr,zh,ko" --sub-format vtt -o "notes/session03_kai2_20261021/codex/tmp/batch_v01_37" "https://www.youtube.com/watch?v=FPKz-kMKX3Y"`
- 起きた問題：字幕取得HTTP 429で失敗、info.json・VTT未取得。旧版・JS runtime未検出・impersonation未対応の警告あり。
- 代用・保存：全11自動生成チャプターを確認。折り畳み表示後に注意点16:29・変換23:45・まとめ26:18が続く。総尺28分13秒。 一部のみと明記し、results/資料037.mdに保存。tmpの該当ファイルを削除（未生成なら削除対象なし）。
