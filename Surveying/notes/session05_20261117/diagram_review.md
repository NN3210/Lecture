# 改3 図版の作図・点検記録

- ソース：`build_diagrams.py`。標準ライブラリ＋PillowでSVGを作り、Inkscapeで1800×1440 PNGへ出力。SVG内テキストはNoto Sans CJK JP、900×720の白背景。全20図。
- 仕様17図に加え、`triangulation`（四角形の内角和）、`exercise_traverse`（5点演習）、`exercise_inverse`（P→Qの逆計算見取り図）を提供。すべて改3/assetsにSVGとPNGの組で保存。
- `direction_loop`、`cover`は講義4点の調整済み方向角と距離を使った実形状。`exercise_traverse`も演習5点の調整済み方向角と距離から計算。北を上、東を右、A→B→…→Aを反時計回りに描いた。実距離の微小な座標閉合差は、この見取り図では点Aを共通終点として描く。
- `turning`は講義例Bで、後視BA=242°30′、前視BC=328°10′20″、時計回りβ=85°40′20″。`backsight`は第4回からの接続用AB40°→BA220°→BC320°。
- `interior`は、反時計回り巡回でβ=内角、時計回り巡回でβ=360°−内角となる2図を対置。どちらも後視から前視への時計回りの弧。
- `exercise_inverse`はΔX=+80、ΔY=−150に比例した北西方向の図。距離170mや方向角の解答は含めない。
- `closure`は閉合差の拡大概念図、`site`は農地・水路・農道の模式図。Bowditchの棒・矢印長は4測線の距離に比例。
- 全20SVGをXMLとして再読込できること、全20PNGが1800×1440であることを確認。全図コンタクトシートを`diagrams_contact_sheet.jpg`に出力し、view_imageでラベル重なりと配色を点検。後視Aラベルとworkflow最下段の余白を調整済み。

- 親レビュー後、内角和説明専用に`triangulation`を追加。対角線ACの左右を2色の三角形で示し、それぞれ180°、合計360°を表示。追加図もview_imageで点検済み。
