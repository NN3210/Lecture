# 制作修正16：座標図版の軽微修正

2026-11-17。`Lecture/AGENTS.md` および `review06_diagrams_coords.md` に基づき修正した。

- `inverse` の T を SVG 座標で30 px上へ移動し、青い斜線との接触を解消。本文のP→Qに合わせて点名をP/Q、下端の式を `ΔX = XQ−XP、ΔY = YQ−YP` に統一した。
- `closure` のBを点の右上に移し、辺BCとの重なりを解消。始点A・A′・橙の閉合差矢印は維持した。
- 図中の「北」「北 X」「X：北」を「座標北」に統一。長くなったbacksightの注記だけ右へ移し、北向きの補助線との空白を確保した。軸・図の寸法（SVG 900×720、PNG 1800×1440）は維持した。
- `build_diagrams.py` はSVGとPNGを一時ファイルに完成保存してから置換するよう変更し、同時に読み込むレンダラーが未完成PNGを読むことを回避。review07由来の `generate_deflection()` とその呼出しは保持した。
- 全21図のSVG・PNGおよびコンタクトシートを再生成。`view_image` で inverse、closure、axes、exercise_inverse、cover、quadrants、backsight、deflection を確認し、指定ラベルの分離と新しい北注記の収まりを確認。part1/part2は未編集。

成分別の緑・橙配色は既存の識別方法を保持し、今回の軽微修正では変更していない。
