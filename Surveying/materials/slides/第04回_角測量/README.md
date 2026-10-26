# 第4回 角測量

高校数学までを前提に、「校庭の2本の杭の開きを測る」場面から角測量を学ぶ教材です。授業計画を先に保存し、解説HTMLを作り、その説明をPowerPointへ展開しました。

## 教材

| ファイル | 用途 |
| --- | --- |
| [lesson_plan.md](lesson_plan.md) | 90分授業の計画・到達目標・時間配分 |
| [explanation.html](explanation.html) | 高校生向けの解説。図、途中式、3つの操作、開閉できる解答 |
| [slides.pptx](slides.pptx) | 編集可能なPowerPoint。60枚、全枚に発表者ノート |
| [slides.pdf](slides.pdf) | PowerPoint本体で書き出した配布用PDF |
| [slides.html](slides.html) | スライド60枚をブラウザで閲覧 |
| [slides.md](slides.md) | スライド本文・表・ノートを含むMarp原稿 |
| [DECK.md](DECK.md) | 図と文字のデザイン方針 |
| [演習問題](../../exercises/第04回_角測量/exercise.md) | 25分の手計算演習 |
| [演習解答](../../exercises/第04回_角測量/exercise_answers.md) | 途中式・採点基準 |

HTMLはファイルを開くだけで利用できます。解説HTMLは画像・フォント・計算処理を外部サービスに依存せず、ネット接続なしで動きます。スライド閲覧HTMLは隣の `preview/` フォルダーと一緒に保管してください。

## 授業での使い方

1～20枚：角の意味、度分秒、器械の準備、正反観測。
21～40枚：方向法、野帳の点検、北の区別、鉛直角と高度定数。
41～48枚：偏心補正とTSの自動機能。
49～52枚：演習25分（方向法15分、偏心10分）。53～54枚：出口問題と次回への接続。
55～60枚：復習用解答。授業中の演習より後に使います。

数値は教材用の架空値です。許容値は授業内の仮定（倍角差8″以下、観測差5″以下、各帰零差の絶対値6″以下）で、公共測量の規程値ではありません。B方向の観測差6″は基準を超えるため、平均角を成果に採用せず再測と判断します。

偏心例の座標は仕組みを理解するための既知値です。実際の観測では、偏心距離・方向と目標への観測角・距離から中心値を復元します。図では偏心を誇張し、計算は正しい座標値に基づいています。

## 編集と再生成

詳しい説明は `explanation.html`、投影用の短い文は `../../../notes/session04/slides_part1.json` ～ `slides_part3.json` にあります。内容を直すときは両者をそろえてください。`slides.md` はJSONから生成するため、Markdownだけの変更は再生成時に反映されません。数式・文字・幾何図・表はPPTX内で編集できます。

`build_deck.mjs` と `diagram_helpers.mjs` が生成元です。Node.jsと `@oai/artifact-tool` を利用します。ライブラリ位置は `ARTIFACT_TOOL_PATH` 環境変数、またはローカルの標準ランタイムから解決します。Surveyingフォルダーで以下を実行します。

```powershell
node materials/slides/第04回_角測量/build_deck.mjs --input-dir notes/session04 --output-dir materials/slides/第04回_角測量/build/revised --render false --marp materials/slides/第04回_角測量/slides.md
python -X utf8 scripts/check_exercise_04.py
```

PowerPoint本体でのPDF・画像出力には `notes/session04/export_powerpoint.py` を使います。既存のプレゼンテーションを変更せず、指定ファイルだけを読取専用で開きます。ライブラリの簡易PNG出力とPowerPoint表示に差がある場合、PowerPoint出力を採用します。

完成状態の検証記録は [final_review.md](../../../notes/session04/final_review.md)、GPT-5.6の20担当の分担は [agent_manifest.md](../../../notes/session04/agent_manifest.md) を参照してください。
