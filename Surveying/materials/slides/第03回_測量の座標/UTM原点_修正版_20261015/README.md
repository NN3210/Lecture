# UTMの原点の修正版（2026-10-15）

第3回の41枚目「UTM座標系」の差し替え用1枚。全体講義ファイルとは別に保存する。既存の図が緯度24°より北しか示していないため見えなかった、赤道上の各投影原点を一覧にした。東距への加算と縮尺係数を分けて説明し、元の枠内の平面直角座標系との比較も残す。

- `UTMの原点と座標の読み方.pptx`：本文と表を編集できるスライド。
- `slides.md`：スライド原稿。
- `解説.md`：講師用解説と一次資料。PPTXの発表者ノートにも収録。
- `notes/utm_origin_20261015/`：候補PPTX・点検画像・検証記録（Surveyingからの相対パス）。

再生成は `PRESENTATION_SKILL` にPresentationsスキルのディレクトリを指定し、`Surveying/scripts/build_utm_origin.mjs` をCodex同梱のNode.jsで実行する。保存先の既存PPTXを変更しないfinalizerのため、再生成時は出力名を新しくする。`--preview-only` はPPTXを変更せず同じ原稿の点検PNGを再出力する。
