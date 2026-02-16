import time
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
SITE_KEY = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
URL = "https://www.google.com/recaptcha/api2/demo"

solver = TwoCaptcha(API_KEY)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("results/recaptcha.txt", "w", encoding="utf-8") as file:
        for i in range(1, 50):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                result = solver.recaptcha(sitekey=SITE_KEY, url=URL)
                token = result["code"]
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                file.flush()

                page.evaluate(
                    """
                    (token) => {
                        document.getElementById('g-recaptcha-response').style.display = 'block';
                        document.getElementById('g-recaptcha-response').value = token;
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

            except ApiException as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
