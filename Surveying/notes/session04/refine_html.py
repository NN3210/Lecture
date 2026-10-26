"""初稿HTMLに、検証で見つかった操作の修正と教材の統一を反映する。"""
from pathlib import Path
import re

root=Path(__file__).resolve().parents[2]
p=root/'materials/slides/第04回_角測量/explanation.html'
h=p.read_text(encoding='utf-8-sig')
h=h.replace('details>*{display:block!important}', 'details>:not(summary){display:block!important}details>summary{display:none!important}')
h=h.replace('html{scroll-behavior:smooth}', 'html{scroll-behavior:smooth}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}:focus-visible{outline:3px solid #166b68;outline-offset:3px}')
h=h.replace('R<sub>kj</sub>（正の結果）とL<sub>kj</sub>（反の結果）','p<sub>kj</sub>（正の結果）とq<sub>kj</sub>（反の結果）')
h=h.replace('R<sub>kj</sub>＋L<sub>kj</sub>', 'p<sub>kj</sub>＋q<sub>kj</sub>').replace('R<sub>kj</sub>－L<sub>kj</sub>', 'p<sub>kj</sub>－q<sub>kj</sub>')
h=h.replace('平均40.000834°', '平均40.000833°')
h=h.replace('id="face-l" type="number"','id="face-l" min="0" max="359.999999" type="number"').replace('id="face-r" type="number"','id="face-r" min="0" max="359.999999" type="number"')
# 操作1の図は、入力した二つの読定と同時に更新する。
wrap_svg='''<figure class="figure"><svg id="wrap-svg" viewBox="0 0 460 450" role="img" aria-labelledby="wrap-title wrap-desc"><title id="wrap-title">入力した水平角</title><desc id="wrap-desc">目盛の0度を上とし、基準と目標の方向および時計回りの開きを表示する。</desc><circle cx="230" cy="230" r="155" fill="none" stroke="#cfd9dd" stroke-width="2"/><text x="213" y="36">0°</text><text x="400" y="236">90°</text><text x="204" y="427">180°</text><text x="6" y="236">270°</text><line id="wrap-ray-a" class="guide"/><line id="wrap-ray-b" class="main"/><path id="wrap-arc" class="arc"/><circle cx="230" cy="230" r="6" class="dot"/><text id="wrap-label-a"/><text id="wrap-label-b"/><text x="220" y="260">O</text></svg><figcaption>破線が基準、実線が目標。円弧は時計回りです。</figcaption></figure>'''
h=h.replace('<button type="button" id="wrap-go">',wrap_svg+'<button type="button" id="wrap-go">')
h=h.replace('<button type="button" id="face-go">','<p>二つの読定は0°以上360°未満。この操作では、反が正＋180°から±1°以内の入力を扱います（観測の合格基準ではありません）。</p><button type="button" id="face-go">')
# 偏心図に操作対象の名前を付ける。
h=h.replace('<line class="warn" x1="195" y1="335" x2="145" y2="55"/>','<line id="ecc-ray-a" class="warn" x1="195" y1="335" x2="145" y2="55"/>')
h=h.replace('<line class="warn" x1="195" y1="335" x2="525" y2="335"/>','<line id="ecc-ray-b" class="warn" x1="195" y1="335" x2="525" y2="335"/>')
h=h.replace('<line class="warn" x1="145" y1="335" x2="195" y2="335"/>','<line id="ecc-shift" class="warn" x1="145" y1="335" x2="195" y2="335"/>')
h=h.replace('<circle cx="195" cy="335" r="8" fill="#a94737"/>','<circle id="ecc-dot" cx="195" cy="335" r="8" fill="#a94737"/>')
h=h.replace('<text x="200" y="375">E (0,1)</text>','<text id="ecc-label" x="200" y="400">E (0,1)</text>')
h=h.replace('<text x="155" y="318" fill="#a94737">偏心1 m</text>','<text id="ecc-distance" x="155" y="310">偏心1 m</text>')
h=h.replace('偏心OEは見えるように大きく描いており、縮尺どおりではありません。','偏心OEは操作に連動します。ずれが見えるように大きく描き、縦横も同じ縮尺ではありません。角の数値は正確な座標から計算します。')
h=h.replace('A方向</td><td>359.427061°</td><td>0°</td><td>+0.572939°','A方向</td><td>359.427061°</td><td>0°</td><td>+0.572939°（一周を調整）')
# リセットは全操作に備え、ブラウザのフォーム動作にも依存しない。
h=h.replace('</button><p class="result" id="wrap-result"','</button> <button type="reset" id="wrap-reset">例に戻す</button><p class="result" id="wrap-result"')
h=h.replace('</button><p class="result" id="face-result"','</button> <button type="reset" id="face-reset">例に戻す</button><p class="result" id="face-result"')
h=h.replace('<p class="result" id="ecc-result"','<button type="reset" id="ecc-reset">1 mに戻す</button><p class="result" id="ecc-result"')
# 方向法の式だけでなく、秒の小さい表を追加する。
direction_example='''<h3>B方向で、実際に比べてみる</h3><div class="wide"><table><caption>下表の「13″」などは共通の73°25′を省略した秒値です。教材用の架空値。</caption><thead><tr><th>対回</th><th>正の結果 p</th><th>反の結果 q</th><th>較差 C=p−q</th><th>倍角の秒位 p+q</th></tr></thead><tbody><tr><td>1</td><td>15″</td><td>11″</td><td>+4″</td><td>26″</td></tr><tr><td>2</td><td>9″</td><td>11″</td><td>−2″</td><td>20″</td></tr></tbody></table></div><p>倍角差は26″−20″＝6″。観測差は4″−(−2″)＝6″です。比べるのは同じB方向の、異なる対回です。平均角の対回差3″と、倍角差6″も区別します。</p>'''
h=h.replace('<h3>方向法と倍角法は別</h3>',direction_example+'<h3>方向法と倍角法は別</h3>')
# 器械の説明を点検結果に合わせて補足。
instrument='''<h3>目盛盤の中心ずれと、目盛の不ぞろい</h3><p><strong>目盛盤偏心</strong>は目盛円の中心と回転中心のずれです。対向する位置の読取りや、機器内の処理で影響を小さくします。一方、<strong>分画誤差</strong>は各目盛間隔の不ぞろいです。複数の対回で円周の異なる部分を使って平均します。電子TSでは表示を0°にするだけで物理的な読取り位置が変わるとは限らないため、使用機種の手順に従います。</p>'''
h=h.replace('<section id="direction">',instrument+'<section id="direction">')
h=h.replace('この授業の<span class="term">方向角</span>', '真北は地理的な北、座標北は地図のX軸の北、磁北は磁石が示す北です。この授業の<span class="term">方向角</span>')
# 配布演習と同じ判定・学習目標へ統一。
start=h.index('<section id="practice">')
end=h.index('<section id="sources">')
practice='''<section id="practice"><h2>7　25分演習</h2><p><a href="../../exercises/第04回_角測量/exercise.md">配布問題（Markdown）</a>と同じ条件で考えます。ここに必要な値も載せているので、このHTMLだけでも解けます。</p><h3>演習1（15分）：方向法の野帳を点検する</h3><div class="wide"><table><thead><tr><th>対回・方向</th><th>正 L</th><th>反 R</th></tr></thead><tbody><tr><td>1・A始</td><td>12°15′20″</td><td>192°15′26″</td></tr><tr><td>1・B</td><td>85°40′35″</td><td>265°40′37″</td></tr><tr><td>1・A閉</td><td>12°15′25″</td><td>192°15′29″</td></tr><tr><td>2・A始</td><td>102°07′40″</td><td>282°07′36″</td></tr><tr><td>2・B</td><td>175°32′49″</td><td>355°32′47″</td></tr><tr><td>2・A閉</td><td>102°07′35″</td><td>282°07′39″</td></tr></tbody></table></div><ol><li>正・反の各列でA始を引き、Bの結果p・qを求める。</li><li>較差C=p−q、倍角D=p+q、平均角を求める。</li><li>同じB方向の対回間で、倍角差と観測差を求める。</li><li>正・反それぞれでA閉−A始の帰零差を求める。</li></ol><p class="warning">授業用の仮基準：倍角差8″以下、観測差5″以下、各帰零差の絶対値6″以下。すべて満たすときだけ採用します。公共測量の規程値ではありません。</p><details><summary>解答と途中計算を開く</summary><p>第1対回はp=73°25′15″、q=73°25′11″なので、C=+4″、D=146°50′26″、平均73°25′13″。第2対回はp=73°25′09″、q=73°25′11″なので、C=−2″、D=146°50′20″、平均73°25′10″です。</p><p>倍角差は6″、観測差は4−(−2)=6″。帰零差は第1対回が正+5″・反+3″、第2対回が正−5″・反+3″。観測差6″が仮の許容値5″を超えるため、原因を確認して再測します。平均73°25′11.5″は点検前の仮計算値であり、このまま成果として採用しません。</p></details><h3>演習2（10分）：偏心した観測を中心へ戻す</h3><p>O=(0,0)、E=(0,1)、A=(100,0)、B=(0,100) m。X北、Y東です。直角三角形OEAの小さい角をδとし、tanδ=1/100を使います。電卓はDEG（度）モードにします。</p><ol><li>Eから時計回りにA→Bを見る角を求める。</li><li>EAとEBの距離を求める。</li><li>O中心の角・距離を求め、「中心値−Eでの観測値」の補正量を符号付きで答える。</li></ol><details><summary>解答と途中計算を開く</summary><p>δ=tan⁻¹(1/100)=0.572938698°。Eでの角は90°+δ=90.572938698°（約90°34′22.58″）。EA=√10001=100.004999875 m、EB=99 mです。</p><p>O中心では角90°、OA=OB=100 m。補正は角−0.572938698°、A距離−0.004999875 m（約−0.0050 m）、B距離+1 m。Eでの角はOより大きく、Aまでの斜めの線は少し長く、Bまでは1 m近くなるからです。</p><p>これは既知の座標で仕組みを理解する例です。実際の偏心観測では、偏心距離と方向、目標への観測角・距離を使って未知の中心値を復元します。</p></details><h3>出口問題</h3><ol><li>350°から20°へ時計回りに回る角は？</li><li>正反平均でも消えない誤差を一つ挙げる。</li><li>天頂角Zと高低角αの関係は？</li><li>許容値を超えたら、どうする？</li></ol><details><summary>解答を開く</summary><p>30°。鉛直軸の傾きや求心誤差など。α=90°−Z。観測値を都合よく書き換えず、原因を確認して再測します。</p></details><p class="callout">次回は、角で決めた「向き」と距離を使って、次の点の座標をつなぎます。第5回はトラバース測量です。</p></section>\n'''
h=h[:start]+practice+h[end:]
h=h.replace('</ul><p><a href="#top">','<li><a href="https://www.jsurvey.jp/20220705P59-2.pdf">日本測量協会：高度定数の較差の解説</a></li><li><a href="https://www.chosashi.or.jp/media/01_chosoku.pdf">土地家屋調査士会連合会：調査・測量実施要領（方向観測の記載要領。規程値の転用はしない）</a></li><li><a href="https://help.fieldsystems.trimble.com/siteworks/en/measuring-total-station-leveling.htm">メーカー資料：TSの整準と二軸補正</a></li></ul><p><a href="#top">')
script=r'''<script>
const byId=id=>document.getElementById(id);
const fmt=n=>{const sign=n<0?'−':'';let t=Math.round(Math.abs(n)*3600);const d=Math.floor(t/3600);t%=3600;const m=Math.floor(t/60),s=t%60;return `${sign}${d}°${String(m).padStart(2,'0')}′${String(s).padStart(2,'0')}″`};
const fixed=(n,d=6)=>{const s=(Math.round((Math.abs(n)+Number.EPSILON)*10**d)/10**d).toFixed(d);return n<0?'−'+s:s};
function readAngle(id){const raw=byId(id).value.trim();if(raw==='')return null;const v=Number(raw);return Number.isFinite(v)&&v>=0&&v<360?v:null}
function setAttrs(id,attrs){const el=byId(id);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)))}
function wrap(){const a=readAngle('wrap-start'),b=readAngle('wrap-end'),o=byId('wrap-result');if(a===null||b===null){o.textContent='0以上360未満の値を入力してください。';return}const d=(b-a+360)%360,add=b<a?360:0;o.textContent=add?`${b}＋360－${a}＝${d.toFixed(3).replace(/\.000$/,'')}°`:`${b}－${a}＝${d.toFixed(3).replace(/\.000$/,'')}°`;const xy=(angle,r)=>[230+r*Math.sin(angle*Math.PI/180),230-r*Math.cos(angle*Math.PI/180)];for(const [v,n] of [[a,'a'],[b,'b']]){const [x,y]=xy(v,155);setAttrs('wrap-ray-'+n,{x1:230,y1:230,x2:x,y2:y});const [tx,ty]=xy(v,110);setAttrs('wrap-label-'+n,{x:tx+(n==='a'?-50:12),y:ty+(n==='a'?-12:18)});byId('wrap-label-'+n).textContent=(n==='a'?'基準':'目標')+` ${v}°`}const [x1,y1]=xy(a,72),[x2,y2]=xy(b,72);setAttrs('wrap-arc',{d:d===0?'':`M${x1},${y1} A72,72 0 ${d>180?1:0} 1 ${x2},${y2}`});byId('wrap-desc').textContent=`基準${a}度、目標${b}度、時計回りの角${d.toFixed(3)}度。`}
function faces(){const l=readAngle('face-l'),r=readAngle('face-r'),o=byId('face-result');if(l===null||r===null){o.textContent='二つの読定を0以上360未満で入力してください。';return}let rc=(r+180)%360;rc+=Math.round((l-rc)/360)*360;if(Math.abs(rc-l)>1){o.textContent='二つの読定を確認してください。反は正＋180°付近（この操作では±1°以内）です。';return}const mean=((l+rc)/2+360)%360;o.textContent=`反を${fixed(rc)}°へ換算 → 平均${fixed(mean)}°（約${fmt(mean)}）`}
function eccentric(){const e=Number(byId('ecc').value),delta=Math.atan(e/100)*180/Math.PI,angle=90+delta;byId('ecc-value').value=`${e.toFixed(1)} m`;byId('ecc-result').textContent=`Eでの角 ${fixed(angle)}° → Oの角90°へ戻す補正 ${fixed(-delta)}°`;const x=145+e*30;setAttrs('ecc-ray-a',{x1:x});setAttrs('ecc-ray-b',{x1:x});setAttrs('ecc-shift',{x2:x});setAttrs('ecc-dot',{cx:x});setAttrs('ecc-label',{x:x+8,y:400});byId('ecc-label').textContent=`E (0,${e.toFixed(1)})`;byId('ecc-distance').textContent=`偏心 ${e.toFixed(1)} m`;byId('e-desc').textContent=`器械Eが測点Oから東へ${e.toFixed(1)}mずれた図。表示のずれは誇張。Eでの水平角は${angle.toFixed(6)}度。`}
byId('wrap-go').addEventListener('click',wrap);byId('face-go').addEventListener('click',faces);byId('ecc').addEventListener('input',eccentric);
byId('wrap-reset').addEventListener('click',()=>{byId('wrap-start').value=350;byId('wrap-end').value=20;wrap()});byId('face-reset').addEventListener('click',()=>{byId('face-l').value=40.001667;byId('face-r').value=220;faces()});byId('ecc-reset').addEventListener('click',()=>{byId('ecc').value=1;eccentric()});
document.querySelectorAll('input[type=number]').forEach(el=>el.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();el.id.startsWith('wrap')?wrap():faces()}}));
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>d.open);document.querySelectorAll('details').forEach(d=>d.open=true)});window.addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((d,i)=>d.open=printState[i]??false));
wrap();faces();eccentric();
</script>'''
h=re.sub(r'<script>.*?</script>',lambda _:script,h,flags=re.S)
p.write_text(h,encoding='utf-8')
print('HTML refined')
