---
marp: true
size: 16:9
paginate: false
---

<!-- _class: hierarchy -->
# 深層学習は機械学習の一部で、AIと同義ではない

## AI
知的な課題を計算機で扱う広い分野

## 機械学習
データから規則や予測モデルを学ぶ方法

## 深層学習
多層のニューラルネットワークを使う方法

<!-- _notes: 元資料5–6枚目の分類を更新。AIは一つの技術名ではなく研究領域・応用領域であり、機械学習と深層学習は包含関係として示す。ルールベースの推論もAIに含まれる。 -->
<!-- _sources: https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks -->

---
<!-- _class: flow -->
# ニューラルネットは、重みとバイアスを学習して予測する

## 入力
画像の画素やセンサー値

## 計算
入力×重みを足し、ユニットのバイアスを加える

## 非線形化
ReLUなどの活性化関数を通す

## 学習
誤差を使い、パラメータを更新する

<!-- _notes: 元資料8枚目の「各接続に重みとバイアス」は誤解を招く。通常の密結合層では重みは接続、バイアスは出力ユニットごと。元資料23枚目のシグモイドは0–1だがReLUは上限1ではない。層を増やすだけで必ず性能が向上するわけではない。 -->
<!-- _sources: https://www.deeplearningbook.org/contents/mlp.html -->

---
<!-- _class: case -->
# XORは「どちらか一方だけ」が1になる

## A=0、B=0
出力0

## A=0、B=1
出力1

## A=1、B=0
出力1

## A=1、B=1
出力0

<!-- _notes: 元資料31枚目の「Aか、でないならB」という説明はXORの定義として曖昧。正しくはAまたはBの一方だけが真の場合に1、両方真・両方偽は0。式は (A∨B)∧¬(A∧B)。4点は1本の直線で分離できず、中間層の非線形な表現が役立つ。 -->
<!-- _sources: https://www.deeplearningbook.org/contents/mlp.html -->

---
<!-- _class: timeline -->
# AIの歴史は「世代」より、成果と限界で捉える

## 1956
ダートマス夏季研究会が開かれる

## 1989
誤差逆伝搬を使う手書き数字認識の論文

## 2012
画像認識競技で深層CNNが大きく改善

## 2017
Transformerが自然言語処理へ新しい構成を提示

<!-- _notes: ダートマス研究会の提案書は1955年に作成され、1956年夏の研究会を構想し、artificial intelligence の語を用いた。元資料6・29–35枚目の3世代区分は便宜的で粗い。1989年と2012年の成果は各課題の結果で、一般知能の達成を意味しない。 -->
<!-- _sources: https://www-formal.stanford.edu/jmc/history/dartmouth/dartmouth.html ; https://papers.nips.cc/paper_files/paper/1989/file/53c3bce66e43be4f209556518c2fcb54-Paper.pdf ; https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf ; https://arxiv.org/abs/1706.03762 -->

---
<!-- _class: compare -->
# 2012年の快挙は画像認識の競技結果として読む

## AlexNet系
Top-5誤り率 15.3%

## 次点の方式
Top-5誤り率 26.2%

## 解釈
この課題で大幅に改善。毎年半減・全課題で人間超えではない

<!-- _notes: 原論文に記載されたImageNet 2012の比較。15.3%と26.2%は評価方法とデータセットに依存する数値であり、「毎年半分」や「一般画像認識が人間を超えた」といった無条件の主張には使えない。 -->
<!-- _sources: https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf -->

---
<!-- _class: flow -->
# 農業AIは、学習後に新しい圃場でも性能を確かめる

## 学習
正解付きの画像や音から規則を学ぶ

## 検証
未使用データで誤検出と見逃しを測る

## 現場試験
季節・品種・光・地域が変わっても評価する

## 更新
失敗例を収集し、再学習・再検証する

<!-- _notes: 元資料24枚目の「重みの調整」だけでは、性能評価と分布変化への対応が抜ける。学習・検証データの重複を避け、現場での新条件に対する汎化性能を評価する。 -->
<!-- _sources: https://www.nist.gov/itl/ai-risk-management-framework -->

---
<!-- _class: compare -->
# 生成AIと画像判別AIは、出力も評価方法も異なる

## 画像判別
病斑の候補や雑草の位置を出す

## 生成AI
文章・画像・コードなどを生成する

## 共通の注意
出力を正解とみなさず、出典と現場条件を確認する

<!-- _notes: 元資料は画像判別中心なので、2026年の学生が連想する生成AIとの違いを短く補う。生成AIも機械学習の一部であるが、診断や農薬の使用判断には対象作物・地域の登録情報や専門家確認が必要。 -->
<!-- _sources: https://www.nist.gov/itl/ai-risk-management-framework/generative-artificial-intelligence-profile -->

---
<!-- _class: compare -->
# qPCRは標的を検出し、配列解読は別の方法で行う

## qPCR
既知の標的DNAがあるかを増幅中の蛍光で検出・定量する

## シーケンシング
DNAの塩基の並びを読み、配列情報を得る

## 環境DNA調査では
対象種を決めて探す方法と、多種を調べる方法を使い分ける

<!-- _notes: 元資料48枚目の「qPCRで配列を解読」は誤り。qPCRは標的配列を利用して増幅・検出するが、塩基の並びそのものは読まない。環境DNAのメタバーコーディングではPCR後に高スループットシーケンシングを使う。検出されたDNAは生体そのものの直接観察ではない。 -->
<!-- _sources: https://www.usgs.gov/glossary/edna-environmental-dna-glossary-umesc ; https://www.usgs.gov/centers/upper-midwest-environmental-sciences-center/science/edna-best-practices-resource-managers ; https://www.genome.gov/about-genomics/fact-sheets/DNA-Sequencing-Fact-Sheet -->
