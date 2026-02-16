import time
import json
import deathbycaptcha
from playwright.sync_api import sync_playwright

DBC_USERNAME = "YOUR-USERNAME"
DBC_PASSWORD = r"YOUR-PASSWORD"
SITE_KEY = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
URL = "https://www.google.com/recaptcha/api2/demo"
PROXY = None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)

    with open("dbc_recaptcha_results.txt", "w", encoding="utf-8") as file:
        for i in range(1, 50):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                captcha_payload = {
                    "googlekey": SITE_KEY,
                    "pageurl": URL
                }

                if PROXY:
                    captcha_payload.update({
                        "proxy": PROXY,
                        "proxytype": "HTTP"
                    })

                json_payload = json.dumps(captcha_payload)
                captcha = client.decode(type=4, token_params=json_payload)

                if not captcha or "text" not in captcha:
                    elapsed = time.perf_counter() - start_time
                    file.write(f"{i}. Solve failed — {elapsed:.2f} sec\n")
                    file.flush()
                    continue

                token = captcha["text"]
                elapsed = time.perf_counter() - start_time
                file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                file.flush()

                page.evaluate(
                    """
                    (token) => {
                        const el = document.getElementById('g-recaptcha-response');
                        el.style.display = 'block';
                        el.value = token;
                    }
                    """,
                    token
                )

                page.evaluate(
                    """
                    (token) => {
                        if (window.onSuccess) {
                            window.onSuccess(token);
                        }
                    }
                    """,
                    token
                )

                page.click("#recaptcha-demo-submit")
                page.wait_for_selector(".recaptcha-success", timeout=10000)

            except deathbycaptcha.AccessDeniedException:
                elapsed = time.perf_counter() - start_time
                file.write(f"{i}. Access denied — {elapsed:.2f} sec\n")
                file.flush()
                continue

            except Exception as e:
                elapsed = time.perf_counter() - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
