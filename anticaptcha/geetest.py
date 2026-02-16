import time
import re
from anticaptchaofficial.geetestproxyless import *
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
URL = "https://www.geetest.com/en/adaptive-captcha-demo"

CAPTCHA_TYPES = [
    {"name": "Slide", "tab_class": "tab-item-1"},
    {"name": "Icon", "tab_class": "tab-item-2"},
    {"name": "Gobang", "tab_class": "tab-item-3"},
    {"name": "IconCrush", "tab_class": "tab-item-4"},
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_default_timeout(60000)

    with open("geetest_results.txt", "w", encoding="utf-8") as file:

        for captcha in CAPTCHA_TYPES:
            file.write(f"\n=== {captcha['name']} ===\n")
            file.flush()

            for i in range(1, 50):
                try:
                    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(5000)
                    page.evaluate("window.scrollTo(0, 600)")
                    page.wait_for_timeout(2000)

                    tab_selector = f".{captcha['tab_class']} button"
                    page.evaluate(
                        f"""
                        (() => {{
                            const btn = document.querySelector("{tab_selector}");
                            if (btn && !btn.classList.contains("on")) {{
                                btn.click();
                            }}
                        }})()
                    """
                    )
                    page.wait_for_timeout(3000)

                    page.evaluate(
                        "document.querySelector('.geetest_btn_click')?.click();"
                    )
                    page.wait_for_timeout(5000)

                    captcha_id = page.evaluate(
                        """
                        () => {
                            const scripts = document.querySelectorAll('script[src*="geetest.com"]');
                            
                            for (let script of scripts) {
                                const match = script.src.match(/captcha_id=([a-f0-9]{32})/);
                                if (match) return match[1];
                            }
                            
                            return null;
                        }
                    """
                    )

                    if not captcha_id:
                        file.write(f"{i}. Captcha ID not found\n")
                        file.flush()
                        continue

                    start = time.perf_counter()

                    solver = geetestProxyless()
                    solver.set_verbose(1)
                    solver.set_key(API_KEY)
                    solver.set_website_url(URL)
                    solver.set_gt_key(captcha_id)
                    solver.set_version(4)

                    token = solver.solve_and_return_solution()

                    end = time.perf_counter()
                    elapsed = end - start

                    if token != 0:
                        page.evaluate(
                            """
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
                        """,
                            token,
                        )

                        page.wait_for_function(
                            """
                            () => {
                                const el = document.querySelector('.geetest_tip');
                                return el && el.innerText.includes('Verification Success');
                            }
                        """,
                            timeout=10000,
                        )

                        file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                        file.flush()
                    else:
                        error_code = solver.error_code
                        file.write(f"{i}. Anti-captcha error: {error_code}\n")
                        file.flush()
                        continue

                except Exception as e:
                    file.write(f"{i}. Error: {e}\n")
                    file.flush()
                    continue

    browser.close()
