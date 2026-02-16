import time
import re
import requests
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
URL = "https://www.geetest.com/en/adaptive-captcha-demo"

CAPTCHA_TYPES = [
    {"name": "Slide", "tab_class": "tab-item-1"},
    {"name": "Icon", "tab_class": "tab-item-2"},
    {"name": "Gobang", "tab_class": "tab-item-3"},
    {"name": "IconCrush", "tab_class": "tab-item-4"},
]


def solve_geetest_v4(captcha_id, url):
    in_url = "https://api.solvecaptcha.com/in.php"

    payload = {
        "key": API_KEY,
        "method": "geetest_v4",
        "captcha_id": captcha_id,
        "pageurl": url,
        "json": "1",
    }

    try:
        response = requests.post(in_url, data=payload, timeout=30)

        if response.status_code != 200:
            return None, f"HTTP Error {response.status_code}"

        result = response.json()

        if result.get("status") != 1:
            return None, f"Task creation error: {result.get('request', 'Unknown error')}"

        task_id = result.get("request")

        res_url = "https://api.solvecaptcha.com/res.php"

        for _ in range(60):
            time.sleep(5)

            res_params = {
                "key": API_KEY,
                "action": "get",
                "id": task_id,
                "json": "1",
            }

            response = requests.get(res_url, params=res_params, timeout=30)

            if response.status_code != 200:
                continue

            result = response.json()

            if result.get("status") == 1:
                return result.get("request"), None
            if result.get("request") == "CAPCHA_NOT_READY":
                continue

            return None, result.get("request", "Unknown error")

        return None, "Timeout"

    except Exception as e:
        return None, f"Exception: {str(e)}"


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
                            const scripts = document.querySelectorAll(
                                'script[src*="geetest.com"]'
                            );

                            for (const script of scripts) {
                                const match = script.src.match(
                                    /captcha_id=([a-f0-9]{32})/
                                );
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
                    solution, error = solve_geetest_v4(captcha_id, URL)
                    elapsed = time.perf_counter() - start

                    if error:
                        file.write(f"{i}. SolveCaptcha error: {error}\n")
                        file.flush()
                        continue

                    if not solution:
                        file.write(f"{i}. No solution received\n")
                        file.flush()
                        continue

                    page.evaluate(
                        """
                        (data) => {
                            if (window.captchaObj) {
                                const original = window.captchaObj.getValidate;
                                window.captchaObj.getValidate = function (_) {
                                    const result = original.call(this, data);
                                    const captcha = document.querySelector('#captcha > div');
                                    if (captcha) captcha.classList.add('geetest_lock_success');
                                    const tip = document.querySelector('.geetest_tip');
                                    if (tip) tip.innerText = 'Verification Success';
                                    return result;
                                };
                                window.captchaObj.getValidate(data);
                            }
                        }
                        """,
                        solution,
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

                except Exception as e:
                    file.write(f"{i}. Error: {e}\n")
                    file.flush()

    browser.close()
