"""第4回説明HTMLのPlaywright実動確認。"""

from pathlib import Path
import json

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "materials" / "slides" / "第04回_角測量" / "explanation.html"
OUT = Path(__file__).resolve().parent / "html_preview"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = {"url": HTML.relative_to(ROOT).as_posix(), "viewports": {}, "checks": [], "console_errors": [], "page_errors": []}

    def check(name, condition, observed=""):
        results["checks"].append({"name": name, "pass": bool(condition), "observed": str(observed)})

    with sync_playwright() as p:
        # Playwright同梱ブラウザが未配置の環境でも、導入済みChromeで再現可能にする。
        browser = p.chromium.launch(headless=True, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        for width in (320, 768, 1440):
            page = browser.new_page(viewport={"width": width, "height": 900})
            page.on("console", lambda msg: results["console_errors"].append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: results["page_errors"].append(str(exc)))
            page.goto(HTML.as_uri(), wait_until="load")
            metrics = page.evaluate("""() => ({
              viewport: document.documentElement.clientWidth,
              documentWidth: document.documentElement.scrollWidth,
              bodyWidth: document.body.scrollWidth,
              overflowElements: [...document.querySelectorAll('body *')]
                .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
                .slice(0, 12).map(e => `${e.tagName.toLowerCase()}${e.id ? '#'+e.id : ''}${e.className && typeof e.className === 'string' ? '.'+e.className.trim().replace(/\\s+/g,'.') : ''}`)
            })""")
            results["viewports"][str(width)] = metrics
            check(f"幅{width}pxでページ全体の横あふれなし", metrics["documentWidth"] <= metrics["viewport"], metrics)
            page.screenshot(path=str(OUT / f"viewport_{width}.png"), full_page=True)
            page.close()

        page = browser.new_page(viewport={"width": 768, "height": 900})
        page.on("console", lambda msg: results["console_errors"].append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: results["page_errors"].append(str(exc)))
        page.goto(HTML.as_uri(), wait_until="load")

        # ラベル関連付け・操作可能性
        for control_id in ("wrap-start", "wrap-end", "face-l", "face-r", "ecc"):
            label = page.locator(f'label[for="{control_id}"]')
            check(f"{control_id} に明示ラベルあり", label.count() == 1 and bool(label.inner_text().strip()), label.inner_text() if label.count() else "なし")
        check("3操作の結果領域がstatus/live region", page.locator('.activity .result[role="status"][aria-live="polite"]').count() == 3,
              page.locator('.activity .result[role="status"][aria-live="polite"]').count())

        # 操作1：通常、360度境界、同値、入力範囲外。
        wrap_cases = [(350, 20, "30°"), (0, 359.999, "359.999°"), (359.999, 0, "0.001°"), (20, 20, "0°")]
        for a, b, expected in wrap_cases:
            page.locator("#wrap-start").fill(str(a)); page.locator("#wrap-end").fill(str(b)); page.locator("#wrap-go").click()
            text = page.locator("#wrap-result").inner_text()
            check(f"操作1 {a}→{b}", expected in text, text)
        page.locator("#wrap-start").fill("360"); page.locator("#wrap-go").click()
        text = page.locator("#wrap-result").inner_text()
        check("操作1 上限外360を拒否", "0以上360未満" in text, text)
        page.locator("#wrap-start").fill(""); page.locator("#wrap-go").click()
        text = page.locator("#wrap-result").inner_text()
        check("操作1 空欄を拒否", "0以上360未満" in text, text)

        # 操作2：例示値、0/180、360度境界付近、空欄。
        face_cases = [(40.001667, 220, "40.000834°"), (0, 180, "0.000000°"), (359.999, 179.999, "359.999000°")]
        for left, right, expected in face_cases:
            page.locator("#face-l").fill(str(left)); page.locator("#face-r").fill(str(right)); page.locator("#face-go").click()
            text = page.locator("#face-result").inner_text()
            check(f"操作2 正{left}/反{right}", expected in text, text)
        for left, right, label in [("", "220", "空欄"), ("10", "10", "正反同値"), ("-1", "179", "負数"), ("360", "180", "360度")]:
            page.locator("#face-l").fill(left); page.locator("#face-r").fill(right); page.locator("#face-go").click()
            text = page.locator("#face-result").inner_text()
            check(f"操作2 {label}を拒否", "二つの読定" in text, text)

        # 操作3：端点と中間値。
        for value, expected_value, expected_result in [(0, "0.0 m", "0.000000°"), (1, "1.0 m", "−0.572939°"), (10, "10.0 m", "−5.710593°")]:
            page.evaluate("v => { const e=document.querySelector('#ecc'); e.value=v; e.dispatchEvent(new Event('input', {bubbles:true})); }", str(value))
            shown = page.locator("#ecc-value").evaluate("e => e.value")
            text = page.locator("#ecc-result").inner_text()
            check(f"操作3 偏心{value}mの表示", shown == expected_value and expected_result in text, f"{shown} / {text}")
        figure_before = page.locator("#eccentric figure").inner_html()
        page.evaluate("() => { const e=document.querySelector('#ecc'); e.value='7'; e.dispatchEvent(new Event('input', {bubbles:true})); }")
        figure_after = page.locator("#eccentric figure").inner_html()
        check("操作3で偏心図も追従する", figure_before != figure_after, "図のDOMは操作前後で同一")

        # reset相当：専用リセットはなく、再読込でHTMLの初期値へ戻る。
        check("専用resetボタンの有無", page.locator('button[type="reset"], input[type="reset"]').count() > 0,
              page.locator('button[type="reset"], input[type="reset"]').count())
        page.reload(wait_until="load")
        defaults = page.evaluate("""() => ({start: document.querySelector('#wrap-start').value, end: document.querySelector('#wrap-end').value, left: document.querySelector('#face-l').value,
          right: document.querySelector('#face-r').value, ecc: document.querySelector('#ecc').value})""")
        check("再読込で3操作が初期値へ戻る", defaults == {"start": "350", "end": "20", "left": "40.001667", "right": "220", "ecc": "1"}, defaults)

        # 解答details：手動開閉と印刷イベントによる全展開。
        details = page.locator("#practice details")
        check("解答detailsが3件ある", details.count() == 3, details.count())
        initially_open = details.evaluate_all("els => els.map(e => e.open)")
        check("解答は初期状態で閉じている", initially_open == [False, False, False], initially_open)
        details.nth(0).locator("summary").click()
        check("解答summaryで開ける", details.nth(0).evaluate("e => e.open"), details.nth(0).evaluate("e => e.open"))
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        printed_open = details.evaluate_all("els => els.map(e => e.open)")
        check("beforeprintで解答を全展開", printed_open == [True, True, True], printed_open)
        page.emulate_media(media="print")
        summary_displays = details.locator("summary").evaluate_all("els => els.map(e => getComputedStyle(e).display)")
        check("印刷CSSでsummaryを非表示", summary_displays == ["none", "none", "none"], summary_displays)
        page.screenshot(path=str(OUT / "print_details.png"), full_page=True)

        check("JavaScript実行時エラーなし", len(results["page_errors"]) == 0, results["page_errors"])
        check("console errorなし", len(results["console_errors"]) == 0, results["console_errors"])
        browser.close()

    (OUT / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(c["pass"] for c in results["checks"])
    print(f"{passed}/{len(results['checks'])} checks passed")
    for c in results["checks"]:
        if not c["pass"]:
            print(f"FAIL: {c['name']} :: {c['observed']}")


if __name__ == "__main__":
    main()
