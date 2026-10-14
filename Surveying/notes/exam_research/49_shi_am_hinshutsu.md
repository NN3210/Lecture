# 測量士試験「午前」の頻出論点と測量士補との違い（Web 記事の整理）

取得日: 2026-10-14。担当課題 49。WebSearch / WebFetch で確認できた内容のみを記す。
予備校・個人ブログ・Q&A サイトが中心で、公式の出題統計ではない。**頻出論点を数値で集計した記事は見つからなかった**ため、下の分野別表は各記事の記述を担当者が突き合わせたもの（推測を含む）である。

## 収集した資料一覧
| No. | 資料名 | URL | 種類 | 要点 |
|---|---|---|---|---|
| 1 | 東京法経学院 令和8年 測量士・測量士補試験 出題傾向と分析 | https://www.thg.co.jp/soku/sokuho/bunseki.htm | 記事（予備校） | 令和8年の士午前を問番号別に分析。士・士補とも28問中計算10問（約35%）。士は新出問題が少なめ。法規の細条文・写真測量の計算・新傾向が難しめ |
| 2 | ジョブハウス建設 測量士の過去問…科目別の出題傾向 | https://jobhouse.jp/construction/columns/1961 | 記事 | 午前の問番号と分野の対応表、科目別の頻出論点、計算問題は約40パターンに分類可。表と本文に不整合あり |
| 3 | アガルート 測量士試験の試験内容 | https://www.agaroot.jp/sokuryoshi/column/contents-of-the-exam/ | 記事（予備校） | 午前は5肢択一28問・700点、450点（18問）未満は午後不採点。分野ごとの計算有無（法規は計算なし、測地測量はベクトル計算が出やすい） |
| 4 | アガルート 測量士試験の難易度 | https://www.agaroot.jp/sokuryoshi/column/difficulty-level/ | 記事（予備校） | 士は土台が士補と同範囲で「深く多面的」に問う。数学（特に行列）・新技術（ICT/UAV）・地図投影/GISが重点。士補学習者は学習時間を短縮できると主張 |
| 5 | アガルート 測量士の勉強法 | https://www.agaroot.jp/sokuryoshi/column/how-to-study/ | 記事（予備校） | 午前の計算は実務と切り離して型で覚える（40パターン超）。関数電卓の使い方。士補への言及なし |
| 6 | アガルート 測量士と測量士補の違い | https://www.agaroot.jp/sokuryoshi/column/difference/ | 記事（予備校） | 合格率（士10%前後、士補30〜50%）、勉強時間（約300h／約200h）、年度別合格率表。出題内容の比較はなし |
| 7 | アガルート 測量士過去問解説（5年分） | https://www.agaroot.jp/sokuryoshi/column/past-questions/ | 記事（予備校） | 間違えやすい例として三次元直交座標の回転、正規分布、クロソイド曲線（午前）。午前・午後必須は過去問が繰り返されやすい、と記載 |
| 8 | アガルート 午前 文章問題講座／計算問題講座 | https://www.agaroot.jp/sokuryoshi/bunsyo/ , https://www.agaroot.jp/sokuryoshi/keisan/ | 講座紹介 | 過去10年の午前文章問題から頻出テーマを抽出、計算問題はほぼ網羅するとあるが論点名は非掲載 |
| 9 | 測量士試験顛末記（Zenn 個人記事） | https://zenn.dev/boiledorange73/articles/0054-surveyer-exam-rep | 個人ブログ | 午前は士補と同形式（28問×25点）。午前は「きっちり点が出る」、午後は時間不足で厳しい。筆者午前は550点（約79%） |
| 10 | 東京法経学院 誤差・座標計算を得点源にする勉強法 | https://www.thg.co.jp/douyo/shikaku/sokuryoshiho/is-calculation-ability-the-key-to-the-surveyor-exam-study-methods-to-turn-errors-and-coordinate-calculations-into-points/ | 記事（予備校） | 誤差論（偶然誤差・標準偏差・加重平均・誤差伝播）と座標計算（平面直角座標、方位角）は「毎年のように出題」 |
| 11 | 東京法経学院 午前問題で迷わず解く演習テクニック | https://www.thg.co.jp/douyo/shikaku/sokuryoshiho/practice-techniques-to-develop-the-ability-to-solve-the-morning-questions-of-the-surveyor-exam-without-hesitation/ | 記事（予備校） | 午前は出題傾向が安定、分野別演習が有効。迷いやすい点は法の適用範囲の細条文など。論点の列挙は乏しい |
| 12 | 測量士資格試験 基本的な戦略（note 個人記事） | https://note.com/tkc_exp/n/nea367e2609f1 | 個人ブログ | 午前は過去問反復で8割以上を狙う。午後選択の難易（地図編集はJPGIS暗記中心、基準点・応用は計算重い） |
| 13 | ファーストコンテック 測量士の合格率…難しい訳 | https://first-contech.co.jp/blog/surveyor_difficulty_study-points | 記事（企業ブログ） | 士が難しい理由=数学・実務問題・幅広さ。数学は三角関数・正弦/余弦定理・行列・確率。計算は過去問類似が出る。合格率 士12.6%／士補35.7%（過去5年） |
| 14 | Yahoo!知恵袋「午前は士補の参考書で足りるか」 | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q13324376948 | Q&A | 士補合格者の質問に対する回答3件（士補との関係の証言。下記） |
| 15 | 中山 測量士補の過去問は何年分やるか | https://nakayama-yusuke.com/nakayama-kakomon_nannen/ | 個人サイト | 士補（H30）の再出題率分析。1年分で40.7%、5年分で74.1%、9年分で80.7%。士の分析はなし |
| 16 | 令和3年 測量士午前 第15問（標準偏差）解説 | https://surveyorexam.com/ (令和3年測量士試験 第15問) | 個人ブログ | TS放射法の高低差の標準偏差（誤差伝播）。微分・統計が苦手なら捨て問も、と記載 |

補助的に確認した検索結果（本文は未精読）: アガルート「写真測量の基本情報」（https://www.agaroot.jp/sokuryoshi/column/syasinssokuryou/）、アガルート「測量士補から測量士へ」（https://www.agaroot.jp/sokuryoshi/column/stepup-surveyor/ 、士補との差の詳細は取得できず）、アガルート「測量士と測量士補の違い（調査士向け）」（https://www.agaroot.jp/chousashi/column/sokuryoushi-difference/ 、午前の出題差の記述なし）。

## 内容の要約

### 1. 試験の構造（士午前）
- 5肢択一28問、1問25点、700点満点。士補と同形式（資料3, 9）。
- 試験時間は士が2時間30分、士補が3時間（資料1）。
- 足切り: 資料3と検索結果の他ページは「450点（18問）未満は午後不採点」。一方、資料9・12・13は「午前400点以上」と記載しており**出典間で不一致**。資料9は士補を450点（18問）、士を400点（16問）としている。年度による変更の可能性があり、最新は国土地理院の案内で要確認（担当課題の指定は450点）。
- 総合は午前午後で1400点中910点（資料3, 6, 9, 12, 13）。

### 2. 士補との違いに関する記述
- 範囲: 「大まかに同じで、士は士補の内容を深く多面的に問う」「計算問題にも一部共通する出題がある」（資料4）。士の科目に追加されるのは地理情報システム（検索結果の科目表）。
- 難度: 合格率は令和8年が士24.2%／士補44.4%、令和7年が40.2%／51.2%、令和6年が13.0%／31.4%（資料6、国土地理院データとして掲載）。
- 計算の重さ: 令和8年は士・士補とも計算問題が28問中10問（約35%）で同程度（資料1）。ただし質は異なり、Q&A回答に「計算問題などで士補より一段ひねった出題」がある（資料14）。
- 新技術の比率: 士は新傾向の出題が比較的少ない年がある一方（令和8年、資料1）、資料4は「ICT・ドローンは出題されやすく、改正点もすぐ問われる」と述べる。令和8年は写真測量・UAV分野(No.19)に新傾向があった（資料1）。比率の定量データは見つからなかった。
- 午後は士のみ（記述式）。士補は択一のみ（資料2, 4）。

### 3. 士補の知識でどの程度解けるか（出典付き）
- 「午前は測量士補の内容でおおむね網羅できるが、計算問題などで一段ひねりがある」（資料14 回答2、個人の意見）。
- 「午前は士補の延長線上。まず士補で9割程度取れるようにしてから午前対策へ」（資料14 回答1、個人の意見）。
- 士補学習者は「全体像を把握済みで、学習時間を大きく短縮できる」（資料4、予備校の主張。根拠となる数値は示されていない）。
- 士補合格による試験免除はない（検索結果のアガルート別ページ）。
- **「士補の知識で何割取れる」という数値を示した記事は見つからなかった**。参考として、士補の過去問を3年分繰り返すと次年度士補試験の肢の約61%、5年分で約74%が既出という分析がある（資料15、士補自身の再出題率であり、士午前の得点率ではない）。個人の午前得点の例は約79%（資料9、士補との関係は不明）。

### 4. 頻出論点の分野別まとめ
記事が名指しした論点を、担当者が士補との共通性で分類した。「出現記事」は上記資料番号。
推測: 「士補と共通の型」は士補の出題範囲（測量士補の科目に含まれる）に基づく担当者の判断で、記事が明示したものではない。

| 分野 | 論点（記事が挙げたもの） | 出現記事 | 区分 |
|---|---|---|---|
| 測量法規 | 測量法・作業規程の準則の条文、測量成果の取扱い、法の適用範囲などの細条文（令和8年は問1〜4。難しめの評価） | 1, 2, 3, 11, 12 | 共通の型（ただし士は条文が細かい） |
| 測量の基礎（誤差・数学） | 誤差伝播（TS高低差の標準偏差）、標準偏差、加重平均、偶然誤差 | 1, 10, 16 | 士で重い。誤差伝播の一般式（偏微分）は士補より一段上（推測） |
| 測量の基礎（誤差・数学） | 正規分布、三次元直交座標の回転、行列、確率、三角関数・正弦/余弦定理 | 4, 7, 13 | 士のみで出る型 |
| 多角測量（TS等） | 角度・距離の誤差、点検・定数補正、多角測量の誤差計算、座標計算・方位角 | 1, 2, 10 | 共通の型 |
| GNSS測量 | 観測方法、観測精度、基準点測量のGNSS観測作業。令和8年に新傾向あり | 1, 2, 3 | 共通の型＋新傾向（士で深い） |
| GNSS／測地系 | ITRF・ジオイド・セミダイナミック補正 | 該当記事なし | 記事では確認できず。出題の有無は過去問PDFで確認が必要 |
| 水準測量 | 往復観測の較差計算、標尺の補正（資料2のみ）。誤差要因は記事では確認できず | 2 | 共通の型 |
| 地形測量・写真測量 | 縮尺・比高・撮影高度、撮影基線長、重複度、空中三角測量、UAV写真測量・レーザ測量 | 1, 2, 4 | 共通の型（計算）＋新技術（UAV等） |
| 地図編集・GIS | 地図投影法（UTM）、GISデータ構造・データの種類、地図記号、JPGIS（午後側の記述） | 1, 2, 4, 12 | 投影・GISは士で深い（士のみの科目: 地理情報システム） |
| 応用測量 | 曲線（クロソイド等）の計算、平面直角座標の計算、河川測量、面積計算 | 1, 2, 7, 12 | クロソイド・河川は共通。面積計算は午後選択側の記述が多い |

集計上の留意:
- 基盤地図情報・地理院タイルを名指しした記事は見つからなかった。
- 面積計算は、午前ではなく午後選択（応用測量）の論点として挙げる記事が多い（資料2のみ午前の応用測量に記載）。
- 令和8年の計算問題の所在は、No.3(三角関数)・No.6(TS点検)・No.15(誤差伝播)・No.17(写真測量の縮尺・比高)・No.26(曲線)・No.27(平面直角座標の平行移動・相似)（資料1）。

### 5. 気づき
- 士午前の「型」は、士補と共通の知識（法規・TS・GNSS・写真測量・クロソイド）に、誤差伝播・行列・座標回転・正規分布などの数学が上乗せされた形と読める。
- 予備校の記事は、論点名より「過去問の反復」「計算を約40パターンで覚える」を強調する傾向がある。
- 授業資料の観点では、士午前対応の補足として誤差伝播（偏微分）と座標変換（回転行列）を取り上げる価値がある（推測）。

## 出典
- https://www.thg.co.jp/soku/sokuho/bunseki.htm
- https://jobhouse.jp/construction/columns/1961
- https://www.agaroot.jp/sokuryoshi/column/contents-of-the-exam/
- https://www.agaroot.jp/sokuryoshi/column/difficulty-level/
- https://www.agaroot.jp/sokuryoshi/column/how-to-study/
- https://www.agaroot.jp/sokuryoshi/column/difference/
- https://www.agaroot.jp/sokuryoshi/column/past-questions/
- https://www.agaroot.jp/sokuryoshi/bunsyo/
- https://www.agaroot.jp/sokuryoshi/keisan/
- https://www.agaroot.jp/sokuryoshi/column/stepup-surveyor/
- https://www.agaroot.jp/chousashi/column/sokuryoushi-difference/
- https://zenn.dev/boiledorange73/articles/0054-surveyer-exam-rep
- https://www.thg.co.jp/douyo/shikaku/sokuryoshiho/is-calculation-ability-the-key-to-the-surveyor-exam-study-methods-to-turn-errors-and-coordinate-calculations-into-points/
- https://www.thg.co.jp/douyo/shikaku/sokuryoshiho/practice-techniques-to-develop-the-ability-to-solve-the-morning-questions-of-the-surveyor-exam-without-hesitation/
- https://note.com/tkc_exp/n/nea367e2609f1
- https://first-contech.co.jp/blog/surveyor_difficulty_study-points
- https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q13324376948
- https://nakayama-yusuke.com/nakayama-kakomon_nannen/
- https://surveyorexam.com/ （令和3年測量士試験 第15問）
