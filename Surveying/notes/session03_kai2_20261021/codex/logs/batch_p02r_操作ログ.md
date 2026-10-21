# batch_p02r 操作ログ

## 資料019（2026年10月22日）
- 開いたURL：https://gge.ext.unb.ca/Pubs/LN34.pdf（HTTP 200、全40ページ）。
- 使ったツール：PowerShell、curl.exe、python -I、PyMuPDF（fitz）、apply_patch。ブラウザーは使用せず。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p02r_19.pdf "https://gge.ext.unb.ca/Pubs/LN34.pdf"`
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p02r_19.pdf'); print('\n'.join('PDF '+str(i+1)+': '+' | '.join([s.strip() for s in p.get_text().splitlines() if s.strip()][:3]) for i,p in enumerate(d)))"`。続けて全ページ本文を前半9ページと残り31ページに分けて抽出し、目次全文（PDF 4〜5）も確認。
- 起きた問題：初回出力がcp932のUnicodeEncodeErrorで停止し、標準出力のUTF-8設定で解消。保存時もPowerShellからPythonへの日本語受け渡しで文字化け・保存エラーが起きたため、apply_patchで保存。数式の文字認識には乱れがあるが構成・本文は判別可能。
- 保存・後処理：`results/資料019.md`を保存。`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02r_19.pdf'`で取得PDFを読了後に削除。cacheは変更せず。

## 資料020（2026年10月22日）
- 開いたURL：https://opac.geologie.ac.at/ais312/dokumente/GM64.pdf（HTTP 200、全57ページ）。
- 使ったツール：PowerShell、curl.exe、python -I、PyMuPDF（fitz）、apply_patch。ブラウザーは使用せず。
- 取得コマンド：`curl.exe -L -s -S -A "Mozilla/5.0" -w "%{http_code}" -o notes/session03_kai2_20261021/codex/tmp/batch_p02r_20.pdf "https://opac.geologie.ac.at/ais312/dokumente/GM64.pdf"`
- 読取コマンド：`python -I -c "import sys,fitz; sys.stdout.reconfigure(encoding='utf-8'); d=fitz.open('notes/session03_kai2_20261021/codex/tmp/batch_p02r_20.pdf'); print('\n'.join('PDF '+str(i+1)+': '+' | '.join([s.strip() for s in p.get_text().splitlines() if s.strip()][:3]) for i,p in enumerate(d)))"`。目次全文（PDF 3）・冒頭9ページ全文・以後の本文説明行を抽出。出力省略されたPDF 22〜41は別コマンドで再取得して確認。
- 起きた問題：式・一部単語に文字認識の乱れあり。大きな抽出出力はツールで中間部分が省略されたため範囲を絞って再読。一覧の「教科書章」と異なり冊子全体だったが、題名・巻号は一致。著者個人名・奥付の連絡先は成果物に転記せず。
- 保存・後処理：`results/資料020.md`を保存。`Remove-Item -LiteralPath 'notes/session03_kai2_20261021/codex/tmp/batch_p02r_20.pdf'`で取得PDFを読了後に削除。cacheは変更せず。
