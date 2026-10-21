# batch_v06 操作ログ（2026-10-22）

## 資料099
- 開いたURL：https://www.youtube.com/watch?v=HW6MCUBY56E
- ツール・取得コマンド：PowerShell／curl.exe。`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_99.html "https://www.youtube.com/watch?v=HW6MCUBY56E"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '99']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parserでHTML、jsonでメタデータ、VTT全編を2分区切りで読取。
- 問題：HTML本文はYouTube共通部分のみだがタイトル取得可。キャッシュ字幕で本編を確認できたためブラウザー・yt-dlpは不要。別途ルール読取で標準出力の文字コードエラーが出たため、読取スクリプトはUTF-8出力に固定。
- 保存・後処理：資料099.mdを保存。取得HTMLは削除、cacheは保持。個人名を含むチャンネル名は役割・機関種別で記載。

## 資料101
- 開いたURL：https://www.youtube.com/watch?v=mAHPFEJXQzU
- ツール・取得コマンド：PowerShell／curl.exe。`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_101.html "https://www.youtube.com/watch?v=mAHPFEJXQzU"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '101']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser・json・VTTを使用。
- 問題：二言語同時出力が長く途中省略されたため、同コマンドのargvを `['', '101', 'en-US', '28']` にして後半を再読。英語字幕全編と原語字幕を参照。HTMLはタイトルのみ有効、ブラウザー・yt-dlp不要。
- 保存・後処理：資料101.md保存、取得HTML削除、cache保持。個人チャンネル名は非記載。

## 資料103
- 開いたURL：https://www.youtube.com/watch?v=HQkGRNYKWHo
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_103.html "https://www.youtube.com/watch?v=HQkGRNYKWHo"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '103']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser／json／露・英VTTの2分区切り読取。
- 問題：自動字幕の数値に揺れがあり原語と照合。HTMLはタイトル・共通文のみだがキャッシュで全編確認でき、ブラウザー・yt-dlp不要。
- 保存・後処理：資料103.md保存、取得HTML削除、cache保持。個人チャンネル名は省略。

## 資料104
- 開いたURL：https://www.youtube.com/watch?v=18UGXX3juyg
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_104.html "https://www.youtube.com/watch?v=18UGXX3juyg"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '104']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser／json／露VTT全編を2分区切りで確認。
- 問題：最初はargvにenフィルターを付けたが英語字幕がなく、フィルターを外して原語字幕を読取。数値の脱落・図示未確認の限界を結果に明記。ブラウザー・yt-dlp不要。
- 保存・後処理：資料104.md保存、取得HTML削除、cache保持。

## 資料105
- 開いたURL：https://www.youtube.com/watch?v=DPfFm7kXaus
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_105.html "https://www.youtube.com/watch?v=DPfFm7kXaus"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '105']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser／json／ウクライナ語VTTを使用。
- 問題：説明欄の03:25への訂正を結果に反映。図郭文字の字幕誤認あり。説明欄の連絡先は成果物に転記せず。HTMLタイトルとcacheで確認できたためブラウザー・yt-dlp不要。
- 保存・後処理：資料105.md保存、取得HTML削除、cache保持。

## 資料108
- 開いたURL：https://www.youtube.com/watch?v=5pFcxTRnq9o
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_108.html "https://www.youtube.com/watch?v=5pFcxTRnq9o"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '108']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser／jsonでタイトル・説明欄・7章を確認。
- 問題：cacheに字幕なし。空ではなくメタデータ・全章の時刻があるため、指定に従い説明欄とチャプターで代用し「一部のみ」と記載。導入方法・つなぎ理由・図などは推測で埋めない。ブラウザー・yt-dlp不要。
- 保存・後処理：資料108.md保存、取得HTML削除、cache保持。

## 資料109
- 開いたURL：https://www.youtube.com/watch?v=TP5zcVf8ouc
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_109.html "https://www.youtube.com/watch?v=TP5zcVf8ouc"` → HTTP 200。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '109']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。html.parser／json使用。cacheは存在するが字幕・chaptersなし、説明欄に授業目次なし。
- ブラウザー：`cua.createBrowserTab('chrome', URL, {sessionName:'📚 講義調査'})`、`cua.getTab({url:URL},{browser:'chrome'})`、`browser109.tabs.get('552231637')`、`target109.playwright.domSnapshot()`を試行。作成時Detached、読取時Debugger unattachedで本文・コメントを読めず、NG（一部のみ）として保存。
- タブ後処理：通常の `target109.close()` も失敗。management capabilityの説明を読み、対象URLの `tabs.query` でID確認後 `cleanup109.tabs.remove(552231637)` で閉鎖。`cua.listTabs({browser:'chrome'})` が空配列となったことを確認。
- 保存・後処理：資料109.md保存、取得HTML削除、cache保持。追加URL探索・動画再生なし。説明欄の個人名は非記載。

## 資料110
- 開いたURL：https://www.youtube.com/watch?v=8vXO03A-gB8
- ツール・取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_v06_110.html "https://www.youtube.com/watch?v=8vXO03A-gB8"` → HTTP 200。ただし動画名のないYouTube共通HTML。
- 読取コマンド：`python -I -c "import sys; sys.argv=['', '110']; exec(compile(open('notes/session03_kai2_20261021/codex/tmp/batch_v06_read.py',encoding='utf-8').read(), 'reader', 'exec'))"`。cacheは仮タイトルだけで実質空。再取得JSONもpython -I -c／jsonで確認。
- 再取得コマンド：`yt-dlp --no-update --no-playlist --skip-download --ignore-no-formats-error --write-info-json --write-auto-sub --write-sub --sub-langs ".*-orig,ja,en" --sub-format "vtt/srv3/best" --extractor-args "youtube:player_client=ios" --sleep-subtitles 3 -o "notes/session03_kai2_20261021/codex/tmp/batch_v06_110" "https://www.youtube.com/watch?v=8vXO03A-gB8"` → Private video、字幕なし。終了コード0でも取得成功とは扱わず。
- ブラウザー：`cua.createBrowserTab('chrome',URL,{sessionName:'📚 講義調査'})` のAX本文で「この動画は非公開です」を確認。`tab110.close()`後、managementの対象URL `tabs.query` が空配列で閉鎖確認。NGとして保存。
- 保存・後処理：資料110.md保存、取得HTML・再取得JSON・本バッチ読取スクリプトを削除、cache保持。代替URL探索・動画再生・git操作なし。
