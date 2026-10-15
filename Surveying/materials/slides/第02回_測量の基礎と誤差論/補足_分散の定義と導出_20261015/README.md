# 分散の定義と導出

2026年10月15日作成。平均の誤差伝播の補足資料の6枚目「補足05」の差し替え用5枚。元の資料と同じ16:9、背景色・文字色を用い、数式は編集可能なOffice数式とした。

1. 誤差eと期待値Eの区別、観測モデル、平均0の仮定。
2. 確率を重みとする期待値の数値例。二乗してから平均することの意味。
3. 分散の定義と平均0の代入、標準偏差の平方根。
4. 定義の二乗を展開し、期待値の線形性で整理する導出。
5. ＋3 mmの偏りが残る反例。誤差の二乗平均＝分散＋偏りの二乗。

必要な条件は二乗期待値が有限であること、および分散をE[eᵢ²]と簡略化するためのE[eᵢ]=0。独立性・正規性・同精度を、この式の導出の条件に混ぜない。正負の誤差が存在するだけで平均0になるとは限らない。

## ファイル

- `分散の定義と導出_補足スライド.pptx`：本文・表・数式を編集できるPowerPoint。
- `分散の定義と導出_補足スライド.pdf`：PowerPoint出力の閲覧・配布用。
- `slides.md`：本文・数式・講師用ノートの正本。説明用の確率モデルを明示。
- `preview/`：PowerPointから出力した全5ページの確認画像。
- `build/`：生成候補、数式変換データ、表示確認記録。

## 再生成

`scripts/build_variance_derivation.mjs`は`slides.md`から生成し、既存の`scripts/patch_session03_math.py`でMathMLをOffice数式に変換する。必要な環境変数は`ARTIFACT_MODULES`（バンドルのnode_modules）、`PRESENTATION_SKILL`、`RUNTIME_PYTHON`、`KATEX_MODULE`（利用可能なkatex.mjs）。最終ファイルが存在する場合は旧出力を退避してから実行する。

```powershell
& '<バンドルのnode実行ファイル>' scripts/build_variance_derivation.mjs
& scripts/export_variance_derivation.ps1
& '<Python実行ファイル>' scripts/check_variance_derivation.py
```

PowerPointの利用可能なWindowsセッションでPDFとPNGを出力する。原稿に書いた期待値の性質と二乗の展開で導出しており、外部資料の引用や新たな実機仕様の仮定はない。単位・仮想確率モデル・一般の恒等式は数値検算でも確認する。
