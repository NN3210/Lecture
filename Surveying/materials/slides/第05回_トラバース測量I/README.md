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

## 改2（2026-10-22）：段階的に飲み込める構成への改訂

`slides.md`（改1、64 枚）を学生が段階的に飲み込めるよう組み直した版が `slides_改2.md`（77 枚）で、`slides_改2.pptx`・`slides_改2.pdf`・`slides_改2.html` はそこから作る。改1 は残してあり、改2 と並存する。

改2 で変えたこと：

- 冒頭に 5-0「今日の一本の筋」（角を測る → 角を整える → 向きにする → 成分にする → 座標にする、の 5 段）を置き、各節の入口で「今どの段か」を示す橋渡しの枚を足した。
- 各節を「問い → 絵で見る → 数字で追う → ここまでの確認」の順にそろえ、公式を出す前に体の動き（振り返る・右に回る・一周分を引く）や具体例で入るようにした。数値例は改1 と同じ 4 点閉合トラバースで統一。
- 発表者ノート（HTML コメント）を全枚で書き直し、具体例・つまずき例・言い回しを含む語りにした。
- 概念イラスト 7 点を Codex（gpt-6-astra）の組み込み画像生成で追加した（下表）。数値の表は、生成画像に文字を入れると崩れるため、Markdown の表のままにしてある。

| 区分 | スライド番号 | 枚数 |
| --- | --- | ---: |
| 表紙、5-0 今日の一本の筋、復習、到達目標、今日の流れ | 1〜7 | 7 |
| 5-1 トラバース測量とは | 8〜15 | 8 |
| 5-2 内角の和と測角誤差の調整 | 16〜28 | 13 |
| 5-3 方向角の計算（交角法を 3 ステップで、偏角法、筆算の型） | 29〜45 | 17 |
| 5-4 緯距・経距 | 46〜54 | 9 |
| 5-5 座標の逆計算と象限判定 | 55〜63 | 9 |
| 5-6 TS の座標観測モード | 64〜68 | 5 |
| 5-7 手計算テスト | 69〜73 | 5 |
| 5-8 まとめ・次回予告 | 74〜76 | 3 |
| 付録 出典 | 77 | 1 |

改2 で追加したイラスト（`illustrations/*.png`、1600×900、文字なし。生成の記録は [生成プロンプト.md](illustrations/生成プロンプト.md) の「改2 追加分」、指示と点検は [notes/session05_kai2_figures/](../../../notes/session05_kai2_figures/)）：

| ファイル | 使う枚 | 何を見せるか |
| --- | --- | --- |
| `five_steps_ladder.png` | 2（5-0） | 角から座標までの 5 段の階段。今日はその真ん中 3 段 |
| `tolerance_gate.png` | 16（5-2） | 許容内なら等分、超えたら器械へ戻って再測 |
| `turn_around_180.png` | 31（5-3） | 振り返れば方向角は 180° 違う |
| `three_step_turn.png` | 33（5-3） | 振り返る → 右に回る → 北からの弧を読む、の 3 コマ |
| `walk_decompose.png` | 46（5-4） | 斜めの 1 本を北向きと東向きの 2 本に分ける |
| `calculator_quadrants.png` | 55（5-5） | 電卓は東側の 2 象限しか見ていない |
| `backsight_rotation.png` | 66（5-6） | 後視を間違えると全部の点が回る |

作り直し方（`Surveying/` で実行。`--build-dir` で改1 の `build/` と分ける）：

```powershell
python -I scripts/build_session05.py --markdown "materials/slides/第05回_トラバース測量I/slides_改2.md" -o "materials/slides/第05回_トラバース測量I/slides_改2.pptx" --build-dir "materials/slides/第05回_トラバース測量I/build/改2"
powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx "materials/slides/第05回_トラバース測量I/slides_改2.pptx" -PngDir "<空のフォルダー>"
npx @marp-team/marp-cli@4.1.2 "materials/slides/第05回_トラバース測量I/slides_改2.md" -o "materials/slides/第05回_トラバース測量I/slides_改2.html"
```

点検は `check_headers.py`（ページ番号）、統括の目視（新規枚）、Sonnet による全枚の PNG 点検（[確認画像/sonnet_点検_改2.md](確認画像/sonnet_点検_改2.md)）の 3 段で行い、指摘のうち表と図の同居で図が小さくなった枚（3 ステップの枚を絵と数字の 2 枚に分割）、題が 2 行に折り返した枚、表の中の絶対値記号が列の区切りと衝突した枚、表が下端に迫った枚を直した。32 枚目（交角法の後視・前視の図）と 39 枚目（偏角法の図）のラベルの重なりは改1 の SVG 由来なので今回は直していない。`確認画像/` には新規枚の PNG を数枚だけ置く。生成の途中案（`notes/session05_kai2_figures/generation_sources/*_attempt*.png`、約 20 MB）はリポジトリに入れていない。
