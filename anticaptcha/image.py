import time
from anticaptchaofficial.imagecaptcha import imagecaptcha

ANTI_CAPTCHA_KEY = "YOUR-API-KEY"
IMAGE_FILE = "images/captcha3.jpg"
CORRECT_ANSWER = "hwjrc"

solver = imagecaptcha()
solver.set_verbose(0)
solver.set_key(ANTI_CAPTCHA_KEY)

correct_count = 0

with open("anticaptcha_image_results.txt", "a", encoding="utf-8") as file:
    for i in range(1, 51):
        start_time = time.perf_counter()

        try:
            answer = solver.solve_and_return_solution(IMAGE_FILE)
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            if answer == 0:
                file.write(f"{i}. Error: {solver.error_code} — {elapsed:.2f} sec\n")
                file.flush()
                continue

            if answer.strip().lower() == CORRECT_ANSWER.lower():
                correct_count += 1
                file.write(f"{i}. OK ({answer}) — {elapsed:.2f} sec\n")
            else:
                file.write(f"{i}. WRONG ({answer}) — {elapsed:.2f} sec\n")

            file.flush()

        except Exception as e:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            file.write(f"{i}. Error: {e} — {elapsed:.2f} sec\n")
            file.flush()
            continue

        time.sleep(2)

accuracy = (correct_count / 15) * 100
print(f"Accuracy: {accuracy:.2f}%")
