# 作業ディレクトリの構成（1 回分）

`Surveying/notes/session<NN>_<tag>_<YYYYMMDD>/` の下にすべて置く。`<NN>` は講義の回、`<tag>` は短い英字（`kai2`、`traverse` など）。

```
notes/session05_traverse_20261101/
├── 00_設定.md                       # テーマ・副話題・ヘッダー接頭辞・段階コード表・既存デッキ・目標件数（new_session.py が作る）
├── collect/                         # 段階 1：lecture-source-search
│   ├── _収集指示.md                 #   サブエージェント共通の指示（init_collect_dir.py が雛形から作る）
│   ├── 資料収集_A_英語スライド.md   #   サブエージェント A の出力（10 列の表）
│   ├── 資料収集_B_英語動画.md
│   ├── 資料収集_C_日本語.md
│   └── 資料収集_D_他言語.md
├── 01_資料一覧.md                   # 段階 1 の出力：通し番号付きの全件（merge_sources.py）
├── codex/                           # 段階 2・3 の作業場
│   ├── .gitignore                   #   cache/ tmp/ logs/*_stdout.log を除外（init_codex_dir.py が置く）
│   ├── batch_prompt_template.md     #   Codex への雛形（通常版。init_codex_dir.py が {{SUBJECT}} 等を埋めて置く）
│   ├── batch_prompt_template_light.md #  省メモリ版（curl → PyMuPDF/html.parser。ブラウザーは最後の手段）
│   ├── batches/batch_v01.md …       #   動画 v、文書 p、再実行 <id>r・rNN（merge_sources.py / make_rerun_batch.py）
│   ├── prompts/batch_<id>_prompt.md #   実際に Codex へ渡したプロンプト（run_codex_batch.py）
│   ├── logs/                        #   batch_<id>_stdout.log（除外）、batch_<id>_last_message.md、<id>_操作ログ.md（Codex が書く）
│   ├── results/資料NNN.md           #   段階 2 の出力：1 資料 1 ファイル（Codex が書く）
│   ├── tmp/                         #   Codex が curl / yt-dlp で落とす一時ファイル（除外。読み終えたら Codex が消す）
│   ├── cache/資料NNN/               #   字幕の先取り（prefetch_subs.py。著作物なので除外）
│   ├── merge_instructions.md        #   Sonnet 向けの圧縮指示（make_merge_instructions.py が段階コード表から作る）
│   ├── merged/<batch_id>.md         #   段階 3：Sonnet がバッチ単位で圧縮したもの
│   ├── stage_stats.md               #   段階 3：段階コードの集計（stage_stats.py）
│   └── つなぎ理由と工夫の整理.md    #   段階 3：Sonnet が「つなぎ・工夫・無い段階・導入」を段階ペア別に整理
├── 02_各資料の構成抽出.md           # 段階 3 の出力：全資料の圧縮版（concat_merged.py）
├── 03_順序の抽象化と理由.md         # 段階 3 の出力：4 つの問いへの答えと飛び石チェック表（統括が書く）
├── 改1_全枚の内容抽出.md            # 段階 4（既存デッキあり）：dump_pptx_outline.py の出力
├── 改1_構成診断.md                  # 段階 4：全体像・重複・順序の問題・欠けの候補・非表示の扱い
├── 04_改2構成案.md                  # 段階 4：枚順の表（k1:NN / new:ID、header=…）
├── 04_新規枚.md                     # 段階 4：新規枚の中身（## new:ID の下に - key: value）
├── 確認画像/                        # 段階 4：目視に使った PNG の一部（全枚は置かない）
└── 手順書/                          # 任意：各段階の実行記録（何件・何分・どこで止まった・何を直した）
```

## どのファイルを commit するか

| commit する | commit しない（`.gitignore`） |
| --- | --- |
| `00_設定.md`、`collect/*`、`01`〜`04`、`改N_*`、`codex/batches/`、`codex/prompts/`、`codex/results/`、`codex/merged/`、`codex/logs/*_last_message.md`、`codex/logs/*_操作ログ.md`、`codex/stage_stats.md`、`確認画像/`（数枚） | `codex/cache/`（字幕＝著作物）、`codex/tmp/`、`codex/logs/*_stdout.log`、50 MB 超の pptx、全枚の PNG |

成果物の pptx・pdf は `materials/slides/第NN回_<題>/` に置く（50 MB 以下に縮めてから）。
