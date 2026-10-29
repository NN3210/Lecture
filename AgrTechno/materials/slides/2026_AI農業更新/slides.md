---
marp: true
size: 16:9
paginate: false
---

<!-- _class: flow -->
# 農業AIは「見つける」だけでなく、作業の判断につなぐ

## 観測
画像・音・センサーで圃場を記録する

## 推定
病害虫・雑草・生育を候補として示す

## 判断
現場の条件と費用を人が確かめる

## 作業
散布・除草・収穫などを実行し結果を検証する

<!-- _notes: 元資料の「画像判別」の後に、AIが現場作業へつながる全体像を示す。モデルの出力だけで防除を決めず、対象作物・地域・時期を照合する。 -->
<!-- _sources: https://www.maff.go.jp/j/kanbo/smart/ -->

---
<!-- _class: case -->
# 病害虫の写真診断は、国内で使えるアプリになっている

## 入力
スマートフォンで病徴・虫・雑草を撮影

## AIの仕事
画像から候補を順位付きで提示

## 現場の仕事
候補を確認し、発生条件・防除基準と照合

## 実装段階
公開アプリ／農水省の研究成果を利用

<!-- _notes: 農林水産技術会議の研究成果によれば、診断付き画像を収集して識別プログラムを開発し、企業がスマートフォンアプリを公開した。研究成果の80%以上は当該評価条件での数値であり、全作物・全圃場での性能保証ではない。 -->
<!-- _sources: https://www.affrc.maff.go.jp/docs/project/seika/2022/r4_seikashu_02.html ; https://www.maff.go.jp/j/syouan/syokubo/gaicyu/datakatuyo/index.html -->

---
<!-- _class: sprayer -->
# カメラで雑草を見分け、必要な場所だけに散布する

## カメラ
作物と雑草を撮影

## AI
雑草の位置を推定

## ノズル
その位置だけに散布

## 実装段階
既存機は提供中。Gen 2は2027年モデル向け

<!-- _notes: See & Sprayは既に提供されているが、このスライドと動画で示すGen 2の標準搭載は2027年モデルからというメーカー説明。2026年10月時点でGen 2が普及済みとは扱わない。対象作物・薬剤・地域は仕様に依存する。 -->
<!-- _sources: https://www.deere.com/en-us/products-solutions/sprayers-and-applicators ; https://www.youtube.com/watch?v=OqIRBgDKtAQ -->

---
<!-- _class: video -->
# 公式動画で、識別から局所散布までを確かめる

## John Deere｜See & Spray Gen 2
2026年公開のメーカー公式動画

## 観察ポイント
カメラ・判断・ノズルの連動を見る

<!-- _video: https://www.youtube.com/watch?v=OqIRBgDKtAQ -->
<!-- _notes: PowerPointのオンライン動画として挿入。2026年10月30日にPowerPointのスライドショーでコンテンツを有効化した後、公式動画の再生が0:02まで進むことを確認。再生にはインターネット接続と外部メディアの許可が必要。公式YouTubeの公開設定やPowerPointのWeb再生環境によって再生できない場合は「公式動画をブラウザーで開く」を利用。 -->
<!-- _sources: https://www.youtube.com/watch?v=OqIRBgDKtAQ -->

---
<!-- _class: compare -->
# 同じ画像認識でも、レーザー除草は作業の仕方が異なる

## 画像認識
作物と雑草の位置を推定

## ロボットの動作
対象の雑草へレーザーを照射

## 実装段階
Carbon Roboticsの市販機。性能はメーカー公表値

<!-- _notes: LaserWeeder G2は市販機としてメーカーが紹介している。除草剤を使わない方式だが、栽培体系・安全管理・設備費などの条件を伴う。元資料4枚目の旧型デモ動画の代わりに、2025年公開の公式G2動画を使用。 -->
<!-- _sources: https://carbonrobotics.com/laserweeder ; https://carbonrobotics.com/laserweeding-technology ; https://www.youtube.com/watch?v=wYyW2mEgXDk -->

---
<!-- _class: video -->
# 公式動画で、画像認識とレーザー照射を確かめる

## Carbon Robotics｜LaserWeeder G2
2025年公開のメーカー公式動画

## 観察ポイント
雑草の位置推定と照射の関係を見る

<!-- _video: https://www.youtube.com/watch?v=wYyW2mEgXDk -->
<!-- _notes: PowerPointのオンライン動画として挿入。2026年10月30日にPowerPointのスライドショーでCarbon Robotics公式動画の再生が0:01まで進むことを確認。再生にはインターネット接続と外部メディアの許可が必要。メーカーのYouTube公開設定やPowerPointの再生環境にも依存する。 -->
<!-- _sources: https://www.youtube.com/watch?v=wYyW2mEgXDk -->

---
<!-- _class: case -->
# トマトの下葉処理では、AIが植物の形を認識する

## 入力
施設内のトマト株をカメラで撮影

## AIの仕事
主茎などの部位・形状を推定

## ロボットの仕事
主茎に沿って下葉を切除

## 実装段階
農研機構が開発・公開した研究成果

<!-- _notes: 農研機構2025年発表の研究開発事例。下葉処理を自動化する試作ロボットであり、一般の圃場への普及済み技術として扱わない。収穫を担うロボットとの混同を避ける。 -->
<!-- _sources: https://www.naro.go.jp/publicity_report/press/laboratory/iam/172523.html -->

---
<!-- _class: video -->
# 研究動画で、認識と下葉処理の連動を確かめる

## 農研機構｜トマト下葉処理ロボット
研究機関が公開した動作動画

## 観察ポイント
主茎の追跡と切除動作を見る

<!-- _video: https://www.youtube.com/watch?v=varnociD_mc -->
<!-- _notes: 農研機構の公式プレスリリースがリンクする動画をオンライン動画として挿入。再生にはインターネット接続が必要。PowerPoint上での実再生は現環境で未検証。 -->
<!-- _sources: https://www.naro.go.jp/publicity_report/press/laboratory/iam/172523.html ; https://www.youtube.com/watch?v=varnociD_mc -->

---
<!-- _class: compare -->
# 魚の画像認識は、撮影できた範囲を数える

## できること
写った魚の検出・分類・計数を補助する

## 追加で必要なこと
撮影範囲、濁り、重複撮影、見逃しを評価する

## 言える範囲
「水域の全個体数が自動でわかる」とは限らない

<!-- _notes: 元資料45枚目は魚の種や個体数が自動でわかると断定している。AIの結果は観測画像に条件づけられ、母集団の推定には調査設計と検出率の評価が必要。カエルの研究事例は維持する。 -->
<!-- _sources: https://www.fisheries.noaa.gov/resource/peer-reviewed-research/estimating-precision-and-accuracy-automated-video-post-processing -->

---
<!-- _class: flow -->
# 実用例を比べると、AIの精度だけでは導入を決められない

## 認識
対象作物・雑草・病害虫に適合するか

## 運用
圃場条件と安全対策を満たすか

## 効果
作業時間・投入資材・費用を現場で検証する

## 段階
市販・実証・研究開発を混同しない

<!-- _notes: 元資料60枚目の将来像を、現場への導入判断として更新。AIという名称だけで性能を推定せず、対象・運用・費用・検証段階を問う。農水省の技術カタログ自体も技術効果の認定ではないと明記している。 -->
<!-- _sources: https://www.maff.go.jp/j/kanbo/smart/smart_agri_technology/smartagri_catalog.html -->
