import time
import json
import deathbycaptcha
from playwright.sync_api import sync_playwright

DBC_USERNAME = "YOUR-USERNAME"
DBC_PASSWORD = "YOUR-PASSWORD"

URL = "https://www.geetest.com/en/adaptive-captcha-demo"

CAPTCHA_TYPES = [
    {"name": "Slide", "tab_class": "tab-item-1"},
    {"name": "Icon", "tab_class": "tab-item-2"},
    {"name": "Gobang", "tab_class": "tab-item-3"},
    {"name": "IconCrush", "tab_class": "tab-item-4"},
]

client = deathbycaptcha.SocketClient(DBC_USERNAME, DBC_PASSWORD)

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

                    captcha_dict = {
                        "captcha_id": captcha_id,
                        "pageurl": URL
                    }

                    json_captcha = json.dumps(captcha_dict)

                    start = time.perf_counter()

                    try:
                        captcha_result = client.decode(
                            type=9,
                            geetest_params=json_captcha
                        )

                        elapsed = time.perf_counter() - start

                        if not captcha_result:
                            file.write(
                                f"{i}. DeathByCaptcha: No captcha result returned\n"
                            )
                            file.flush()
                            continue

                        solution_text = captcha_result.get("text")

                        if not solution_text:
                            file.write(f"{i}. No solution text received\n")
                            file.flush()
                            continue

                        try:
                            solution_data = (
                                json.loads(solution_text)
                                if isinstance(solution_text, str)
                                else solution_text
                            )
                        except Exception:
                            solution_data = solution_text

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
                            solution_data,
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

                    except deathbycaptcha.AccessDeniedException:
                        file.write(
                            f"{i}. DeathByCaptcha error: Access denied (check credentials or balance)\n"
                        )
                        file.flush()

                    except Exception as e:
                        file.write(f"{i}. DeathByCaptcha error: {e}\n")
                        file.flush()

                except Exception as e:
                    file.write(f"{i}. Error: {e}\n")
                    file.flush()

    browser.close()
