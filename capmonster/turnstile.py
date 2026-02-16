import time
import asyncio
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import TurnstileRequest
from playwright.async_api import async_playwright

API_KEY = "YOUR-API-KEY"
SITE_KEY = "0x4AAAAAAAGlwMzq_9z6S9Mh"
URL = "https://clifford.io/demo/cloudflare-turnstile"

client_options = ClientOptions(api_key=API_KEY)
cap_monster_client = CapMonsterClient(options=client_options)


async def solve_turnstile():
    req = TurnstileRequest(
        websiteURL=URL,
        websiteKey=SITE_KEY,
    )
    resp = await cap_monster_client.solve_captcha(req)
    return resp["token"]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        with open("turnstile_results.txt", "w", encoding="utf-8") as file:
            for i in range(1, 50):
                await page.goto(URL)
                start_time = time.perf_counter()

                try:
                    token = await solve_turnstile()

                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                    await page.evaluate(
                        """
                        (token) => {
                            const input = document.querySelector('input[name="cf-turnstile-response"]');
                            if (input) input.value = token;
                        }
                        """,
                        token,
                    )

                    await page.click("button[type='submit']")
                    await page.wait_for_timeout(2000)

                except Exception as e:
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    file.write(f"{i}. Error: {str(e)} — {elapsed:.2f} sec\n")
                    file.flush()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
