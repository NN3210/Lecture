# 第2回「測量の基礎と誤差論」図解・やさしい解説版

2026-10-08改訂。高校生にも分かる説明を目指し、指定された誤差・標準偏差・正規分布・平均・重みの説明を更新した。元の68枚の版は上のフォルダに保存したまま、別ファイルで作成している。

- [新しいPowerPoint](測量学_第02回_図解改訂版.pptx)
- [閲覧用PDF](測量学_第02回_図解改訂版.pdf)
- [改訂版原稿（正本）](slides_revised.md)
- [確認記録](確認記録.md)

本編68枚＋出典付録2枚＝70枚。導入1〜5、講義6〜60、演習61〜65、まとめ66〜68。90分の時間配分と演習問題は従来版を維持し、付録69〜70は参照用とした。発表者ノートは全70枚に付けた。

## 改訂箇所

| ページ | 内容 |
| --- | --- |
| 6 | 見える観測値・推定する平均・未知の真値を区別する概念図 |
| 7〜10 | 過失・定誤差・偶然誤差を身近な数値例と対処で説明 |
| 13〜14 | 中心極限定理の条件、独立な±1要因の和による正規近似の図、GUMの出典 |
| 15〜16 | 元の「標準偏差と誤差の範囲」と「1観測の標準偏差〜単位」を2枚に統合。計算・自由度・単位・95%信頼区間を説明 |
| 17 | 的の中心と観測点で、ばらつきと偏りを区別 |
| 22 | 単位・対象量・過失・補正・独立性・精度を確認する流れ |
| 28〜29 | 4回平均の各入力の寄与と、分散を二乗して足す理由 |
| 30 | 回数の平方根に反比例する効果、相関による限界、共通の偏りが残る理由 |
| 39〜40 | 分散を最小にする配分のグラフと、平方完成による逆分散重みの説明 |
| 69〜70 | GUMとNISTの出典、該当節、公式サイトへのリンク |

図は本教材用に計算・作図したもので、実測データや第三者の図の転載ではない。元の作成指針の画像制限に対し、今回の図解依頼を優先し、SVG原図とPNGを保存してPPTXに埋め込んだ。本文と表は編集可能で、図とブロック数式は画像。

## 再生成

`Surveying/`を作業ディレクトリとして次を実行する（python-pptx、matplotlib、numpy、Pillowが必要）。既存の`md2pptx.py`を利用する。

```sh
python scripts/build_session02_revised.py
```

PDFは生成したPPTXをLibreOfficeで書き出した。PowerPointでも「エクスポート」からPDFにできる。フォントはNoto Sans CJK JP、行内数式はDejaVu Sans。フォント未導入の端末では代替フォントによって配置が変わる場合があるため、配布時の見た目はPDFで確認できる。

## 出典

- JCGM 100:2008, *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*（GUM）, 4.2.2–4.2.3、5.1.2、5.2.2、G.2、G.3、表G.2。 [BIPM公式PDF](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)
- NIST/SEMATECH, *e-Handbook of Statistical Methods*, [§1.3.5.2 Confidence Limits for the Mean](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)。
- 同、[§4.1.4.3 Weighted Least Squares Regression](https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd143.htm)、[§4.4.5.2 Accounting for Non-Constant Variation Across the Data](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd452.htm)。

いずれも2026-10-08に公式サイトを確認。
