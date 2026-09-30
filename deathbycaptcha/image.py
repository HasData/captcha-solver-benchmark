import time
import os
import deathbycaptcha

DBC_USERNAME = "YOUR-USERNAME"
DBC_PASSWORD = r"YOUR-PASSWORD"
IMAGE_FILE = "images/captcha3.jpg"
CORRECT_ANSWER = "hwjrc"

if not os.path.exists(IMAGE_FILE):
    raise FileNotFoundError("File not found")

if os.path.getsize(IMAGE_FILE) < 100:
    raise ValueError("File is too small")

client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)

correct_count = 0

with open("dbc_image_results.txt", "w", encoding="utf-8") as file:
    for i in range(1, 51):
        start_time = time.perf_counter()

        try:
            captcha = client.decode(IMAGE_FILE, timeout=60)

            if not captcha or "text" not in captcha:
                elapsed = time.perf_counter() - start_time
                file.write(f"{i}. Solve error — {elapsed:.2f} sec\n")
                file.flush()
                continue

            answer = captcha["text"].strip()
            captcha_id = captcha["captcha"]

            elapsed = time.perf_counter() - start_time

            if answer.lower() == CORRECT_ANSWER.lower():
                correct_count += 1
                file.write(f"{i}. OK ({answer}) — {elapsed:.2f} sec\n")
            else:
                file.write(f"{i}. WRONG ({answer}) — {elapsed:.2f} sec\n")
                client.report(captcha_id)

            file.flush()

        except deathbycaptcha.AccessDeniedException:
            elapsed = time.perf_counter() - start_time
            file.write(f"{i}. Access Denied — {elapsed:.2f} sec\n")
            file.flush()
            continue

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
            file.flush()
            continue

        time.sleep(2)

accuracy = (correct_count / 15) * 100
print(f"Accuracy: {accuracy:.2f}%")
