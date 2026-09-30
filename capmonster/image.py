import asyncio
import time
import os
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import ImageToTextRequest

API_KEY = "YOUR-API-KEY"
IMAGE_FILE = "images/captcha3.jpg"
CORRECT_ANSWER = "hwjrc"

async def solve_image():

    if not os.path.exists(IMAGE_FILE):
        raise FileNotFoundError("File not found")

    if os.path.getsize(IMAGE_FILE) < 100:
        raise ValueError("File is smaller than 100 bytes")

    with open(IMAGE_FILE, "rb") as f:
        image_bytes = f.read()

    client = CapMonsterClient(
        options=ClientOptions(api_key=API_KEY)
    )

    request = ImageToTextRequest(
        image_bytes=image_bytes,
        module_name=None,
        threshold=50,
        case=True,
        numeric=0,
        math=False
    )

    return await client.solve_captcha(request)

async def main():
    correct_count = 0

    with open("capmonster_image_results.txt", "w", encoding="utf-8") as file:
        for i in range(1, 51):
            start = time.perf_counter()

            try:
                result = await solve_image()
                elapsed = time.perf_counter() - start

                if not result or not result.get("text"):
                    file.write(f"{i}. Solve error — {elapsed:.2f} sec\n")
                    file.flush()
                    continue

                answer = result["text"].strip()

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

            await asyncio.sleep(2)

    print(f"Accuracy: {(correct_count/15)*100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
