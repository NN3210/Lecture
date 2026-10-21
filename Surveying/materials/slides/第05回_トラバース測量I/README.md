# 第05回 トラバース測量 I

農業農村工学系の学部講義、90 分。講義計画（`materials/lecture_plan_13.md` の第 5 回）に沿って、トラバースの種類と選点、測角誤差の許容と等配分、方向角の計算（交角法・偏角法）、緯距・経距、座標の逆計算と象限判定、TS の座標観測モードまでを扱い、25 分の手計算テストで到達度を確かめる。日本語の Marp 原稿 `slides.md`（64 枚、発表者ノート付き）を正本とし、そこから編集可能な PowerPoint（`slides.pptx`）、PDF（`slides.pdf`）、HTML（`slides.html`）を作る。

第 4 回（距離と角の観測）の資料はまだこのリポジトリにないため、冒頭の「前回の解答」の代わりに、第 3 回の方向角・順計算と第 4 回で扱う角の観測の要点を復習として置いた。

## 内容と構成

| 区分 | スライド番号 | 枚数 | 時間 |
| --- | --- | ---: | --- |
| 表紙、前回までの復習、到達目標、今日の流れ | 1〜5 | 5 | 0〜5 分 |
| 5-1 トラバース測量とは（閉合・結合・開放、点検できる理由、農業農村工学での用途、選点） | 6〜13 | 8 | 5〜12 分 |
| 5-2 内角の和と測角誤差の調整（(n−2)×180°、許容 σ√n、等配分、例題、流れの整理、結合トラバースの測角誤差） | 14〜23 | 10 | 12〜22 分 |
| 5-3 方向角の計算（交角法、一周して戻る検算、360° の整え、偏角法、筆算の型） | 24〜36 | 13 | 22〜36 分 |
| 5-4 緯距・経距（定義、象限と符号、例題、合計がほぼ 0 になる理由、関数表で解く） | 37〜43 | 7 | 36〜45 分 |
| 5-5 座標の逆計算と象限判定（逆計算の式、象限表、4 象限の例題、ΔX=0 の扱い、atan2） | 44〜51 | 8 | 45〜53 分 |
| 5-6 TS の座標観測モード（内部計算、出力の意味、後視の誤り、精度管理と倫理） | 52〜55 | 4 | 53〜58 分 |
| 5-7 手計算テスト（問 1・問 1 の図・問 2、計算中のチェック、提出前の確認） | 56〜60 | 5 | 58〜85 分 |
| 5-8 まとめ・次回予告 | 61〜63 | 3 | 85〜90 分 |
| 付録 出典 | 64 | 1 | （配布のみ） |
| 合計 | 1〜64 | 64 | 90 分 |

各節の末尾に「ここまでの確認」を置き、5-3・5-5 には測量士補試験で問われる型の表を入れた。数値例は 4 点閉合トラバース（A→B→C→D→A、T_AB = 62°30′00″、辺長 120.000・95.000・117.015・102.977 m）で統一し、`scripts/check_exercise_05.py` で検算してある。座標の向きは測量の約束（X 軸が北、Y 軸が東、方向角は北から右回り）で、ΔX = S cos T、ΔY = S sin T。

## ファイル

- [スライド原稿（Marp）](slides.md)、[PPTX](slides.pptx)、[PDF](slides.pdf)、[HTML](slides.html)
- 本文中の数式 21 式は、PowerPoint で編集できる Office 数式（OMML）。KaTeX の MathML を Office 同梱の `MML2OMML.XSL` で変換した（`build/maths.json`、`build/math-validation.json`）
- [図の作図指示書](diagrams/README.md) と概念図 12 点（`diagrams/*.svg` が正本、`*.png` がスライド埋め込み用）。Codex（gpt-6-astra）が `scripts/draw_session05_figures.py` で描いた。点検記録は [notes/session05_figures/](../../../notes/session05_figures/)（`contact_sheet.png`、`validation.json`）
- 概念イラスト 3 点（`illustrations/*.png`：表紙、5-1 トラバースの折れ線、5-6 TS の座標観測）と [生成プロンプトの記録](illustrations/生成プロンプト.md)。Codex（gpt-6-astra）の組み込み画像生成で作った文字なしの概念画で、写真や実測データではない
- [手計算テスト（配布用）](../../exercises/第05回_トラバース測量I/exercise.md)、[模範解答・採点基準](../../exercises/第05回_トラバース測量I/exercise_answers.md)
- [検算スクリプト](../../../scripts/check_exercise_05.py)（講義の数値例と演習の答を再計算する）
- `preview/`：PowerPoint から書き出した確認用 PNG（1280×720）

手計算テストは問 1（5 点閉合トラバースの測角誤差の調整、方向角、緯距・経距の一部、6 点）と問 2（2 点の座標から距離と方向角、4 点）の計 10 点、25 分、関数電卓使用可。解答ファイルは学生用配布物に添付しない。

## 作り直し方

リポジトリの `Surveying/` で実行する。Windows + Microsoft 365（PowerPoint と `MML2OMML.XSL`）、Python（python-pptx、lxml、matplotlib、Pillow）、Node.js（KaTeX は `npx` のキャッシュから自動で探す）が要る。

```powershell
python scripts/draw_session05_figures.py            # 概念図 12 点（diagrams/ と notes/session05_figures/）
python scripts/build_session05.py                   # slides.md → slides.pptx（Office 数式入り）
powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx "materials/slides/第05回_トラバース測量I/slides.pptx"   # PDF と preview/
npx @marp-team/marp-cli@4.1.2 "materials/slides/第05回_トラバース測量I/slides.md" -o "materials/slides/第05回_トラバース測量I/slides.html"
```

`build_session05.py` は `scripts/md2pptx.py` の Builder を継承し、画像つきのスライドの配置（残りの高さに図を収める、表の折り返しを見込んだ行高さ、全段落への ja-JP と句読点のぶら下げの指定で行頭の「。」を防ぐ）と、数式の仮文字列を `scripts/katex_mathml.mjs`（KaTeX → MathML）と `scripts/omml_equations.py`（MathML → OMML、`mc:AlternateContent` で TeX 原文の代替を添付）で Office 数式に置き換える処理を足したもの。`--no-omml` で数式を Unicode 文字列にした版も作れる。イラストは `notes/session05_figures/codex_prompt_illustrations.md` の指示で Codex に生成させた。
