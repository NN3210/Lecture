# 点の回転と座標軸の回転

数学の通常の座標系（横が x、縦が y）を用い、点を回す場合と座標軸を回す場合の符号の違いを説明する補足資料。全2枚。

- [編集可能なPowerPoint](点の回転と座標軸の回転_図解.pptx)
- [閲覧・配布用PDF](点の回転と座標軸の回転_図解.pdf)

1枚目は座標軸を固定して点を反時計回りに回す。角度 φ が φ+θ になることから、加法定理で R(θ) を導く。
2枚目は点を固定して座標軸を反時計回りに回す。新しい軸から測る角度が φ−θ になることから R(−θ) を導く。原点の移動は x, y を x−x₀, y−y₀ に置き換える。

同じ点 (1,0) と θ=90° の例で、前者は (0,1)、後者は (0,−1) になることを図で確かめる。数式はOffice Math、座標軸・点・回転の矢印はPowerPointの編集可能な図形。講師用の詳しい説明は発表者ノートに保存した。

## 再生成

`Surveying/` で `PRESENTATION_SKILL`（Presentationsスキルのディレクトリ）と `MARP_MODULES`（KaTeXを含むNodeモジュールのディレクトリ）を指定する。必要に応じ `ARTIFACT_MODULES` と `RUNTIME_PYTHON` も指定する。

```powershell
node scripts/build_rotation_supplement.mjs
python scripts/patch_session03_math.py native-math.pptx materials/slides/第03回_測量の座標/補足_点と座標軸の回転_20261015
node scripts/build_rotation_supplement.mjs --finalize-only
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx materials/slides/第03回_測量の座標/補足_点と座標軸の回転_20261015/点の回転と座標軸の回転_図解.pptx -NoPng
```

検証済みファイルの上書きを避けるため、再生成時には最終版のファイル名と検証記録名を新しい名前に変更する。中間ファイルは `build/`、表示確認画像と検証記録は `notes/rotation_supplement/` に保存する。
