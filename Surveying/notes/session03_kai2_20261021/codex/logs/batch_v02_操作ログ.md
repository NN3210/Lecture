# batch_v02 操作ログ

## 資料042（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=3Zse9qqmxVU
- 使用ツール：cua_repl（Chrome・DOM・h1・自動再生停止）、exec_command、apply_patch。
- 実行コマンド：`python -I notes/session03_kai2_20261021/codex/tmp/batch_v02_read.py 42 4500`、続いて同コマンド末尾に`60`を指定して1分区切りで再読。
- 読んだ範囲：メタデータと全字幕。チャプターなしのため字幕から段階を区分。
- 問題：広告自動再生を停止。自動字幕の専門語・数字に誤認識があるため限界を明記。実在確認OK。

## 資料041（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=Y504XVm-78E
- 使用ツール：cua_repl（Chrome・DOM・自動再生停止・h1）、exec_command、apply_patch。
- 実行コマンド：`python -I notes/session03_kai2_20261021/codex/tmp/batch_v02_read.py 41 4000`。
- 読んだ範囲：メタデータ・全章立て・2分区切りの全字幕。数式の画面表示は未確認。
- 問題：自動再生を停止。自動字幕の記号誤認識に留意し、式の精密転記を避けた。一覧の前回番号は未確認として区別。実在確認OK。

## 資料040（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=HtSuoqRqgeE
- 使用ツール：cua_repl（Chrome・DOM・自動再生停止・h1）、exec_command、apply_patch。
- 実行コマンド：`python -I notes/session03_kai2_20261021/codex/tmp/batch_v02_read.py 40 3500`。
- 読んだ範囲：メタデータと章立て、全字幕を2分ごとに通読。映像・数式の画面表記は未確認。
- 問題：自動再生を停止。自動字幕に数式・専門語の誤認識あり、数値解は転記せず。実在確認OK。

## 資料039（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=OLKvmGTczCE
- 使用ツール：cua_repl（Chrome移動・AX確認・自動再生停止・h1取得）、exec_command、apply_patch。
- 実行コマンド：`python -I notes/session03_kai2_20261021/codex/tmp/batch_v02_read.py 39 2200`。
- 読んだ範囲：キャッシュの説明・章立てと、2分区切りの全字幕。映像は調査に使っていない。
- 問題：広告が自動再生されたため停止。作者欄は個人名を省略。実在確認OK、追加ダウンロードなし。

## 資料038（2026-10-22）
- 開いたURL：https://www.youtube.com/watch?v=PICwxT0fTHQ
- 使用ツール：cua_repl（Chromeで作成、AX状態確認、自動再生の停止）、exec_command、apply_patch。
- 実行コマンド：`python -I notes/session03_kai2_20261021/codex/tmp/batch_v02_read.py 38 1300`。24〜30分は同コマンドの引数を900にしてSelect-Stringで追加抽出。
- 読んだ範囲：キャッシュのメタデータ、全章立て、全時間帯を2分ごとに抽出した英語字幕の抜粋。長い窓の中間は省略（字幕一部のみ精読）。
- 問題：初回は端末のcp932出力で失敗したため標準出力をUTF-8に修正。ページの自動再生は停止（約5秒）；再生して内容を調査していない。実在確認OK。PDF・字幕の新規ダウンロードなし。
