import time
from twocaptcha import TwoCaptcha, ApiException
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"

SITE_KEY = "0x4AAAAAAAGlwMzq_9z6S9Mh"
URL = "https://clifford.io/demo/cloudflare-turnstile"

solver = TwoCaptcha(API_KEY)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("turnstile_results.txt", "w", encoding="utf-8") as file:
        for i in range(1, 50):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                result = solver.turnstile(sitekey=SITE_KEY, url=URL)
                token = result["code"]

                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                file.flush()

                page.evaluate(
                    """
                    (token) => {
                        const input = document.querySelector('input[name="cf-turnstile-response"]');
                        if (input) input.value = token;
                    }
                    """,
                    token,
                )

                page.click("button[type='submit']")
                page.wait_for_timeout(2000)

            except ApiException as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. API error: {e} — {elapsed:.2f} sec\n")
                file.flush()

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {str(e)} — {elapsed:.2f} sec\n")
                file.flush()

    browser.close()
