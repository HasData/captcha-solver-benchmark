import time
import json
import deathbycaptcha
from deathbycaptcha import AccessDeniedException
from playwright.sync_api import sync_playwright

username = "YOUR-USERNAME"
password = r"YOUR-PASSWORD"

client = deathbycaptcha.HttpClient(username, password)

SITE_KEY = "0x4AAAAAAAGlwMzq_9z6S9Mh"
URL = "https://clifford.io/demo/cloudflare-turnstile"

captcha_data = {
    "sitekey": SITE_KEY,
    "pageurl": URL
}
captcha_json = json.dumps(captcha_data)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open("turnstile_results.txt", "w", encoding="utf-8") as file:
        for i in range(1, 51):
            page.goto(URL)
            start_time = time.perf_counter()

            try:
                captcha = client.decode(type=12, turnstile_params=captcha_json)
                if captcha and "text" in captcha:
                    token = captcha["text"]
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                    page.evaluate(
                        """
                        (token) => {
                            document.querySelector('input[name="cf-turnstile-response"]').value = token;
                        }
                        """,
                        token
                    )

                    page.click("button[type='submit']")
                    page.wait_for_timeout(2000)

                else:
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Error: captcha not solved — {elapsed:.2f} sec\n")
                    file.flush()

            except AccessDeniedException:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: access denied — {elapsed:.2f} sec\n")
                file.flush()
                continue

            except Exception as e:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                file.flush()
                continue

    browser.close()
