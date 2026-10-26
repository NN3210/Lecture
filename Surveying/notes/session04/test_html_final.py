"""第4回 explanation.html の最終独立検証。"""

from pathlib import Path
import json

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "materials" / "slides" / "第04回_角測量" / "explanation.html"
OUT = Path(__file__).resolve().parent / "html_preview_final"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"target": "materials/slides/第04回_角測量/explanation.html", "checks": [], "console_errors": [], "page_errors": []}

    def check(name, condition, observed=""):
        result["checks"].append({"name": name, "pass": bool(condition), "observed": str(observed)})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")

        # 狭幅表示
        narrow = browser.new_page(viewport={"width": 320, "height": 900})
        narrow.goto(HTML.as_uri(), wait_until="load")
        widths = narrow.evaluate("""() => ({client: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
          offenders: [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1)
            .slice(0, 10).map(e => e.tagName + (e.id ? '#'+e.id : ''))})""")
        check("320pxでページ全体の横あふれなし", widths["scroll"] <= widths["client"], widths)
        narrow.screenshot(path=str(OUT / "viewport_320.png"), full_page=True)
        narrow.close()

        page = browser.new_page(viewport={"width": 1000, "height": 900})
        page.on("console", lambda msg: result["console_errors"].append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: result["page_errors"].append(str(exc)))
        page.goto(HTML.as_uri(), wait_until="load")

        # 初期値と丸め境界
        initial = page.locator("#face-result").inner_text()
        check("正40.001667・反220の平均を小数6桁で40.000834", "平均40.000834°" in initial, initial)
        check("平均の度分秒は40°00′03″", "40°00′03″" in initial, initial)

        # 正反平均の不正入力
        for left, right, label in [("", "220", "空欄"), ("10", "10", "同値"), ("-1", "179", "負数"), ("360", "180", "360")]:
            page.locator("#face-l").fill(left)
            page.locator("#face-r").fill(right)
            page.locator("#face-go").click()
            text = page.locator("#face-result").inner_text()
            check(f"正反平均が{label}を拒否", "入力してください" in text or "確認してください" in text, text)

        # Enterキー（操作1と操作2）
        page.locator("#wrap-start").fill("350")
        page.locator("#wrap-end").fill("20")
        page.locator("#wrap-end").press("Enter")
        check("操作1をEnterで実行", "30°" in page.locator("#wrap-result").inner_text(), page.locator("#wrap-result").inner_text())
        page.locator("#face-l").fill("40.001667")
        page.locator("#face-r").fill("220")
        page.locator("#face-r").press("Enter")
        check("操作2をEnterで実行", "平均40.000834°" in page.locator("#face-result").inner_text(), page.locator("#face-result").inner_text())

        # 操作3の数値とSVG同期
        before = page.evaluate("""() => ({x: eccDot().getAttribute('cx'), value: document.querySelector('#ecc-value').value})""".replace("eccDot()", "document.querySelector('#ecc-dot')"))
        page.locator("#ecc").fill("7")
        after = page.evaluate("""() => ({x: document.querySelector('#ecc-dot').getAttribute('cx'),
          ray: document.querySelector('#ecc-ray-a').getAttribute('x1'), value: document.querySelector('#ecc-value').value,
          text: document.querySelector('#ecc-result').innerText})""")
        check("偏心スライダーの数値表示が7.0 mへ更新", after["value"] == "7.0 m", after)
        check("偏心スライダーでSVGが連動", before["x"] != after["x"] and after["x"] == after["ray"], {"before": before, "after": after})
        check("偏心7 mの補正値を更新", "−4.004173°" in after["text"], after["text"])

        # 専用reset
        page.locator("#wrap-start").fill("1"); page.locator("#wrap-end").fill("2"); page.locator("#wrap-reset").click()
        check("操作1 reset", page.locator("#wrap-start").input_value() == "350" and page.locator("#wrap-end").input_value() == "20", "")
        page.locator("#face-l").fill("1"); page.locator("#face-r").fill("181"); page.locator("#face-reset").click()
        check("操作2 reset", page.locator("#face-l").input_value() == "40.001667" and page.locator("#face-r").input_value() == "220" and "40.000834°" in page.locator("#face-result").inner_text(), page.locator("#face-result").inner_text())
        page.locator("#ecc").fill("9"); page.locator("#ecc-reset").click()
        ecc_output = page.locator("#ecc-value").evaluate("e => e.value")
        check("操作3 reset", page.locator("#ecc").input_value() == "1" and ecc_output == "1.0 m", ecc_output)

        # detailsと印刷
        details = page.locator("#practice details")
        check("解答detailsは3件・初期状態で閉", details.count() == 3 and details.evaluate_all("ds => ds.every(d => !d.open)"), details.count())
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        check("beforeprintで全解答を開く", details.evaluate_all("ds => ds.every(d => d.open)"), details.evaluate_all("ds => ds.map(d => d.open)"))
        page.emulate_media(media="print")
        displays = details.locator("summary").evaluate_all("ss => ss.map(s => getComputedStyle(s).display)")
        check("印刷時summaryを非表示", displays == ["none", "none", "none"], displays)
        page.screenshot(path=str(OUT / "print_details.png"), full_page=True)
        page.emulate_media(media="screen")
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        check("afterprintで解答の開閉状態を復元", details.evaluate_all("ds => ds.every(d => !d.open)"), details.evaluate_all("ds => ds.map(d => d.open)"))

        # キーボードフォーカス視認性
        page.locator("#wrap-end").focus()
        page.keyboard.press("Tab")
        check("Tabキーで計算ボタンへ移動", page.evaluate("document.activeElement.id") == "wrap-go", page.evaluate("document.activeElement.id"))
        outline = page.locator("#wrap-go").evaluate("e => getComputedStyle(e).outlineStyle")
        check("キーボードフォーカスが視認可能", outline != "none", outline)
        check("JavaScript例外なし", not result["page_errors"], result["page_errors"])
        check("console errorなし", not result["console_errors"], result["console_errors"])
        browser.close()

    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(c["pass"] for c in result["checks"])
    print(f"{passed}/{len(result['checks'])} checks passed")
    for item in result["checks"]:
        if not item["pass"]:
            print(f"FAIL: {item['name']} :: {item['observed']}")


if __name__ == "__main__":
    main()
