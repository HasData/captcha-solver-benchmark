import time
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
SITE_KEY = "6LcmDCcUAAAAAL5QmnMvDFnfPTP4iCUYRk2MwC0-"
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"

solver = TwoCaptcha(API_KEY)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("results/recaptcha_invisible.txt", "w", encoding="utf-8") as file:
        for i in range(1, 51):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                result = solver.recaptcha(
                    sitekey=SITE_KEY,
                    url=URL,
                    invisible=1
                )

                token = result["code"]
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{elapsed:.2f}\n")
                file.flush()

                page.evaluate(
                    """
                    (token) => {
                        const el = document.getElementById('g-recaptcha-response');
                        el.value = token;
                    }
                    """,
                    token
                )

                page.click("button[type='submit']")
                page.wait_for_timeout(3000)

            except ApiException as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f}\n")
                file.flush()
                continue

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f}\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
