# 第3回スライドの視覚改訂（2026-10-15）

全81枚の順序・小テスト・手計算演習を維持し、本文を短くして補足を発表者ノートへ移した。図を大きく配置し、文字色・余白・表・強調色を統一。GNSSとTSの観測イラストを各1点追加した。

本文と表は編集可能。本文・表の数式211件はOffice Math（OMML）に変換し、分数・根号・添字・行列の括弧・等号の位置を整えた。既存の図中の文字は図の一部。数式はCambria Math、日本語はMeiryoを使用する。

## 確認方法

- PowerPointで全81枚を開き、同じファイルからPDFを出力。`preview/slide-01.png`〜`slide-81.png`と7枚の一覧画像で表示を確認した。
- PDFの文字範囲と未変換プレースホルダーを機械点検（`pdf-audit.json`）。演習は`../../scripts/check_exercise_03.py`で検算。
- PPTXのパッケージ構造、81枚の枚数、スライド寸法、36個の編集可能な表、フォントをfinalizePresentationで点検。
- Artifact Toolの再読込は`Unsupported OMML node 'ArgumentProperties'`となるため、数式を除去せず、再読込検査だけを無効化。実際の使用先であるPowerPointでの開封・PDF出力を確認した。数式非対応の旧ビューア向け代替文字列はLaTeX原文。配布・閲覧にはPDFを利用する。

## 内容上の明確化

- 軸を回す変換と点を回す変換、剛体変換と縮尺を変える相似変換を区別。
- 水の流れは水面の勾配で判断する。ジオイドは静止した水の基準面であり、「ジオイドに沿って流れる」という説明を修正。
- WGS84・ITRF・日本の測地系は実現法・版・元期を確認する。測地成果2024の名称変更と標高成果の改定を区別。
- 平面直角座標系の目安は中央子午線から東西それぞれ約130 km。メルカトル図法の計算と光の影による模型を区別。
- 198°の例は第3象限。丸めた座標による逆計算には近似記号を使用。

出典はスライド81と各発表者ノートに記録。主な照合先：[国土地理院・平面直角座標系](https://www.gsi.go.jp/sokuchikijun/datum-main.html)、[標高成果改定FAQ](https://www.gsi.go.jp/sokuchikijun/hyoko2024rev-QA.html)、[基準点成果等閲覧サービスFAQ](https://service.gsi.go.jp/kijunten/app/faq/)。

改訂前は`before-sheet-*.jpg`、改訂後は`preview/contact-*.jpg`で比較できる。最終成果物は[スライドのフォルダー](../../materials/slides/第03回_測量の座標/)にある。
