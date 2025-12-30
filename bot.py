
import os
import time
import requests
import feedparser
import hashlib

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUBREDDITS = [s.strip() for s in os.getenv("SUBREDDITS", "").split(",") if s.strip()]
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))
USER_AGENT = "reddit-rss-telegram-bot"

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise SystemExit("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

seen = set()

def rss_url(sub):
    return f"https://www.reddit.com/r/{sub}/new/.rss"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    session.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })

def post_id(entry):
    return hashlib.sha256((entry.get("id","") + entry.get("link","")).encode()).hexdigest()

print("Bot started. Monitoring:", ", ".join(SUBREDDITS))

while True:
    for sub in SUBREDDITS:
        try:
            feed = feedparser.parse(rss_url(sub))
            for e in feed.entries[:20]:
                pid = post_id(e)
                if pid in seen:
                    continue

                text = (e.get("title","") + " " + e.get("summary","")).lower()

                for kw in KEYWORDS:
                    if kw in text:
                        send(f"🔔 {kw}\nr/{sub}\n{e.get('title','')}\n{e.get('link','')}")
                        seen.add(pid)
                        break
        except Exception as err:
            print("Error:", err)

        time.sleep(3)

    time.sleep(CHECK_INTERVAL)
