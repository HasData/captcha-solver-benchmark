import time
import re
import json
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
URL = "https://www.geetest.com/en/adaptive-captcha-demo"

CAPTCHA_TYPES = [
    {"name": "Slide", "tab_class": "tab-item-1"},
    {"name": "Icon", "tab_class": "tab-item-2"},
    {"name": "Gobang", "tab_class": "tab-item-3"},
    {"name": "IconCrush", "tab_class": "tab-item-4"},
]

solver = TwoCaptcha(API_KEY)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("geetest_results.txt", "w", encoding="utf-8") as file:

        for captcha in CAPTCHA_TYPES:
            file.write(f"\n=== {captcha['name']} ===\n")
            file.flush()

            for i in range(1, 50):
                try:
                    page.goto(URL, wait_until="networkidle")
                    page.wait_for_timeout(4000)
                    page.evaluate("window.scrollTo(0, 600)")
                    page.wait_for_timeout(1000)

                    tab_selector = f".{captcha['tab_class']} button"
                    page.evaluate(f"""
                        (() => {{
                            const btn = document.querySelector("{tab_selector}");
                            if (btn && !btn.classList.contains("on")) {{
                                btn.click();
                            }}
                        }})()
                    """)
                    page.wait_for_timeout(2000)

                    page.evaluate("document.querySelector('.geetest_btn_click')?.click();")
                    page.wait_for_timeout(2000)

                    html = page.content()
                    match = re.search(r'captcha_id=([a-f0-9]+)', html)
                    if not match:
                        file.write(f"{i}. captcha_id not found\n")
                        file.flush()
                        continue

                    captcha_id = match.group(1)

                    start = time.perf_counter()
                    result = solver.geetest_v4(captcha_id=captcha_id, url=URL)
                    end = time.perf_counter()
                    elapsed = end - start

                    if "code" in result:
                        result = json.loads(result["code"])

                    page.evaluate("""
                        (data) => {
                            if (window.captchaObj) {
                                const old = window.captchaObj.getValidate;
                                window.captchaObj.getValidate = function(_) {
                                    const res = old.call(this, data);
                                    const cap = document.querySelector('#captcha > div');
                                    if (cap) cap.classList.add('geetest_lock_success');
                                    const tip = document.querySelector('.geetest_tip');
                                    if (tip) tip.innerText = 'Verification Success';
                                    return res;
                                };
                                window.captchaObj.getValidate(data);
                            }
                        }
                    """, result)

                    page.wait_for_function("""
                        () => {
                            const el = document.querySelector('.geetest_tip');
                            return el && el.innerText.includes('Verification Success');
                        }
                    """, timeout=10000)

                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                except ApiException as e:
                    file.write(f"{i}. ApiException: {e}\n")
                    file.flush()
                    continue

                except Exception as e:
                    file.write(f"{i}. Error: {e}\n")
                    file.flush()
                    continue

    browser.close()
