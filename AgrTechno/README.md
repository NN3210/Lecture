# AgrTechno — 講義「農業とテクノロジー：農業分野におけるリモートセンシング技術」

帯広畜産大学 地域環境計画学（2 年後期）の 1 回分の講義スライドを、年度ごとにブラッシュアップして管理するプロジェクトです。

## 目的

- 昨年度（2025-11-07 実施）のスライド 39 枚を土台に、最新技術（現在運用中の衛星・センサ、無料データ基盤、日本と十勝の農業での実用例、AI 基盤モデル）を反映する。
- 電磁波〜放射〜分光反射〜植生指数の基礎部分を、物理が高校止まりの農学系 2 年生が「段階的に少しずつ飲み込める」順番に組み直す。
- Markdown（Marp）を唯一の原稿にして、そこから PowerPoint を機械的に組み立て直せる形にする。

## 構成

- `README.md` — この説明
- `AGENTS.md` — このプロジェクトでの作業ルール
- `notes/` — 作業ログ（`worklog.md`）、旧デッキの抽出と診断（`改0_*.md`）、調査メモ（`research_YYYYMMDD/`）、Codex への指示と報告
- `materials/slides/` — 講義スライド。回ごとのフォルダに Marp の `slides.md`、図版 `figures/`、生成した `pptx` / `pdf` / `png` を置く
- `scripts/` — `slides.md` から pptx を組み立てるスクリプト（`Surveying/scripts/md2pptx.py` を利用）、図版を描くスクリプト

## 進め方（2026 年度）

1. 旧デッキを `dump_pptx_outline.py` で全枚抽出し、構成診断を書く（`notes/改0_構成診断.md`）
2. Sonnet サブエージェントで最新動向を調査する（`notes/research_20261022/`）
3. Codex（gpt-6-astra）に電磁波の段階設計の検討と図版生成（image_gen）を依頼する
4. 講義内容を Markdown で段取りし（`materials/slides/.../slides.md`）、pptx を組み立て、PNG で全枚点検する

## 組み立て方（2026 年度版）

原稿は `materials/slides/2026_農業とテクノロジ_RS/slides.md` だけ。直すときは Markdown を直して組み立て直す（PowerPoint を手で編集しない）。

```bash
python scripts/figures/make_charts.py                  # 定量図 13 点（figures/charts/）を描き直す（必要なときだけ）
python scripts/build_agrtechno.py                      # slides.md → slides.pptx（数式は Office 数式）
powershell -ExecutionPolicy Bypass -File ../.claude/skills/lecture-deck-build/scripts/pptx_export.ps1 -Pptx materials/slides/2026_農業とテクノロジ_RS/slides.pptx -PngDir materials/slides/2026_農業とテクノロジ_RS/png
```

- `build_agrtechno.py` は `Surveying/scripts` の `md2pptx.py`・`omml_equations.py`・`katex_mathml.mjs` を読み取り専用で使う（node と KaTeX が必要）。
- 概念イラスト（`figures/illustrations/`、文字なし 13 点）は Codex の画像生成で作った。プロンプトは同じフォルダの `生成プロンプト.md`。
- `png/` と `build/` は中間ファイルで、git には入れない。

## 注意

- 昨年度の原本 `261022_農業とテクノロジ_RS.pptm`（約 31 MB、個人名と 3D モデルを含む）はリポジトリに入れません。所在は `notes/worklog.md` に記します。
- 公開リポジトリのため、個人名・連絡先は書かず、役割名（担当教員、前任教員、協力企業 等）で表します。
