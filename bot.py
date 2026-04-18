import requests
from datetime import datetime

TOKEN = "8785731071:AAHBme8qZt5Ak4SeainvzZBNE7XYUsvzmu4"
CHANNEL = "-1003756748417"

report_date = datetime.now().strftime("%Y-%m-%d")

text = f"📅 {report_date}\n🚨 GitHub bot աշխատում է"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, json={
    "chat_id": CHANNEL,
    "text": text
})

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)
