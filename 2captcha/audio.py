import time
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException

API_KEY = "YOUR-API-KEY"
AUDIO_FILE = "scratched.mp3"
CORRECT_ANSWER = "r v six t e"

solver = TwoCaptcha(API_KEY)

with open("results/audio_results.txt", "a", encoding="utf-8") as file:
    for i in range(1, 51):
        start_time = time.perf_counter()

        try:
            result = solver.audio(AUDIO_FILE, "en")
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            answer = result["code"].strip()

            if answer == CORRECT_ANSWER:
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
