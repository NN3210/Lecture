あなたは測量学の講義資料の作図担当です。作業ディレクトリは Surveying/（このディレクトリ）です。対話はできないので、質問せずに最後まで作業し、終わったら報告文だけを出力してください。

## やること

1. `materials/slides/第05回_トラバース測量I/diagrams/README.md` を読む。これが 12 点の図の仕様書で、数値は検算済みです。
2. 既存の `scripts/draw_session03_figures.py` を読み、その流儀（フォント選択、rcParams、4 色、save() の検査、canvas()、角丸箱・矢印の描き方、contact sheet と validation.json の作り方）を踏襲して、`scripts/draw_session05_figures.py` を新規に書く。第3回のスクリプトは変更しない。
3. 実行して、`materials/slides/第05回_トラバース測量I/diagrams/` に 12 点の SVG と PNG（dpi 180）を出力する。`notes/session05_figures/contact_sheet.png` と `notes/session05_figures/validation.json` も作る。
4. 出力した PNG を 1 枚ずつ画像として開いて目で確認し、文字の重なり・はみ出し・矢印の向きの誤り・座標軸の向きの誤り・角の弧の位置の誤りがあれば直して再実行する。全図が仕様どおりで、投影しても読める状態になるまで繰り返す。
5. 最後に、作った図の一覧と、仕様から変えた点（あれば理由）を日本語で報告する。

## 守ること

- git の操作（add / commit / push / stash / checkout / reset など）は一切しない。
- 書き換えてよいのは `scripts/draw_session05_figures.py`、`materials/slides/第05回_トラバース測量I/diagrams/` 配下、`notes/session05_figures/` 配下だけ。他のファイルは変更しない。
- 標準ライブラリ、numpy、matplotlib、Pillow だけを使う。LaTeX は使わない（matplotlib の mathtext は可）。
- 座標の向きは測量の約束：X 軸が上＝北、Y 軸が右＝東、方向角は X 軸（北）から右回り。数学の向きと混同しない。方向角の弧は北から右回りに、内角の弧は隣接する 2 辺の間に、本当にその角度を表すように描く。
- 図の数値は README の表の値をそのまま使う。
- 文字は 12〜16 pt。下段用は 12 × 2.8〜3.4 インチ、全面用は 12 × 5.0〜5.3 インチ。
- 文字の重なりを避ける。箱の中の文章は短く、必要なら改行する。
- 個人名・企業名・製品名・ロゴは描かない。
- スクリプトには日本語のコメントと docstring を書く。
