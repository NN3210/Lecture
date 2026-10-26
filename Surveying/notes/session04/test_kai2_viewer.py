from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
file=ROOT/'materials/slides/第04回_角測量/slides_回2.html'
checks=[]
def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page=browser.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(file.as_uri())
    check('初期は本編50枚',page.locator('#jump option').count()==50)
    check('1枚目画像が読み込める',page.locator('#slide').evaluate('(e)=>e.complete&&e.naturalWidth===1280'))
    page.keyboard.press('ArrowRight')
    check('右キーで2枚目',page.locator('#jump').input_value()=='1')
    page.locator('#jump').select_option('49')
    check('本編末尾で次へを停止',page.locator('#next').is_disabled())
    page.locator('#appendix').check()
    check('明示操作でのみ付録を加える',page.locator('#jump option').count()==63)
    page.locator('#next').click();page.wait_for_load_state('load')
    check('51枚目は問1解答','問1解答' in page.locator('#slide').get_attribute('alt'))
    page.locator('#jump').select_option('62')
    check('付録末尾で次へを停止',page.locator('#next').is_disabled())
    page.locator('#appendix').uncheck()
    check('付録を外すと本編末尾に戻る',page.locator('#jump').input_value()=='49')
    page.locator('#jump').select_option('0')
    page.locator('summary').click()
    check('発表者ノートを読める',len(page.locator('#notes').inner_text())>55)
    check('全63画像が存在',all((file.parent/'preview_回2'/f'slide-{i:02d}.png').exists() for i in range(1,64)))
    check('JavaScriptエラーなし',not errors)
    page.set_viewport_size({'width':320,'height':700})
    check('320pxでページ横あふれなし',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    browser.close()
(ROOT/'notes/session04/kai2/viewer_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':len(checks),'failed':[c for c in checks if not c['pass']]},ensure_ascii=False))
assert all(c['pass'] for c in checks)
