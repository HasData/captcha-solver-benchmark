import asyncio
import time
from playwright.async_api import async_playwright
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2Request

API_KEY = "YOUR-API-KEY"
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"
SITE_KEY = "6LcmDCcUAAAAAL5QmnMvDFnfPTP4iCUYRk2MwC0-"

async def solve_with_capmonster():
    client_options = ClientOptions(api_key=API_KEY)
    client = CapMonsterClient(options=client_options)

    request = RecaptchaV2Request(
        websiteUrl=URL,
        websiteKey=SITE_KEY,
        isInvisible=True
    )

    return await client.solve_captcha(request)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        with open("capmonster_invisible_results.txt", "a", encoding="utf-8") as file:
            for i in range(1, 50):
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
                    file.write(f"{elapsed:.2f}\n")
                    file.flush()

                    await page.evaluate(
                        """
                        (token) => {
                            const el = document.getElementById('g-recaptcha-response');
                            el.value = token;
                            document.forms[0].submit();
                        }
                        """,
                        token
                    )

                    await page.wait_for_timeout(3000)

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
