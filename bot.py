import requests
from datetime import datetime

TOKEN = "քո_նոր_token-ը"
CHANNEL = "-1003756748417"

report_date = datetime.now().strftime("%Y-%m-%d")

text = f"📅 {report_date} \n🚨 Test message from GitHub bot"

r = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHANNEL, "text": text}
)

print(r.status_code, r.text)
