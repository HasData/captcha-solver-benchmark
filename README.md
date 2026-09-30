# CAPTCHA Solving Services Benchmark

![Python 3.11 or newer badge](https://img.shields.io/badge/python-3.11+-blue) ![Playwright automation badge](https://img.shields.io/badge/Playwright-Automation-green)

[![HasData, the company that ran the benchmark](banner.png)](https://hasdata.com/)

Benchmarking scripts for testing **5 popular CAPTCHA solving services** across **6 CAPTCHA types**. Each script runs 50 attempts to measure solve time and success rate.

This repo is a companion to our full analysis: **[Top 5 CAPTCHA Solving Services in 2026](https://hasdata.com/blog/captcha-solving)** - see the article for detailed results, performance comparisons, and recommendations.

## Services Tested

Each service gets its own folder with identical scripts.

| Service | Python SDK |
|---------|-----------|
| **2Captcha** | `2captcha-python` |
| **Anti-Captcha** | `anticaptchaofficial` |
| **CapMonster** | `capmonstercloudclient` |
| **DeathByCaptcha** | `deathbycaptcha` |
| **SolveCaptcha** | - |

SolveCaptcha runs over plain HTTP, no SDK involved.

## CAPTCHA Types

-  **Image CAPTCHA**. Normal CAPTCHA
-  **Audio CAPTCHA**. Speech-to-text transcription
- **reCAPTCHA v2**. Google's checkbox challenge
-  **reCAPTCHA Invisible**. Background verification
- **Cloudflare Turnstile**. Cloudflare's CAPTCHA alternative
- **GeeTest v4**. Slide, Icon, Gobang, IconCrush

## Project Structure

Five folders, one per vendor.

```
captcha-solver-benchmark/
├── 2captcha/
│   ├── images/
│   ├── audio/
│   ├── image.py
│   ├── audio.py
│   ├── recaptcha2.py
│   ├── recaptcha-invisible.py
│   ├── turnstile.py
│   ├── geetest.py
│   └── balance.py
│
├── anticaptcha/
├── capmonster/
├── deathbycaptcha/
└── solvecaptcha/
```

Each folder contains identical scripts adapted for that service's API.

## Installation

Three steps and the key.

### 1. Clone the repository

Standard clone, nothing global.

```bash
git clone https://github.com/your-username/captcha-solver-benchmark.git
cd captcha-solver-benchmark
```

Everything runs from the repo root.

### 2. Install dependencies

Pick the service you want to test and add its SDK from the table above.

**2Captcha**
```bash
pip install 2captcha-python playwright
playwright install
```

**Anti-Captcha**
```bash
pip install anticaptchaofficial playwright
playwright install
```

**CapMonster**
```bash
pip install capmonstercloudclient playwright
playwright install
```

**DeathByCaptcha**
```bash
pip install deathbycaptcha playwright
playwright install
```

**SolveCaptcha**
```bash
pip install requests playwright
playwright install
```

Playwright drives the pages that host the live challenges.

### 3. Add your API key

Edit the script you want to run and replace:

```python
API_KEY = "YOUR-API-KEY"
```

Every vendor issues the key on sign-up.

## Usage

Navigate to the service folder and run any script:

```bash
cd 2captcha
python image.py          # Test image CAPTCHA recognition
python audio.py          # Test audio transcription
python recaptcha2.py     # Test reCAPTCHA v2
python recaptcha-invisible.py  # Test invisible reCAPTCHA
python turnstile.py      # Test Cloudflare Turnstile
python geetest.py        # Test GeeTest v4 (all types)
python balance.py        # Check account balance
```

Results are saved to `.txt` files in the same directory.

## Key Parameters

Each script accepts these parameters (edit directly in the file):

| Parameter | Description |
|-----------|-------------|
| `API_KEY` | Your service API key |
| `IMAGE_FILE` / `AUDIO_FILE` | Path to test file |
| `SITE_KEY` | CAPTCHA site key from target page |
| `URL` | Target page URL |
| `CORRECT_ANSWER` | Expected answer (for accuracy tracking) |

All scripts run **50 attempts** by default. Adjust the range in the loop:

```python
for i in range(1, 51):  # 50 attempts, the upper bound is N + 1
```

Every attempt sends one solve request, so a longer loop costs more on each service.

## Results

Scripts write timing and success data to text files, one line per attempt:

```
1. Success, 2.34 sec
2. Success, 1.89 sec
3. Error: timeout, 15.00 sec
```

The benchmark ran 50 attempts per service per type. CapMonster took Turnstile in 6.24 seconds where 2Captcha needed 16.96, the same CapMonster managed 14% accuracy on legacy image CAPTCHAs, and SolveCaptcha hit 94% on Invisible reCAPTCHA. The full tables live in **[Top 5 CAPTCHA Solving Services in 2026](https://hasdata.com/blog/captcha-solving)**.

## Disclaimer

These scripts are for **educational and benchmarking purposes only**. Learn more about [the legality of web scraping](https://hasdata.com/blog/is-web-scraping-legal). 

Services have costs and rate limits.



## 🔎 More Resources

* **Full Analysis**: [Top 5 CAPTCHA Solving Services in 2026](https://hasdata.com/blog/captcha-solving?utm_source=github&utm_medium=syndication&utm_campaign=captcha-solving)
* **Discord Community**: [Join HasData](https://hasdata.com/join-discord)
* **Star this repo if helpful** ⭐
