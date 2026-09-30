import time
import requests
from playwright.sync_api import sync_playwright


API_KEY = "YOUR-API-KEY"

SITE_KEY = "0x4AAAAAAAGlwMzq_9z6S9Mh"
URL = "https://clifford.io/demo/cloudflare-turnstile"

IN_URL = "https://api.solvecaptcha.com/in.php"
RES_URL = "https://api.solvecaptcha.com/res.php"


def submit_turnstile():
    payload = {
        "key": API_KEY,
        "method": "turnstile",
        "sitekey": SITE_KEY,
        "pageurl": URL,
        "json": 1,
    }

    r = requests.post(IN_URL, data=payload, timeout=30)
    data = r.json()

    if data["status"] != 1:
        raise Exception(f"Submit error: {data}")

    return data["request"]


def get_result(captcha_id):
    params = {
        "key": API_KEY,
        "action": "get",
        "id": captcha_id,
        "json": 1,
    }

    while True:
        time.sleep(5)

        r = requests.get(RES_URL, params=params, timeout=30)
        data = r.json()

        if data["status"] == 1:
            return data["request"]

        if data["request"] != "CAPCHA_NOT_READY":
            raise Exception(f"Result error: {data}")


def solve_turnstile():
    captcha_id = submit_turnstile()
    token = get_result(captcha_id)
    return token


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        with open("turnstile_results.txt", "w", encoding="utf-8") as file:
            for i in range(1, 51):
                page.goto(URL)
                start = time.perf_counter()

                try:
                    token = solve_turnstile()
                    elapsed = time.perf_counter() - start

                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                    page.evaluate(
                        """
                        (token) => {
                            const input = document.querySelector(
                                'input[name="cf-turnstile-response"]'
                            );
                            if (input) {
                                input.value = token;
                            }
                        }
                        """,
                        token,
                    )

                    page.click("button[type='submit']")
                    page.wait_for_timeout(2000)

                except Exception as e:
                    elapsed = time.perf_counter() - start
                    file.write(f"{i}. Error: {str(e)} — {elapsed:.2f} sec\n")
                    file.flush()

        browser.close()


if __name__ == "__main__":
    main()
