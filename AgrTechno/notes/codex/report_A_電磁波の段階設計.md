# 報告A：電磁波の段階設計と定量図版

作成日：2026-10-22。指定の背景資料を読み、**13段・標準13分（余裕2分、15分以内）の設計書とPNG13点**を作成した。既存スライド原稿への組み込みは今回の範囲に含めず、Git操作は行っていない。

## 成果物

- [電磁波の段階設計.md](電磁波の段階設計.md)：各段の到達文、見せる図、たとえ、誤解、読み上げ用4文のノート、式の扱い、確認問題と答え。旧表現の修正表、数値表、変更理由、短縮順も収録。
- [make_charts.py](../../scripts/figures/make_charts.py)：全図を作る1本のスクリプト。図ごとに関数・docstringを分離。
- [chart_validation.json](chart_validation.json)：画素数・実選択フォント・字形検査・画像外の文字・ファイルサイズ・実行版の検証記録。
- [DECK.md](DECK.md)：1枚1主張と図の設計ルール。
- [worklog_codex.md](worklog_codex.md)：作業記録。

## 作った図の一覧

全図のfigure/axes背景は #FAF9F5、8×4.5 inch・200 dpi。軸ラベルと目盛りは14 pt以上。図内に図タイトルは置かず、凡例と説明注記だけを使用した。小さな脚注・補助ラベルは9〜13 pt。模式曲線には「模式図」を表示した。

| ファイル | 画素数 | 選択フォント | 気づいた点・扱い |
|---|---|---|---|
| [chart_01_em_spectrum.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_01_em_spectrum.png) | 1600 × 900 | Yu Gothic | 全体対数軸＋RS帯域の拡大。マイクロ波も電波の一部と注記。 |
| [chart_02_wavelength_frequency.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_02_wavelength_frequency.png) | 1600 × 900 | Yu Gothic | 2波の伝播速度は同じ。式を図内に入れず山の間隔を比較。 |
| [chart_03_planck_temperature.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_03_planck_temperature.png) | 1600 × 900 | Yu Gothic | 6000 Kピークを共通基準とする。各曲線のピークに点。 |
| [chart_04_sun_earth_two_peaks.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_04_sun_earth_two_peaks.png) | 1600 × 900 | Yu Gothic | 各曲線を独立規格化。約3 µmは条件付きの目安で交点から導かない。 |
| [chart_05_atmosphere_windows.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_05_atmosphere_windows.png) | 1600 × 900 | Yu Gothic | 0〜100%の透過率。吸収名をプロット外の2段へ配置。晴天・雲を区別。 |
| [chart_06_solar_spectrum_toa_surface.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_06_solar_spectrum_toa_surface.png) | 1600 × 900 | Yu Gothic | 太陽の全波長積分を1361 W/m²へ規格化。地上は模式透過率との積。 |
| [chart_07_reflectance_curves.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_07_reflectance_curves.png) | 1600 × 900 | Yu Gothic | 雪の可視反射率は約90%で縦軸70%の外と明記。水吸収・レッドエッジを注記。 |
| [chart_08_reflectance_with_bands.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_08_reflectance_with_bands.png) | 1600 × 900 | Yu Gothic | 全域と可視/NIR拡大を併置。S2/OLIの帯は矩形近似、中心と幅は設計書に収録。 |
| [chart_09_ndvi_bars.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_09_ndvi_bars.png) | 1600 × 900 | Yu Gothic | NDVIは0.82／0.33／0.20／−0.50。右パネルは反射率ではなく共通倍率の未補正信号例。 |
| [chart_10_ndvi_saturation.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_10_ndvi_saturation.png) | 1600 × 900 | Yu Gothic | NDVIとNDREの形を比較する模式曲線。LAI3〜4は普遍的閾値ではない。 |
| [chart_11_resolution_tradeoff.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_11_resolution_tradeoff.png) | 1600 × 900 | Yu Gothic | 範囲と代表点を区別。ドローンの縦位置と商用再訪の縦幅は配置・概念上の値。 |
| [chart_12_satellite_timeline.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_12_satellite_timeline.png) | 1600 × 900 | Yu Gothic | 打上げイベント。失敗は×、FLEXは予定・結果要確認、Nextは時期未定の計画。 |
| [chart_13_leaf_cross_section.png](../../materials/slides/2026_農業とテクノロジ_RS/figures/charts/chart_13_leaf_cross_section.png) | 1600 × 900 | Yu Gothic | 葉内の赤の吸収とNIRの多重散乱。下への透過もあると注記。 |

## 梯子の要約（見出し）

- 段0：目で葉を見ることも、離れた場所からの観測である
- 段1：目に見える光は、電磁波のほんの一部である
- 段2：同じ速さなら、短い波長ほど揺れが速い
- 段3：反射は届いた光を返し、熱放射は物体自身が出す
- 段4：温度が高いほど、放射の山は高くなり短波長側へ動く
- 段5：太陽の山は約0.5 µm、常温の地表の山は約10 µmにある
- 段6：大気は、通しやすい波長と吸収しやすい波長を持つ
- 段7：入った光は、反射・吸収・透過に分かれる
- 段8：赤は色素に吸収され、近赤外は葉の内部で散乱する
- 段9：波長ごとの反射率の形から、植生・土・水を見分ける
- 段10：衛星は曲線全体を、いくつかの波長帯で測る
- 段11：赤と近赤外の差を、和で割ったものがNDVIである
- 段12：NDVIが頭打ちになる畑では、別の情報も使う

段0・3・7は設計書に矢印イラストの内容を指定している。今回の13点とは別の図であり、イラスト自体は未作成。図05は段6の補足、図11・12は後続の衛星選択・歴史に使い、13分の本文へすべてを押し込まない。時間は設計上の見積もりで、学生を伴う授業での実測ではない。

## 昨年度スライドで直すべき箇所の要約

- [016]〜[018]：電圧・電流だけを電場・磁場の定義にしない。「詳しい原因は不明」を削除し、電磁波が媒質不要で、真空では同じ光速で進むと整理する。
- [018]：「波長（周波数）はエネルギー」を訂正。λとfは反比例、E=hfのEは1光子のエネルギーで、光の総強度とは区別する。
- [019]〜[021]：熱放射に古典的電子軌道やα・β線を混ぜない。黒体は反射も透過もせず全吸収する理想体。低温でも広い連続スペクトルを持つ。
- 放射の3法則は式の連続提示をやめ、反射／放射の経路→温度別曲線→太陽と地表のピークへ進む。本文の物理式はλ=c/fとウィーンの短い式だけに絞る。
- [022]：可視は約0.38〜0.75 µm程度、授業は0.4〜0.7 µmへ丸める。新しい太陽スペクトルは実測値ではなく理論・模式近似だと明記する。
- [023]〜[024]：分光反射率に放射を混ぜず、「色や熱も電磁波」を訂正する。葉のNIR散乱をクロロフィルの反射と説明しない。
- [028]：NDVIに分母の意味、値域の条件、飽和を補う。曇天で真の反射率が半分になるとは言わず、共通倍率だけなら相殺するという説明へ修正する。

## 確認したこと

- Python 3.11.3、matplotlib 3.10.8、numpy 2.4.4、Pillow 12.1.1で実行した。
- 保存した13点をPillowで開き、全点1600×900 px、背景色が指定値であることを検査した。
- matplotlib.font_managerが選んだ実フォントは全図Yu Gothic。描画対象の文字についてフォントの字形表を検査し、欠けは0。描画時のmissing glyph警告も0。フォント名は標準出力へ出す。
- 全13画像を開いて目視し、脚注と軸ラベルの接近、比較図の名前、年表の密集部分を修正した。最終版で文字の切れ・豆腐・ラベル同士の重なりは見当たらない。
- プランク式を広い波長域で数値積分し、π∫Bλdλ=σT⁴と相対誤差2×10⁻⁵以内で整合することを6温度で検査した。ピーク位置はウィーンの法則と相対誤差0.1%以内。
- 透過率が0〜1に収まり、NDVIの共通倍率の例が一致することを確認した。
- 全図再生成と --only 03 を実行し、後者で変更されたPNGは図03だけだった。

## 再生成

AgrTechnoを作業ディレクトリとして実行する。

    python -I scripts/figures/make_charts.py
    python -I scripts/figures/make_charts.py --only 03

初期環境のmatplotlibは3.7.2で、packagingとsixも不足していた。システム側を変更せず、許可された scripts/figures/_vendor/ にmatplotlib 3.10.8・packaging 25.0・six 1.17.0を置き、スクリプトがそのパスを優先する。作業中のパッケージ取得は環境準備であり、資料のWeb検索や外部ページの照合は行っていない。キャッシュも scripts/figures/_mplconfig/ に限定した。別環境では [requirements.txt](../../scripts/figures/requirements.txt) の依存関係と日本語フォントが必要。ローカル依存パッケージ・キャッシュは配布図版ではないため、同ディレクトリの .gitignore に除外を記した。Gitコマンドは使用していない。

## 確認できなかった事項・適用限界

- R1で要確認の衛星の現況・商用再訪・実運用条件は、そのまま未確認。FLEXは2026予定の記述までで打上げ結果未確認。Landsat Nextは最終構成・時期未定で、2030年打上げ確定とは描いていない。
- R1にないLandsat各号、SPOT初号機、Terra/Aqua、ALOS-1、Sentinel-1B/2Bの過去の打上げ年は一般知識から補った。設計書の年表で出所を区別し、一次資料での照合を要確認とした。
- S2の機体別中心波長・実帯域応答、OLIの実応答は未照合。図08は一般公称仕様の矩形近似で、応答関数そのものではない。
- クロロフィルa/bのピークは溶媒中の代表値。測定条件依存の正確値は未確認で、葉の反射曲線と同一視しない。
- 大気透過率、植生等の反射率、NDVI/NDRE対LAIは模式曲線。観測データのフィットや施肥判断用の較正式ではない。太陽の地上スペクトルも標準大気モデルではない。
- リモコン実演の教材出典はR4で検索要約にとどまる。各スマホでの実演、実際の教室投影での視認性、授業所要時間は未検証。出典を確認できない体験案は設計書で「推測」と記した。
- 段12のkNDVIは補足に限定。単なる変換で測定情報が増えるとは説明せず、水・雲・雪の除外が必要とした。
