# 補足：方向角と象限

添付の「方向角は、象限を見て補正する」の説明を、理由から理解できる8枚に分けた補足資料。第3回の方向角の逆計算の説明に挿入する。既存の講義本体は変更しない。

- [編集用PowerPoint](方向角と象限_補足スライド.pptx)
- [閲覧・配布用PDF](方向角と象限_補足スライド.pdf)
- [講師用原稿と確認問題の解答](講師用原稿.md)
- `preview/`：全ページの確認画像。`スライド*.PNG` はPowerPoint出力、`slide-*.png` はArtifact Tool出力。

## 構成

| 枚 | 内容 | 伝えること |
| --- | --- | --- |
| 1 | X北・Y東と方向角の約束 | 北から時計回り、座標差は終点から始点を引く |
| 2 | 北東45°と南西225° | 正反対でも比は同じになる |
| 3 | 逆正接の主値 | arctanの答えは−90°より大きく90°より小さい |
| 4 | 象限と補正の表 | 180°は向きの修正、360°は同じ向きの表記の変更 |
| 5 | 南東・北西の計算例 | 同じ比−4/3でも、補正後は126.87°と306.87° |
| 6 | トラバースの順計算と逆計算 | cos・sinは符号も返す。逆計算では符号の確認が必要 |
| 7 | atan2、軸上、同一点 | 二つの座標差を渡す方法と例外 |
| 8 | 確認問題 | 比の前に向きを予想し、補正の理由を説明する |

1〜6枚目が説明の中心。7枚目は計算機利用の補足、8枚目は理解の確認に使う。解答は発表者ノートと講師用原稿に記載し、問題のスライドには表示していない。

## 数式・図の約束

Xは北向き、Yは東向き。座標図の横軸はΔY、縦軸はΔX。表のαは、絶対値を取らず、符号付きの比から計算した `arctan(ΔY/ΔX)` である。鋭角を使う別の補正式と混用しない。座標差は説明用の仮想値。

本文・数式は編集可能なテキスト、表はPowerPointの表、座標図は座標差のデータを持つ散布図。図の軸名は読みやすい位置にテキストで配置している。図の元データを変えた場合は、点の説明や本文の数値も合わせて更新する。

ExcelではB2=ΔX、C2=ΔYとして `=MOD(DEGREES(ATAN2(B2,C2)),360)`。Pythonでは `degrees(atan2(delta_y, delta_x)) % 360`。いずれも同一点（ΔX=ΔY=0）は先に除外する。

仕様の出典（2026-10-15確認）：[Microsoft公式のATAN2](https://support.microsoft.com/ja-jp/excel/functions/atan2-function)、[Python公式のmath.atan2](https://docs.python.org/3/library/math.html#math.atan2)。

## 再生成

`scripts/build_direction_angle_supplement.mjs` を、Codex同梱Node.jsとArtifact Toolで実行する。環境変数 `PRESENTATION_SKILL` にPresentationsスキルのディレクトリを指定する。出力先に完成PPTXや同名の検証記録が既にある場合は、別名で保存してから実行する。

PDFとPowerPoint確認画像は、完成PPTXに対して `scripts/export_axis_rotation.ps1 -Pptx <完成PPTX>` を実行して作成する。PowerPointを利用できるWindowsのログオンセッションが必要。

`build/` に初稿と生成用データ、`notes/direction_angle_20261015/` に構造・配置の検証記録を保存する。

完成後のPPTX/PDFの検査とPDFの描画は `scripts/check_direction_angle_supplement.py` で実行できる。
