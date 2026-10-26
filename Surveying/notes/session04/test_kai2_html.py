from pathlib import Path
import json,math
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'notes/session04/kai2/html_qa'
OUT.mkdir(exist_ok=True)
target=ROOT/'materials/slides/第04回_角測量/explanation_回2.html'
checks=[]
def check(name,ok,detail=''):
    checks.append(dict(name=name,pass_=bool(ok),detail=detail))
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page=browser.new_page(viewport={'width':1100,'height':900})
    errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.goto(target.as_uri())
    check('初期350→20は30°','30°' in page.locator('#wrap-result').inner_text())
    page.locator('#start').fill('20');page.locator('#end').fill('350');page.locator('#end').press('Enter')
    check('逆向き20→350は330°','330°' in page.locator('#wrap-result').inner_text())
    page.locator('#end').fill('20');page.locator('#end').press('Enter')
    check('同じ読定は0°','＝0°' in page.locator('#wrap-result').inner_text())
    for value in ['', '-1','360']:
        page.locator('#start').fill(value);page.locator('#wrap-form button').first.click()
        check('読定不正入力 '+repr(value),'入力してください' in page.locator('#wrap-result').inner_text())
    page.locator('#wrap-form button[type=reset]').click();page.wait_for_timeout(50)
    check('読みのreset','30°' in page.locator('#wrap-result').inner_text())
    page.locator('#common-error').fill('5');page.locator('#reverse-error').fill('12');page.locator('#reverse-error').press('Enter')
    check('共通5秒が平均に残る','平均 40°00′05.0″' in page.locator('#face-result').inner_text())
    page.locator('#reverse-error').fill('-12')
    check('反転誤差の符号を変えても共通成分不変','平均 40°00′05.0″' in page.locator('#face-result').inner_text())
    page.locator('#common-error').fill('');page.locator('#face-form button').first.click()
    check('空欄を0として黙って計算しない','入力してください' in page.locator('#face-result').inner_text())
    page.locator('#face-form button[type=reset]').click();page.wait_for_timeout(50)
    check('平均reset','平均 40°00′00.0″' in page.locator('#face-result').inner_text())
    text=page.locator('#ecc-result').inner_text()
    check('偏心デモの角・距離補正','−0°34′22.6″' in text and '-0.0050m' in text,text)
    before=page.locator('#ecc-dot').get_attribute('cx')
    page.locator('#ecc-e').fill('2');page.locator('#ecc-e').press('Enter')
    text=page.locator('#ecc-result').inner_text()
    check('偏心2mの逆正接','1.145763°' in text,text)
    check('偏心図と値が同期',page.locator('#ecc-dot').get_attribute('cx')!=before)
    page.locator('#ecc-s').fill('200')
    check('距離も2倍なら同じ角','0.572939°' in page.locator('#ecc-result').inner_text())
    page.locator('#ecc-e').fill('0')
    check('偏心0なら補正0','0°00′00.0″' in page.locator('#ecc-result').inner_text())
    page.locator('#ecc-e').fill('10');page.locator('#ecc-s').fill('20')
    check('入力上限でも図が領域内',float(page.locator('#ecc-dot').get_attribute('cx'))<560)
    page.locator('#ecc-s').fill('0')
    check('距離0を拒否','入力してください' in page.locator('#ecc-result').inner_text())
    page.locator('#ecc-form button[type=reset]').click();page.wait_for_timeout(50)
    check('偏心reset',page.locator('#ecc-e').input_value()=='1' and page.locator('#ecc-s').input_value()=='100')
    local=page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.getAttribute("href")).filter(x=>!x.startsWith("http")&&!x.startsWith("#"))')
    check('教材内のファイルリンクが存在',all((target.parent/l).resolve().exists() for l in local),local)
    check('外部通信なし',not any(r.startswith('http') for r in requests))
    check('JavaScriptエラーなし',not errors,errors)
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(250)
    page.screenshot(path=str(OUT/'desktop.png'))
    page.locator('#return').screenshot(path=str(OUT/'eccentric.png'))
    page.set_viewport_size({'width':320,'height':900});page.goto(target.as_uri())
    check('320pxでページ横あふれなし',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.screenshot(path=str(OUT/'mobile.png'))
    page.locator('summary').first.focus();page.keyboard.press('Enter')
    check('キーボードで解答を開く',page.locator('details').first.get_attribute('open') is not None)
    state=page.locator('details').evaluate_all('(ds)=>ds.map(d=>d.open)')
    page.evaluate('dispatchEvent(new Event("beforeprint"))')
    check('印刷で解答を表示',page.locator('details').evaluate_all('(ds)=>ds.every(d=>d.open)'))
    page.emulate_media(media='print')
    check('印刷でも確認問題の問いを表示',page.locator('summary').evaluate_all('(ss)=>ss.every(s=>getComputedStyle(s).display!=="none")'))
    page.emulate_media(media='screen')
    page.evaluate('dispatchEvent(new Event("afterprint"))')
    check('印刷後に開閉状態を戻す',page.locator('details').evaluate_all('(ds)=>ds.map(d=>d.open)')==state)
    for stem in ['exercise_回2','exercise_answers_回2']:
        f=ROOT/'materials/exercises/第04回_角測量'/f'{stem}.html'
        page.emulate_media(media='print')
        page.set_viewport_size({'width':1000,'height':900});page.goto(f.as_uri())
        page.pdf(path=str(f.with_suffix('.pdf')),print_background=True,prefer_css_page_size=True)
        import fitz
        with fitz.open(f.with_suffix('.pdf')) as pdf:
            check(stem+'：A4・2ページ',len(pdf)==2 and abs(pdf[0].rect.width-595.28)<2,len(pdf))
            for i,pdf_page in enumerate(pdf):
                pdf_page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/f'{stem}_page{i+1}.png')
    browser.close()
(OUT/'results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
failed=[c for c in checks if not c['pass_']]
print(json.dumps({'checks':len(checks),'failed':failed},ensure_ascii=False))
assert not failed
