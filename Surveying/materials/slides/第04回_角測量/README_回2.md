# 第4回 角測量「回2」— 授業用セット

Claude Code と Codex が、初版への批評・反論・修正・教材化後の再批評を行って制作した改訂版です。初版は上書きしていません。

## 授業で使うファイル

| ファイル | 用途 |
|---|---|
| [slides_回2.pptx](slides_回2.pptx) | **授業で上映する編集可能なPowerPoint**。本編50枚＋通常非表示の付録13枚。全63枚に発表者ノート |
| [slides_回2.pdf](slides_回2.pdf) | 本編50枚のPDF |
| [slides_回2_付録付き.pdf](slides_回2_付録付き.pdf) | 解答・補足を含む63枚のPDF |
| [slides_回2.html](slides_回2.html) | ブラウザで上映・閲覧。隣の `preview_回2/` と一緒に保存 |
| [lesson_plan_回2.md](lesson_plan_回2.md) | 90分の授業計画・確認問題・指導上の注意 |
| [explanation_回2.html](explanation_回2.html) | 高校数学までで読める解説。3つの操作、途中式、開閉式の解答付き |
| [演習問題PDF](../../exercises/第04回_角測量/exercise_回2.pdf) | 授業中に配るA4・2ページ。25分・10点 |
| [別紙解答PDF](../../exercises/第04回_角測量/exercise_answers_回2.pdf) | 解答・採点基準、A4・2ページ |

問題と解答のHTML版も同じフォルダーにあります。解説HTMLは演習の解答を含むため、復習用として配布してください。授業中の問題配布には演習問題PDFを使います。

## 上映と時間配分

PowerPointを開き、通常のスライドショーを開始します。51〜63枚は非表示にしてあるため、本編50枚で終わります。授業後の解説で付録を使う場合は、目的のページへ移動するか非表示を解除してください。

- 0〜5分：前回の要点・診断の問い（1〜5枚）
- 5〜29分：読む・据える・正反で減らす（6〜23枚）
- 29〜49分：方向法・鉛直角の点検（24〜37枚）
- 49〜58分：偏心・TS（38〜44枚）
- 58〜60分：予備・配布準備
- 60〜85分：方向法15分、偏心10分（45〜47枚）
- 85〜90分：まとめ・後視反転・出口問題（48〜50枚）

これは設計上の時間配分です。実際の学級での所要時間は未測定です。演習開始を60分にそろえ、補足を標準時間へ追加しない運用にしています。

## 初版からの主な改善

1. 生読定は正r・反l、零方向差引き後は正の結果p・反の結果qに統一。
2. 「較差＝器械誤差の2倍」「一致すれば正しい」という誤解を反例で防止。
3. 講義と演習で仮基準を統一（倍角差10″以下・観測差8″以下）。初版の8″・5″とは別なので資料を混ぜない。
4. 偏心デモはO直角、演習はE直角。補正の符号を図から判断する問題へ変更。
5. 次の測点で後視が180°反転する橋渡しを追加。
6. ラジアン・一般偏心式を補足へ移し、演習25分と予備2分を確保。

数値・許容値は授業用の架空設定で、公共測量の規程値ではありません。Bは平均62°14′15.5″を採用、Cは倍角差16″で再測です。

## 原稿と再生成

正本は計画、解説HTML、および `../../../notes/session04/build_kai2_content.py` で生成する `../../../notes/session04/kai2/slides_part1.json` です。`slides_回2.md` はJSONからの書き出しで、単独で編集してもPPTXへ反映されません。文字・図形・表はPPTX内でも編集できますが、再生成前には手編集を原稿へ戻してください。

生成器は `build_kai2.mjs`、新しい幾何図は `diagram_kai2.mjs`。初版の図からの調整は `prepare_kai2_builder.py` が分離した `diagram_kai2_base.mjs` に反映します。Node.jsと既設の `@oai/artifact-tool` を使用。PDF・画像はMicrosoft PowerPointで出力します。

再生成は原稿生成 → 専用生成器の準備 → PPTX候補作成 → 付録非表示 → 最終検証 → PowerPoint書出しの順です。既存の最終PPTXと検証レポートは上書きせず、別名で保存してから実行します。

```powershell
python -X utf8 notes/session04/build_kai2_content.py
python -X utf8 notes/session04/prepare_kai2_builder.py
node materials/slides/第04回_角測量/build_kai2.mjs --input-dir notes/session04/kai2 --output-dir notes/session04/kai2/build --pptx notes/session04/kai2/build/candidate.pptx --marp materials/slides/第04回_角測量/slides_回2.md --render false
python -X utf8 notes/session04/hide_kai2_appendix.py
node notes/session04/finalize_kai2.mjs
python -X utf8 notes/session04/export_kai2_final.py
python -X utf8 notes/session04/package_kai2.py
```

配布問題は `build_kai2_worksheets.py`、HTML操作・印刷検証は `test_kai2_html.py`、数値は `kai2_numeric_check.py`。検証記録は [回2最終レビュー](../../../notes/session04/kai2_final_review.md) にまとめています。
