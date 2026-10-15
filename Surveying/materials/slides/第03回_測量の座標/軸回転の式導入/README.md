# 軸回転の式の導出

原点を `(x₀, y₀)` に移し、座標軸を反時計回りに `θ` 回したときの座標変換を説明する補足スライド。全13枚、16:9。点の位置を保ったまま座標を読み直す。

## 成果物

- [PowerPoint](軸回転の式の導出.pptx)：本文と数式を編集可能。数式はOffice Math形式。
- [PDF](軸回転の式の導出.pdf)：閲覧・配布用。
- [スライド原稿](スライド原稿.json)：各枚の見出し、数式、講師向け説明。
- `preview/`：PowerPointから書き出した全13枚の表示確認画像。
- [参考図](参考図_添付.png)：依頼時の添付画像。原図のQの新座標は誤記のため、スライド上で訂正を明記。

## 内容

1. 軸回転の式の導出
2. 同じ点を、新しい座標で読む
3. 原点を移す
4. 新しいx′軸の向き
5. 新しいy′軸の向き
6. 同じベクトルを二通りに表す
7. x′の導出：y′を消去する
8. y′の導出：x′を消去する
9. 原点移動と軸回転を合わせる
10. 符号の確認：軸を回すと、角度を引く
11. 計算例P
12. 計算例Q
13. 行列での表現と逆変換

座標はx軸右向き・y軸上向き、角度は反時計回り正とする。日本の測量におけるX軸北向き・Y軸東向きや方向角の約束へ適用するときは、軸と角度の定義を確認する。

計算例の条件は新原点 `(1, 0.5)`、回転角30°。P `(3, 2)` の新座標は約 `(2.48, 0.30)`、Q `(1, 3)` は約 `(1.25, 2.17)`。原図のQの表示 `(1.54, 2.33)` を訂正した。

## 再生成

`Surveying/` を作業ディレクトリとして、WindowsとMicrosoft PowerPointのある環境で実行する。

```powershell
python scripts/build_axis_rotation.py
```

`build_axis_rotation.mjs` がArtifact Toolで本文を作り、既存の `patch_session03_math.py` の変換処理を `build/patch_math.py` に展開してOffice数式にする。`finalize_axis_rotation.mjs` で構造・配置・フォントを確認し、`export_axis_rotation.ps1` で対象の資料だけを開いてPDF・PNGを出力する。

必要環境は既存の第3回資料と同じ。Node.js、Artifact Tool、KaTeX、Pythonのlxml、Microsoft OfficeのMML2OMML.XSLを使う。環境が標準配置と異なる場合は `ARTIFACT_MODULES`、`MARP_MODULES`、`PRESENTATION_SKILL`、`RUNTIME_PYTHON` を指定する。PNGは全ページを表示確認する。検証記録は `notes/axis_rotation/` に保存する。
