# Lecture リポジトリ 作業ルール（Claude Code / Codex 共通）

このリポジトリは講義資料の作成用です。現在の作業対象は `Surveying/`（測量学・測量学実習）です。
Codex Cloud ではサブディレクトリ単位の環境が作れないため、この Lecture リポジトリ全体を環境にし、作業は `Surveying/` 以下で行います。

## 必ず守ること

1. 成果物・中間ファイルは **すべて `Surveying/` 以下に保存** し、`main` に commit / push する。ローカル専用の場所や一時ディレクトリに置いたままにしない。
2. このリポジトリは **公開（public）** です。個人名・メールアドレス・電話番号・学生情報・外部企業担当者の連絡先は書かない。必要なら役割名（協力企業A、担当者 等）で表す。
3. 1ファイル 50MB を超えるファイル（写真の原本、動画、点群など）は commit しない。縮小版か、所在のメモ（`Surveying/notes/`）だけを置く。
4. 作業を終えるときは `git status` が clean になるまで commit し、push する。別エージェント（Claude または Codex）が続きを読む前提で、`Surveying/notes/worklog.md` に日付付きで何をしたかを 2〜5 行追記する。
5. 日本語で記述する（講義資料が日本語のため）。

## ディレクトリ構成

- `Surveying/README.md` — 目的・構成・進め方
- `Surveying/notes/` — 背景メモ、作業ログ、決定事項
- `Surveying/materials/` — 講義スライド・配布資料・課題（Markdown / pptx / pdf）
- `Surveying/data/` — 実習データ（座標、観測簿、サンプル）。個人が特定できるものは入れない
- `Surveying/scripts/` — 計算・作図スクリプト（Python / R）
