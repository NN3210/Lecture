# 作業ログ

## 2026-10-08（Claude Code）

- ローカルの `MISC/Lecture` を GitHub `NN3210/Lecture` のクローンにした（それまでは git 管理外の空フォルダ）。
- `AGENTS.md`（共通ルール）、`Surveying/README.md`、`notes/2026_practicum_summary.md` を作成。
- Codex はターミナルから `codex exec` で呼び出せることを確認（codex-cli 0.160.0）。Claude Code 側の MCP 登録 `codex mcp-server` はこのバージョンに存在しないサブコマンドのため接続失敗する。
- 録音要約（2026-05-27 学内実習、2026-07-16 現地測量）から測量に関わる指導ポイントを `notes/2026_field_teaching_notes.md` に抜粋。個人名・研究内容は除外。
- 測量学の 13 回講義計画 `materials/lecture_plan_13.md` を作成。Codex に `codex exec` でレビューさせ（原文は `notes/reviews/2026-10-08_codex_review_lecture_plan.md`）、以下を反映: 時間配分の統一（導入5+講義55+演習25+まとめ5）、第 11・12 回の入替え（写真→面積体積）、両差の公式名と三角水準の式、器高と器械高の区別、重みの一般則、閉合比の定義、点高法の係数の意味、写真縮尺の対地高度、測地成果 2024・ジオイド 2024 への更新（国土地理院サイトで確認）、地図編集・標尺補正・偏心観測・深浅測量・分割点・追加距離の追加、第 14 回を総復習専用に変更、測量士補の電卓不可への対応、試験ごとの重点の書き分け。

## 2026-10-08（Claude Code + Codex、第2回スライド）

- 第2回「測量の基礎と誤差論」のスライド作成指針 `materials/slides/_guidelines/slide_guidelines.md` を作成し、Codex（`gpt-6-astra`、`codex exec`）にスライド 68 枚（`materials/slides/第02回_測量の基礎と誤差論/slides.md`・`slides.html`・`README.md`）と手計算テスト（`materials/exercises/第02回_測量の基礎と誤差論/exercise.md`・`exercise_answers.md`）、検算スクリプト `scripts/check_exercise_02.py` を作らせた。
- Claude が成果物をチェック（`notes/reviews/2026-10-08_claude_review_session02.md`）。数値はすべて一致。表紙・例題Aの表・数式内の日本語・問2の密度の 4 点を直接修正した。
- Marp の `--pptx`/`--pdf` はこの PC では headless ブラウザがタイムアウトして使えないため、`scripts/md2pptx.py`（python-pptx + matplotlib mathtext）と `scripts/pptx_export.ps1`（PowerPoint COM で PDF 化）を作り、`slides.pptx`・`slides.pdf` を生成した。
- クラウド閲覧用に `slides.html`（KaTeX フォント埋め込み版）を Claude の Artifact として公開した（URL は非公開リンクのためリポジトリには書かない）。

## 2026-10-08（Codex、第2回の図解改訂版）

- 指定箇所を高校生にも伝わる説明・数値例・7点の図に改訂し、旧版を保持して`materials/slides/第02回_測量の基礎と誤差論/改訂版_20261008/`に新しいPPTX・PDF・原稿を保存した（本編68枚＋出典2枚）。
- 標準偏差・自由度・単位・信頼区間を2枚に統合。中心極限定理、平均の分散、観測回数の効果と限界、逆分散重みの平方完成にGUM・NISTの出典を添えた。
- 再生成用`build_session02_revised.py`と図原稿を保存し、例題・演習・追加数値例の検算、PDF描画、全体一覧と主要改訂ページの表示確認を実施した。
