"""検算・教材統合で得た修正をスライド原稿へ反映する（再実行可）。"""
from pathlib import Path
import json

base=Path(__file__).resolve().parent
for f in sorted(base.glob('slides_part*.json')):
    slides=json.loads(f.read_text(encoding='utf-8-sig'))
    for d in slides:
        i=d['id']
        d['ref']='angle' if i<=9 else 'setup' if i<=14 else 'faces' if i<=20 else 'direction' if i<=34 else 'vertical' if i<=40 else 'eccentric' if i<=48 else 'practice'
        if i==2:
            d['lines']=['角の読み方と、測り方を説明できる？','方向法の野帳を点検できる？','偏心した観測を中心へ戻せる？']
        if i==5:
            d.update(kind='diagram',lead='同じ視準線を、水平と真上から測り分ける',lines=['高低角α：水平から、上を正','天頂角Z：真上から測る','α＋Z＝90°'])
        if i==11:d['lead']='視準軸と水平軸、水平軸と鉛直軸は直交する'
        if i==12:
            d.update(kind='diagram',lead='求心は「どこに置くか」。中心を測点に合わせる',lines=['鉛直軸の延長がOを通る','傾きがなくても、中心はずれる'],diagramOptions={'mode':'centering'})
        if i==13:
            d.update(kind='diagram',title='整準は、鉛直軸を鉛直にする',lead='整準は「どちらを向くか」。軸の傾きを直す',lines=['重力方向と鉛直軸をそろえる','正反平均では傾きは消えない'],diagramOptions={'mode':'leveling'})
        if i==18:d.pop('diagram',None)
        if i==19:d['title']='目盛盤偏心は、二つの中心のずれ'
        if i==20:
            d.update(kind='diagram',title='円の別の部分を使い、分画誤差を分散する',lead='目標は同じ。円の異なる部分を使って測る',lines=['目盛間隔の不ぞろいを平均する','表示を0°にするだけとは限らない'])
        if i==21:
            d['diagramOptions'].update(angle=73.42,thirdAngle=142.30)
        if i==22:d['diagramOptions']['angle']=73.42
        if i==27:d['lines']=['教材用の架空データ','帰零差：正＋5″、反＋3″']
        if i==28:d['lines']=['教材用の架空データ','帰零差：正−5″、反＋3″']
        if i==33:
            d['title']='超過を見つけたら、原因確認と再測'
            d['rows'][2]=['帰零差','最大5″','6″以内','可']
            d['notes']=d['notes'].replace('最大4″','最大5″')
        if i==34:
            d['title']='方向法と倍角法は、観測の仕方が違う'
            d['lead']='複数の方向を読む方法と、一つの角を積み重ねる方法'
            d['lines']=['倍角法の計算は宿題。読定差120°を3回の反復で得たら？']
            if '宿題の答' not in d['notes']:d['notes']+=' 宿題の答は120°÷3=40°です。角の累積読定では、一周をまたぐ回数も含めた連続値を使います。'
        if i==39:
            d['lines']=['正読定に加える補正は−12″','高度定数の較差にはKを用いる']
        if i==43:
            d['title']='三角比で、方向のずれδを求める'
            d['steps']=['tan δ＝1/100','δ＝tan⁻¹(0.01)＝0.5729386977°','秒へ換算：δ≈0°34′22.58″']
            d['result']='∠AEB≈90.572939°'
        if i==44:
            d['result']='角補正≈−0.572939°'
            d['steps'][2]='補正＝90°−(90°＋δ)＝−δ'
        if i==45:
            d['rows'][0]=['A','100.0050 m','100.0000 m','−0.0050 m']
            d['lines']=['A：斜めで少し長い　B：1 m近く見える','表示は0.0001 mに丸め。計算途中は丸めない。']
        if i==46:
            d['title']='小角近似では、単位はラジアン'
            d['left']=['δ≈e/r［rad］','1/100＝0.01 rad','180/π倍すると約0.573°']
            d['lines']=['e：横方向のずれ、r：目標までの距離','ずれが距離より十分小さいときに使う']
        if i==48:
            d['left']=['目標への自動視準・追尾','作動範囲内の二軸補正','読定・記録の支援']
            d['right']=['目標の取り違え・追尾喪失','求心・据付の安定性','許容値超過と再測判断']
            d['sources']=['https://help.fieldsystems.trimble.com/siteworks/en/measuring-total-station-leveling.htm','https://help.fieldsystems.trimble.com/sps-series-total-station/autolock-technology.htm']
        if i==49:
            d['lines']=['正・反で別々にA始を引く','配布問題の計算表を使う（15分）']
        if i==50:
            d['lines']=['授業用の仮基準：倍角差≤8″、観測差≤5″','各帰零差の絶対値≤6″（公共測量の規程値ではない）']
        if i==52:
            d['diagram']='eccentric'
            d['question']='Eの角と距離を、O中心へ戻そう'
            d['lines']=['X北・Y東。図の座標はm。','δ＝tan⁻¹(1/100)、電卓はDEG','補正＝中心O−偏心E']
        if i==54:
            d['question']='角と距離から、次の杭の座標を求める'
            d['lines']=['水平角で次の辺の向きを決める','距離を南北・東西の成分に分ける']
        if i==56:d['widths']=[12,18,35,35]
        if i==57:
            d['rows'][2]=['帰零差','最大5″','6″以下','可']
            d['widths']=[30,20,25,25]
        if i==58:
            d['steps']=['δ＝tan⁻¹(1/100)≈0.572939°','∠AEB＝90°＋δ≈90.572939°','EA＝√10001≈100.0050 m','EB＝100−1＝99 m']
            d['result']='角とA距離は増え、B距離は減る'
            d['lines']=[]
        if i==59:
            d['rows']=[['A→B角','90°','90.572939°','−0.572939°'],['A距離','100 m','100.0050 m','−0.0050 m'],['B距離','100 m','99 m','＋1.0000 m']]
            d['widths']=[19,19,31,31]
        if i==60:d['lines']=['350°→20°は30°','鉛直軸の傾きは正反で消えない','α＝90°−Z。超過なら原因確認・再測']
    f.write_text(json.dumps(slides,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Content refinements saved')
