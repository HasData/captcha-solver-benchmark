import time
import json
import deathbycaptcha
from playwright.sync_api import sync_playwright

DBC_USERNAME = "YOUR-USERNAME"
DBC_PASSWORD = r"YOUR-PASSWORD"
SITE_KEY = "6LcmDCcUAAAAAL5QmnMvDFnfPTP4iCUYRk2MwC0-"
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"
PROXY = None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)

    with open("dbc_invisible_results.txt", "a", encoding="utf-8") as file:
        for i in range(1, 50):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                captcha_payload = {
                    "googlekey": SITE_KEY,
                    "pageurl": URL,
                    "invisible": 1
                }

                if PROXY:
                    captcha_payload.update({
                        "proxy": PROXY,
                        "proxytype": "HTTP"
                    })

                json_payload = json.dumps(captcha_payload)

                captcha = client.decode(type=4, token_params=json_payload)

                if not captcha or "text" not in captcha:
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Solution Error — {elapsed:.2f} sec\n")
                    file.flush()
                    continue

                token = captcha["text"]
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{elapsed:.2f}\n")
                file.flush()

                page.evaluate(
                    """
                    (token) => {
                        const el = document.getElementById('g-recaptcha-response');
                        el.value = token;
                        document.forms[0].submit();
                    }
                    """,
                    token
                )

                page.wait_for_timeout(3000)

            except deathbycaptcha.AccessDeniedException:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Access Denied — {elapsed:.2f} sec\n")
                file.flush()
                continue

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
