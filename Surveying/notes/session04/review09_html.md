# 第4回 `explanation.html` 実動検証（担当09）

- 実施日: 2026-10-27
- 対象: `materials/slides/第04回_角測量/explanation.html`
- 方法: Python Playwright + ローカル `file:` URL + Chrome headless
- 自動確認: 35項目中24項目合格（欠陥を期待どおり検出した項目はテスト上 `FAIL` として記録）
- 生データ: `html_preview/results.json`

## 結論

表示のレスポンシブ対応、入力ラベル、操作1の通常計算、解答detailsの手動開閉と `beforeprint` による展開は動作した。一方、操作3はスライダーを動かしても表示が更新されない重大な実装不具合がある。操作1・2は空欄や不正範囲を一部受理し、操作2は正反として成立しない同値も受理する。専用resetはない。印刷時にsummaryを隠すCSSもChrome上で効いていない。

## 欠陥・懸念

### 重大: 操作3が動作しない

- 0 m、10 mへスライダー値を変更して `input` イベントを発火しても、表示は `1.0 m` / `−0.572939°` のまま。
- 原因は末尾のイベント登録が `addEventListener('input', ecc)` であり、定義済み関数名 `eccentric` を渡していないためと考えられる。`ecc` は同名idの要素として解決され、エラーを出さず更新も行われなかった。
- 図のDOMも1 m固定で、操作前後に変化しない。数値だけを直すのか図も連動させるのか、教材として意図を明記した方がよい。

### 高: 操作2の入力検証不足

- 空欄は `Number('') === 0` のため拒否されず、正0°・反220°として処理され平均20°を表示。
- 正10°・反10°（180°離れていない）も平均10°として受理。
- 正−1°、正360°も受理。inputにも `min` / `max` がない。
- 「反はおよそ正＋180°」という説明に対し、差が妥当かを判定する許容範囲がない。

### 中: 操作1の空欄を0°として受理

- 基準読定を空欄にすると、目標20°に対して `20－0＝20°` と表示する。
- `Number.isFinite(Number(value))` だけでは空文字を除外できないため、空文字を先に検査する必要がある。

### 中: 操作2の初期表示とクリック後表示が不一致

- HTML初期表示: `平均40.000834°`
- ボタン押下後: `平均40.000833°`
- DMS表示はいずれも約40°00′03″。内部値40.0008335の小数6桁丸めがJavaScriptの2進浮動小数点と `toFixed(6)` に依存している。

### 中: 印刷CSSでsummaryが残る

- `beforeprint` を手動発火すると3件のdetailsはすべて `open=true` になった。
- しかし `emulate_media('print')` 後も3件のsummaryの算出displayはすべて `block` で、期待した `display:none` にならなかった。印刷プレビュー画像にもsummaryが残る。

### 軽微: 専用resetなし

- `button[type=reset]` / `input[type=reset]` は0件。
- ページ再読込では、操作1=350/20、操作2=40.001667/220、操作3=1へ戻ることを確認した。

## 合格した確認

- 幅320 / 768 / 1440 pxでページ全体の横スクロールなし（`scrollWidth === clientWidth`）。
- 320 pxの表は意図どおり `.wide` 内部で横スクロールし、ページ本体はあふれない。
- 5入力すべてに `label[for]` がある。
- 3結果領域すべてに `role=status` と `aria-live=polite` がある。
- 操作1: 350→20=30°、0→359.999=359.999°、359.999→0=0.001°、20→20=0°、360°拒否。
- 操作2: 0/180、359.999/179.999の境界例は期待値どおり。
- 解答detailsは3件、初期状態では閉じ、summaryクリックで開く。
- ページ実行中のuncaught JavaScript error / console errorは0件。

## 再実行

```powershell
python notes\session04\test_html.py
```

スクリーンショットは `notes/session04/html_preview/viewport_320.png`、`viewport_768.png`、`viewport_1440.png`、`print_details.png` に保存した。
