import time
import requests
import os

API_KEY = "YOUR-API-KEY"
IMAGE_FILE = "images/captcha3.jpg"
CORRECT_ANSWER = "hwjrc"

SUBMIT_URL = "https://api.solvecaptcha.com/in.php"
RESULT_URL = "https://api.solvecaptcha.com/res.php"

if not os.path.exists(IMAGE_FILE):
    raise FileNotFoundError("File not found")

if os.path.getsize(IMAGE_FILE) < 100:
    raise ValueError("File is too small")

correct_count = 0

with open("solvecaptcha_image_results.txt", "a", encoding="utf-8") as file:
    for i in range(1, 51):
        start = time.perf_counter()

        try:
            with open(IMAGE_FILE, "rb") as img:
                response = requests.post(
                    SUBMIT_URL,
                    data={
                        "key": API_KEY,
                        "method": "post",
                        "json": 1
                    },
                    files={"file": img}
                ).json()

            if response.get("status") != 1:
                raise RuntimeError(response)

            captcha_id = response["request"]

            while True:
                time.sleep(5)

                result = requests.get(
                    RESULT_URL,
                    params={
                        "key": API_KEY,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1
                    }
                ).json()

                if result.get("status") == 1:
                    answer = result["request"].strip()
                    break

                if result.get("request") != "CAPCHA_NOT_READY":
                    raise RuntimeError(result)

            elapsed = time.perf_counter() - start

            if answer.lower() == CORRECT_ANSWER.lower():
                correct_count += 1
                file.write(f"{i}. OK ({answer}) — {elapsed:.2f} sec\n")
            else:
                file.write(f"{i}. WRONG ({answer}) — {elapsed:.2f} sec\n")

            file.flush()

        except Exception as e:
            elapsed = time.perf_counter() - start
            file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
            file.flush()
            continue

        time.sleep(2)

accuracy = (correct_count / 15) * 100
print(f"Accuracy: {accuracy:.2f}%")
