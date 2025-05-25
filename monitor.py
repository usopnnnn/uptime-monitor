import time
import requests
from datetime import datetime

URL = "https://google.com"

while True:
    try:
        response = requests.get(URL)
        status = response.status_code
    except Exception as e:
        status = f"Error: {e}"

    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()}: {URL} → {status}\n")

    time.sleep(10)
