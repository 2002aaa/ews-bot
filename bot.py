import requests
from datetime import datetime

# 👇 ԴԱՏԱՐԿ ՄԻ ԹՈՂ — այստեղ պետք է դնես քո ՆՈՐ TOKEN-ը
TOKEN = "8517894443:AAHG1ZUEmB-mubI-pywiBzP7bT0vwxvVqVU"

# 👇 Քո channel id (սա ճիշտ է, չփոխես)
CHANNEL = "@ewsarmenia"

# Ամսաթիվ
report_date = datetime.now().strftime("%Y-%m-%d")

# Message
text = f"""📅 Ամսաթիվ: {report_date}

🚨 EWS Armenia — Daily Update

✅ GitHub ավտոմատ համակարգը աշխատում է
"""

# Telegram API URL
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Request
response = requests.post(
    url,
    json={
        "chat_id": CHANNEL,
        "text": text
    }
)

# Debug output
print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
