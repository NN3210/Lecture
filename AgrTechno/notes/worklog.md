# AgrTechno 作業ログ

## 2026-10-22

- 昨年度の講義スライド原本（`AgrTechno/261022_農業とテクノロジ_RS.pptm`、39 枚、約 31 MB、スライド 4 に 12 MB の 3D モデル、スライド 1 に担当教員の氏名）を受領。原本はリポジトリに入れず、ローカルの同フォルダに置いたまま（`.gitignore` で除外）。
- `dump_pptx_outline.py` で全 39 枚のテキストと発表者ノートを `notes/改0_全39枚の内容抽出.md` に抽出し、画像 47 点を一時フォルダに取り出した。
- プロジェクトの骨組み（`README.md`、`AGENTS.md`、`notes/worklog.md`）を作成。
- Sonnet サブエージェントで最新動向を調査（`notes/research_20261022/` R1〜R4・R6：衛星センサとデータ基盤の現況、日本の農業での実用例、国際と研究の動向、電磁波と放射の教え方、GNSS/GIS の更新事実）し、旧 39 枚の構成診断（`notes/改0_構成診断.md`）と新しい構成案（`notes/改1_構成案.md`）を書いた。
- Codex（gpt-6-astra）に電磁波〜植生指数の段階設計（ジョブ A）と文字なしの概念イラスト 13 点（ジョブ B、image_gen）を依頼。イラストは Pillow で背景を #FAF9F5 に平坦化して `figures/illustrations/` に置き、生成原本 `_source/` は commit しない。指示と報告は `notes/codex/`。
- 講義原稿 `materials/slides/2026_農業とテクノロジ_RS/slides.md`（Marp、本編 57 枚＋付録 3 枚＝60 枚、道標 A〜E で 5 章）を書き、定量図 13 点は `scripts/figures/make_charts.py`（matplotlib、模式図は明記）で描いた。
- `scripts/build_agrtechno.py`（`Surveying/scripts/md2pptx.py` を継承、数式は KaTeX→OMML）で pptx を組み立て、`pptx_export.ps1` で PDF と PNG を書き出し、Sonnet に全 60 枚を点検させて直した：2 段組（図＋文章）、章扉、題の自動縮小、表の列幅、本文サイズの自動選択、プランク式の表記、図中の注記位置、孤立行の言い換え。
- 公開リポジトリのため、個人名は役割名（担当教員・前任教員）に置き換え、Codex のログ中の Windows ユーザー名は `<home>` に置換してから commit した。
- 最終点検（Sonnet 26 枚＋統括 10 枚）で残った孤立行 5 枚（3・39・45・53・54）を言い換え、短い列（8 文字以下）は最長セルが 1 行に収まる幅を先に確保するよう `build_agrtechno.py` の列幅計算を直した。成果物は `slides.pptx`（7.7 MB、60 枚、Office 数式 6 式）と `slides.pdf`（4.1 MB）。
- スキル `lecture-storyline-guide` で講師用解説 `materials/slides/2026_農業とテクノロジ_RS/講師用解説_思想と教え方.html`（約 80 KB、1 ファイル、JavaScript なし）を作成。要旨（写真ではなく数値／葉の反射／NDVI／衛星＋実測）、7 つの対比、7 段の梯子と 9 か所の橋渡し、節ごとの台詞とつまずき、誤文 18 行の表、想定質問 8 件、削る順位 7 段と背骨 23 枚、弱点 7 点と改訂案 3 点を収めた。
- 枚番号は `build/outline.txt` の通し番号（1〜60）で引用し、図は `figures/charts/chart_09_ndvi_bars.png` を相対パスで 1 点だけ埋め込んだ。タグの対応・画像の実在・目次アンカーを点検し、ブラウザで表示を確認。スライド本体（`slides.md`・pptx）は変更していない。`README.md` の構成に 1 行追加。
2026-10-30: 2025年版AI講義62枚を監査し、農業AI差込10枚・AI基礎補足8枚をMarp原稿から生成。
2026-10-30: 公式一次資料で実装段階と歴史・数値を確認し、XOR・qPCR・ImageNet等の訂正と差込ガイドを作成。
2026-10-30: PowerPointでJohn DeereとCarbon Roboticsのオンライン動画実再生、自作模式図と補足図を視覚確認。原本と他プロジェクトは変更せず。
