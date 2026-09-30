import time
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException

API_KEY = "YOUR-API-KEY"
IMAGE_FILE = "images/captcha3.jpg"
CORRECT_ANSWER = "hwjrc"

solver = TwoCaptcha(API_KEY)

correct_count = 0

with open("results/image_results.txt", "a", encoding="utf-8") as file:
    for i in range(1, 51):
        start_time = time.perf_counter()

        try:
            result = solver.normal(
                IMAGE_FILE,
                numeric=0
            )

            end_time = time.perf_counter()
            elapsed = end_time - start_time

            answer = result["code"].strip()

            if answer.lower() == CORRECT_ANSWER.lower():
                correct_count += 1
                file.write(f"{i}. OK ({answer}) — {elapsed:.2f} sec\n")
            else:
                file.write(f"{i}. WRONG ({answer}) — {elapsed:.2f} sec\n")

            file.flush()

        except ApiException as e:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            file.write(f"{i}. API Error: {e} — {elapsed:.2f} sec\n")
            file.flush()
            continue

        except Exception as e:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
            file.flush()
            continue

        time.sleep(2)

accuracy = (correct_count / 15) * 100
print(f"Accuracy: {accuracy:.2f}%")