import requests

API_KEY = "YOUR-API-KEY"

url = "https://api.solvecaptcha.com/res.php"

params = {
    "key": API_KEY,
    "action": "getbalance"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    balance = response.text
    try:
        balance_value = float(balance)
        print(f"Balance: {balance_value}")
    except ValueError:
        print(f"Error API: {balance}")
else:
    print(f"HTTP error: {response.status_code}")
