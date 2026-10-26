# スライド原稿の共通仕様

最終説明は materials/slides/第04回_角測量/explanation.html を根拠にする。制作中の改善は最終統合で反映する。
原稿はUTF-8 JSONの配列。各要素は以下。

```json
{"id":1,"section":"角の意味","title":"水平角は上から見た開き","kind":"diagram","diagram":"horizontal","lead":"OAを基準に、時計回りでOBを見る","lines":["水平角 ∠AOB"],"notes":"高校生に語りかける2〜4文。図の読み方・例・注意点。","ref":"angle","sources":[]}
```

必須: id,title,kind,notes,ref。section、lead（45字以内）、lines（1〜3項、各30字程度）、sources URL配列。
kind: cover / diagram / number / calculation / compare / table / question / exercise / closing。
diagram: horizontal / radius / vertical / circle / offset / axes / setup / faces / cancellation / eccentric / north / traverse。
diagramは必要なら diagramOptions = {angle:60, ...}。全体の幾何・描画は親が担当。
number型: value（大きい数値）, unit（単位）, lines。
calculation型: steps（2〜4式文字列）, result（答）。
compare型: leftTitle,rightTitle,left（2〜3短文配列）,right（同）。
table型: headersとrows（3〜5列、4データ行以内が基本）。widthsを付けてもよい。DMSがある場合最大4列推奨。
question/exercise型: question（40字程度）, lines（ヒント）、tableかdiagramを組み合わせ可能。
closing型: question、diagram。

全体60枚程度（本編と演習、最後の復習用解答）。長い段落、カード3枚の羅列、装飾写真、内容のない目次は作らない。各枚で単位・読定値/結果・時計回りの規約を混同しない。記号の統一：生読定は正L・反R、零方向差引きの結果はp（正）・q（反）、較差C=p−q、倍角D=p+q。高度定数K、指標誤差i=K/2。
出典は研究メモのURLを適切なスライドnotesへ。例題の数字は教材用架空値と明示。
前後の接続・到達目標は本文に散りばめる。60–85分は演習2問。解答ページは授業後に参照する補足。
