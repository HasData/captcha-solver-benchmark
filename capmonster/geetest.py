import time
import re
import json
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import GeetestRequest
from playwright.sync_api import sync_playwright

API_KEY = "YOUR-API-KEY"
URL = "https://www.geetest.com/en/adaptive-captcha-demo"

CAPTCHA_TYPES = [
    {"name": "Slide", "tab_class": "tab-item-1"},
    {"name": "Icon", "tab_class": "tab-item-2"},
    {"name": "Gobang", "tab_class": "tab-item-3"},
    {"name": "IconCrush", "tab_class": "tab-item-4"},
]

client_options = ClientOptions(api_key=API_KEY)
cap_monster_client = CapMonsterClient(options=client_options)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_default_timeout(60000)

    with open("geetest_results.txt", "w", encoding="utf-8") as file:

        for captcha in CAPTCHA_TYPES:
            file.write(f"\n=== {captcha['name']} ===\n")
            file.flush()

            for i in range(1, 51):
                try:
                    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(5000)
                    page.evaluate("window.scrollTo(0, 600)")
                    page.wait_for_timeout(2000)

                    tab_selector = f".{captcha['tab_class']} button"
                    page.evaluate(
                        f"""
                        (() => {{
                            const btn = document.querySelector("{tab_selector}");
                            if (btn && !btn.classList.contains("on")) {{
                                btn.click();
                            }}
                        }})()
                        """
                    )
                    page.wait_for_timeout(3000)

                    page.evaluate(
                        "document.querySelector('.geetest_btn_click')?.click();"
                    )
                    page.wait_for_timeout(5000)

                    captcha_data = page.evaluate(
                        """
                        () => {
                            const scripts = document.querySelectorAll('script[src*="geetest.com"]');
                            let captchaId = null;
                            let challenge = null;

                            for (let script of scripts) {
                                const src = script.src;

                                const captchaIdMatch = src.match(/captcha_id=([a-f0-9]{32})/);
                                if (captchaIdMatch) captchaId = captchaIdMatch[1];

                                const challengeMatch = src.match(/challenge=([a-f0-9-]{36})/);
                                if (challengeMatch) challenge = challengeMatch[1];
                            }

                            return { captchaId, challenge };
                        }
                        """
                    )

                    captcha_id = captcha_data.get("captchaId")
                    challenge = captcha_data.get("challenge")

                    if not captcha_id:
                        file.write(f"{i}. Captcha ID not found\n")
                        file.flush()
                        continue

                    start = time.perf_counter()

                    geetest_request = GeetestRequest(
                        websiteUrl=URL,
                        gt=captcha_id,
                        challenge=challenge if challenge else "",
                        version=4,
                    )

                    result = page.evaluate(
                        """
                        async (params) => {
                            const response = await fetch('https://api.capmonster.cloud/createTask', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    clientKey: params.apiKey,
                                    task: {
                                        type: 'GeeTestTaskProxyless',
                                        websiteURL: params.url,
                                        gt: params.gt,
                                        challenge: params.challenge,
                                        version: 4
                                    }
                                })
                            });
                            const data = await response.json();

                            if (data.errorId !== 0) {
                                return { error: data.errorDescription };
                            }

                            const taskId = data.taskId;

                            for (let i = 0; i < 60; i++) {
                                await new Promise(r => setTimeout(r, 3000));

                                const resultResponse = await fetch('https://api.capmonster.cloud/getTaskResult', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                        clientKey: params.apiKey,
                                        taskId: taskId
                                    })
                                });
                                const resultData = await resultResponse.json();

                                if (resultData.status === 'ready') {
                                    return resultData.solution;
                                } else if (resultData.errorId !== 0) {
                                    return { error: resultData.errorDescription };
                                }
                            }

                            return { error: 'Timeout' };
                        }
                        """,
                        {
                            "apiKey": API_KEY,
                            "url": URL,
                            "gt": captcha_id,
                            "challenge": challenge if challenge else "",
                        },
                    )

                    elapsed = time.perf_counter() - start

                    if not result or "error" in result:
                        error_msg = (
                            result.get("error", "Unknown error")
                            if result
                            else "No solution"
                        )
                        file.write(f"{i}. CapMonster error: {error_msg}\n")
                        file.flush()
                        continue

                    page.evaluate(
                        """
                        (data) => {
                            if (window.captchaObj) {
                                const original = window.captchaObj.getValidate;
                                window.captchaObj.getValidate = function(_) {
                                    const res = original.call(this, data);
                                    const captcha = document.querySelector('#captcha > div');
                                    if (captcha) captcha.classList.add('geetest_lock_success');
                                    const tip = document.querySelector('.geetest_tip');
                                    if (tip) tip.innerText = 'Verification Success';
                                    return res;
                                };
                                window.captchaObj.getValidate(data);
                            }
                        }
                        """,
                        result,
                    )

                    page.wait_for_function(
                        """
                        () => {
                            const el = document.querySelector('.geetest_tip');
                            return el && el.innerText.includes('Verification Success');
                        }
                        """,
                        timeout=10000,
                    )

                    file.write(f"{i}. Success — {elapsed:.2f} sec\n")
                    file.flush()

                except Exception as e:
                    file.write(f"{i}. Error: {e}\n")
                    file.flush()

    browser.close()
