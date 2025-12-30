
import time
import requests
import feedparser
import hashlib

# -------------------
# Telegram Settings (Hardcoded for testing ONLY)
# -------------------
TELEGRAM_TOKEN = "8488282143:AAEmofU0H6WvQCyxDusBs8uA6AL_boL8u4w"  # Replace with your bot token
TELEGRAM_CHAT_ID = "7296034489"  # Replace with your numeric chat ID

# -------------------
# Subreddits to monitor
# -------------------
SUBREDDITS = [
    "CryptoCurrency", "Bitcoin", "ethereum", "binance", "CryptoMarkets",
    "CoinBase", "Kraken", "CoinbaseSupport", "kucoin", "Gemini",
    "Metamask", "ledgerwallet", "Trezor", "trustwallet", "cardano",
    "solana", "dogecoin", "Ripple", "polkadot", "UniSwap"
]

# -------------------
# Keywords to trigger alerts
# -------------------
KEYWORDS = [
    "problem", "issue", "error", "bug", "glitch", "crash", "frozen", "not working",
    "broken", "malfunction", "stuck", "pending", "failed", "lost", "missing",
    "help", "support", "customer service", "scammed", "hacked", "stolen",
    "fraud", "phishing", "compromised", "locked", "suspended", "login",
    "password", "2fa", "verification", "kyc", "withdrawal", "deposit",
    "maintenance", "downtime", "outage", "server error", "trading halted"
]

# -------------------
# Other settings
# -------------------
CHECK_INTERVAL = 120
USER_AGENT = "reddit-rss-telegram-bot"
HEARTBEAT_INTERVAL = 3600
last_heartbeat = 0

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})
seen = set()

# -------------------
# Helper functions
# -------------------
def rss_url(sub):
    return f"https://www.reddit.com/r/{sub}/new/.rss"

def post_id(entry):
    return hashlib.sha256((entry.get("id","") + entry.get("link","")).encode()).hexdigest()

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = session.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "disable_web_page_preview": False,
            "parse_mode": "HTML"
        })
        if response.status_code != 200:
            print(f"❌ Failed to send message: {response.text}")
    except Exception as e:
        print(f"❌ Exception in send(): {e}")

# -------------------
# Startup
# -------------------
send(f"✅ <b>Reddit Telegram Bot is running!</b>\nMonitoring {len(SUBREDDITS)} subreddits.")
print("Bot started. Monitoring:", ", ".join(SUBREDDITS))

# -------------------
# Main loop
# -------------------
while True:
    # Heartbeat
    current_time = time.time()
    if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
        send(f"💓 <b>Heartbeat:</b> Bot is running! Monitoring {len(SUBREDDITS)} subreddits.")
        last_heartbeat = current_time

    for sub in SUBREDDITS:
        try:
            feed = feedparser.parse(rss_url(sub))
            for entry in feed.entries[:20]:
                pid = post_id(entry)
                if pid in seen:
                    continue
                title = entry.get("title","")
                summary = entry.get("summary","")
                text = (title + " " + summary).lower()
                for kw in KEYWORDS:
                    if kw in text:
                        snippet = summary[:300] + ("..." if len(summary) > 300 else "")
                        message = (
                            f"🔔 <b>Keyword:</b> {kw}\n"
                            f"<b>Subreddit:</b> r/{sub}\n"
                            f"<b>Title:</b> {title}\n"
                            f"<b>Snippet:</b> {snippet}\n"
                            f"<b>Link:</b> {entry.get('link','')}"
                        )
                        send(message)
                        seen.add(pid)
                        break
        except Exception as e:
            print(f"❌ Error fetching subreddit {sub}: {e}")

        time.sleep(3)

    time.sleep(CHECK_INTERVAL)
