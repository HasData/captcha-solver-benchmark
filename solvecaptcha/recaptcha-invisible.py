import time
import requests
import asyncio
from playwright.async_api import async_playwright

API_KEY = "YOUR-API-KEY"
SITE_KEY = "6LcmDCcUAAAAAL5QmnMvDFnfPTP4iCUYRk2MwC0-"
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"


def solve_with_solvecaptcha():
    submit_url = "https://api.solvecaptcha.com/in.php"
    payload = {
        "key": API_KEY,
        "method": "userrecaptcha",
        "googlekey": SITE_KEY,
        "pageurl": URL,
        "invisible": 1,
        "json": 1
    }

    start = time.perf_counter()

    response = requests.post(submit_url, data=payload).json()
    if response.get("status") != 1:
        raise RuntimeError(f"Submit error: {response}")

    captcha_id = response["request"]
    result_url = "https://api.solvecaptcha.com/res.php"

    while True:
        time.sleep(5)
        result = requests.get(
            result_url,
            params={
                "key": API_KEY,
                "action": "get",
                "id": captcha_id,
                "json": 1
            }
        ).json()

        if result.get("status") == 1:
            end = time.perf_counter()
            return result["request"], end - start

        if result.get("request") != "CAPCHA_NOT_READY":
            raise RuntimeError(f"Solve error: {result}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        with open("solvecaptcha_invisible_results.txt", "a", encoding="utf-8") as file:
            for attempt in range(1, 51):
                await page.goto(URL)
                start_time = time.perf_counter()

                try:
                    token, elapsed = solve_with_solvecaptcha()
                    file.write(f"{elapsed:.2f}\n")
                    file.flush()

                    await page.evaluate(
                        """
                        (token) => {
                            const el = document.getElementById('g-recaptcha-response');
                            el.value = token;
                        }
                        """,
                        token
                    )

                    await page.evaluate("document.forms[0].submit()")
                    await page.wait_for_timeout(3000)

                except Exception as error:
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(
                        f"{attempt}. Error: {error} — {elapsed:.2f} seconds\n"
                    )
                    file.flush()
                    continue

                await asyncio.sleep(2)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
