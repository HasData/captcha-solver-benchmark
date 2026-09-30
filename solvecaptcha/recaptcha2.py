import time
import requests
import asyncio
from playwright.async_api import async_playwright

API_KEY = "YOUR-API-KEY"
SITE_KEY = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
URL = "https://www.google.com/recaptcha/api2/demo"


def solve_with_solvecaptcha():
    submit_url = "https://api.solvecaptcha.com/in.php"
    payload = {
        "key": API_KEY,
        "method": "userrecaptcha",
        "googlekey": SITE_KEY,
        "pageurl": URL,
        "json": 1
    }

    start = time.perf_counter()

    r = requests.post(submit_url, data=payload).json()
    if r.get("status") != 1:
        raise RuntimeError(f"Submit error: {r}")

    captcha_id = r["request"]
    result_url = "https://api.solvecaptcha.com/res.php"

    while True:
        time.sleep(5)
        res = requests.get(result_url, params={
            "key": API_KEY,
            "action": "get",
            "id": captcha_id,
            "json": 1
        }).json()

        if res.get("status") == 1:
            end = time.perf_counter()
            return res["request"], end - start

        if res.get("request") != "CAPCHA_NOT_READY":
            raise RuntimeError(f"Solve error: {res}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        with open("solvecaptcha_results.txt", "w", encoding="utf-8") as file:
            for i in range(1, 51):
                await page.goto(URL)
                start_time = time.perf_counter()

                try:
                    token, elapsed = solve_with_solvecaptcha()
                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                    await page.evaluate(
                        """
                        (token) => {
                            const el = document.getElementById('g-recaptcha-response');
                            el.style.display = 'block';
                            el.value = token;
                        }
                        """,
                        token
                    )

                    await page.evaluate(
                        """
                        (token) => {
                            if (window.onSuccess) {
                                window.onSuccess(token);
                            }
                        }
                        """,
                        token
                    )

                    await page.click("#recaptcha-demo-submit")
                    await page.wait_for_selector(".recaptcha-success", timeout=10000)

                except Exception as e:
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
                    file.flush()
                    continue

                await asyncio.sleep(2)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
