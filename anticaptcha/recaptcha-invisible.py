import time
from playwright.sync_api import sync_playwright
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

ANTI_CAPTCHA_KEY = "YOUR-API-KEY"
SITE_KEY = "6LcmDCcUAAAAAL5QmnMvDFnfPTP4iCUYRk2MwC0-"
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("anticaptcha_invisible_results.txt", "a", encoding="utf-8") as file:
        for i in range(1, 50):
            page.goto(URL)

            solver = recaptchaV2Proxyless()
            solver.set_verbose(0)
            solver.set_key(ANTI_CAPTCHA_KEY)
            solver.set_website_url(URL)
            solver.set_website_key(SITE_KEY)
            solver.set_is_invisible(1)
            solver.set_soft_id(0)

            start_time = time.perf_counter()

            try:
                token = solver.solve_and_return_solution()
                end_time = time.perf_counter()
                elapsed = end_time - start_time

                if token == 0:
                    file.write(f"{i}. Error: {solver.error_code} — {elapsed:.2f} sec\n")
                    file.flush()
                    continue

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

                page.evaluate("document.forms[0].submit()")
                page.wait_for_timeout(3000)

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
