import asyncio
import time
from playwright.async_api import async_playwright
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2Request

API_KEY = "YOUR-API-KEY"
URL = "https://www.google.com/recaptcha/api2/demo"
SITE_KEY = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"

async def solve_with_capmonster():
    client_options = ClientOptions(api_key=API_KEY)
    client = CapMonsterClient(options=client_options)

    request = RecaptchaV2Request(
        websiteUrl=URL,
        websiteKey=SITE_KEY
    )

    return await client.solve_captcha(request)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        with open("capmonster_results.txt", "w", encoding="utf-8") as file:
            for i in range(1, 51):
                await page.goto(URL)
                start_time = time.perf_counter()

                try:
                    result = await solve_with_capmonster()
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time

                    if not result or not result.get("gRecaptchaResponse"):
                        file.write(f"{i}. Solve error — {elapsed:.2f} sec\n")
                        file.flush()
                        continue

                    token = result["gRecaptchaResponse"]
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
