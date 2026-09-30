import time
from playwright.sync_api import sync_playwright
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

ANTI_CAPTCHA_KEY = "YOUR-API-KEY"
SITE_KEY = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
URL = "https://www.google.com/recaptcha/api2/demo"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("anticaptcha_results.txt", "w", encoding="utf-8") as file:
        for i in range(1, 51):
            page.goto(URL)

            solver = recaptchaV2Proxyless()
            solver.set_verbose(0)
            solver.set_key(ANTI_CAPTCHA_KEY)
            solver.set_website_url(URL)
            solver.set_website_key(SITE_KEY)
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

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            time.sleep(2)

    browser.close()
