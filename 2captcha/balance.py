import requests

API_KEY = "YOUR-API-KEY"

url = "https://api.2captcha.com/getBalance"

payload = {
    "clientKey": API_KEY
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    if data.get("errorId") == 0:
        print(f"Your balance: {data.get('balance')}")
    else:
        print(f"API error: {data}")
else:
    print(f"HTTP error: {response.status_code}")
