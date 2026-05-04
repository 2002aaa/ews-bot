import os
import json
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import requests

TOKEN = os.environ["8785731071:AAHBpR2043ifC79U-T_nm-byb96p3j7X20Q"]
CHAT_ID = "@ewsarmenia"

END_DATE = datetime.today()
START_DATE = END_DATE - pd.DateOffset(years=3)

print("Downloading data...")
tickers = {
    "SP500": "^GSPC",
    "GOLD":  "GC=F",
    "BRENT": "BZ=F",
    "VIX":   "^VIX",
    "DXY":   "DX-Y.NYB",
}

raw = yf.download(
    list(tickers.values()),
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,
    progress=False
)["Close"]
raw.columns = list(tickers.keys())

df = raw.sort_index().ffill().bfill().dropna()

if len(df) < 30:
    raise ValueError(f"Not enough data: {len(df)} rows")

df["SP500_ret"] = df["SP500"].pct_change()
df["VIX_z"] = (df["VIX"] - df["VIX"].rolling(120).mean()) / df["VIX"].rolling(120).std()
df["DXY_z"] = (df["DXY"] - df["DXY"].rolling(120).mean()) / df["DXY"].rolling(120).std()
df["GOLD_z"] = (df["GOLD"] - df["GOLD"].rolling(60).mean()) / df["GOLD"].rolling(60).std()

def expanding_norm(x):
    mn = x.expanding().min()
    mx = x.expanding().max()
    return (x - mn) / (mx - mn).replace(0, np.nan)

df["RiskScore"] = (
    0.40 * expanding_norm(df["VIX_z"].clip(lower=0)) +
    0.25 * expanding_norm(df["DXY_z"].clip(lower=0)) +
    0.20 * expanding_norm(-df["SP500_ret"]) +
    0.15 * expanding_norm(df["GOLD_z"].clip(lower=0))
)

df = df.dropna(subset=["RiskScore"])

latest = df.iloc[-1]
date   = df.index[-1].strftime("%Y-%m-%d")
risk   = float(latest["RiskScore"]) * 100

if risk >= 65:
    status = "🔴 ԲԱՐՁՐ ՌԻSK"
    color  = "#e74c3c"
elif risk >= 40:
    status = "🟡 ՄԻJIN ՌԻSK"
    color  = "#f39c12"
else:
    status = "🟢 NORMAL"
    color  = "#2ecc71"

print(f"Date: {date} | Risk: {risk:.1f}% | {status}")

# PLOT
fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#0d1117")

plot_df = df["RiskScore"].tail(365)
ax.fill_between(plot_df.index, plot_df.values, alpha=0.3, color=color)
ax.plot(plot_df.index, plot_df.values, color=color, linewidth=1.5)
ax.axhline(0.65, color="#e74c3c", linestyle="--", alpha=0.6, linewidth=1)
ax.axhline(0.40, color="#f39c12", linestyle="--", alpha=0.6, linewidth=1)
ax.set_ylim(0, 1)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, color="white", fontsize=9)
plt.yticks(color="white", fontsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor("#333")
ax.set_title("EWS Armenia — Composite Risk Index", color="white", fontsize=13, pad=12)
ax.set_ylabel("Risk Score", color="white", fontsize=10)
plt.tight_layout()
plt.savefig("risk.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print("Plot saved.")

# SAVE JSON for dashboard
history = df["RiskScore"].tail(365)
dashboard_data = {
    "date": date,
    "latest_risk": float(latest["RiskScore"]),
    "history_dates": [d.strftime("%Y-%m-%d") for d in history.index],
    "history_values": [round(float(v), 4) for v in history.values],
    "indicators": {
        "S&P500": f"{float(df['SP500'].iloc[-1]):,.0f}",
        "VIX": f"{float(df['VIX'].iloc[-1]):.1f}",
        "Gold": f"{float(df['GOLD'].iloc[-1]):,.0f}",
        "Brent": f"{float(df['BRENT'].iloc[-1]):.1f}",
        "DXY": f"{float(df['DXY'].iloc[-1]):.1f}",
    }
}
with open("data.json", "w") as f:
    json.dump(dashboard_data, f)
print("data.json saved.")

# SEND
caption = (
    f"📊 *EWS Armenia — Daily Update*\n\n"
    f"📅 Ամuathիv` `{date}`\n"
    f"📈 Ռիukի մakardak` `{risk:.1f}%`\n"
    f"⚡ Kargazhichak` {status}\n\n"
    f"_Aghbyurner` S\\&P500, VIX, Brent, Gold, DXY_"
)

url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
with open("risk.png", "rb") as photo:
    resp = requests.post(
        url,
        files={"photo": photo},
        data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "MarkdownV2"},
        timeout=30
    )

if resp.status_code == 200:
    msg_id = resp.json()["result"]["message_id"]
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/pinChatMessage",
        data={"chat_id": CHAT_ID, "message_id": msg_id, "disable_notification": True},
        timeout=30
    )
    print("DONE — message sent and pinned.")
else:
    print(f"ERROR: {resp.status_code} — {resp.text}")
    exit(1)
