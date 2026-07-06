import requests
import time
import re
import threading
from flask import Flask

# ==================== Render এর জন্য ডামি ওয়েব সার্ভার ====================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_app():
    try:
        app.run(host='0.0.0.0', port=10000)
    except Exception:
        pass

# ==================== আপনার আসল কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = "8884098961:AAE1UxFAH60LQaUdnB6q3MKN2VHJ8mw84Q0"
TELEGRAM_CHAT_ID = "-1004358010030"

API_USERNAME = "RamAli25"
API_PASSWORD = "md7247600@gmail.com"
# =============================================================

API_URL = "https://iprns.stats.direct/rest/sms"
latest_stamp = None  

def get_country_style(phone):
    if phone.startswith("236"):
        return "🇨🇫 #CF"
    elif phone.startswith("961"):
        return "🇱🇧 #LB"
    return "🌐 #INT"

def get_source_emoji(source):
    src_upper = source.upper()
    if "FACEBOOK" in src_upper or "FB" in src_upper:
        return "🔷"
    elif "1XBET" in src_upper:
        return "🟥"
    return "✉️"

def mask_phone_premium(phone):
    if len(phone) >= 8:
        return f"{phone[:5]} 💠 {phone[-4:]}"
    return phone

def extract_otp(message):
    match = re.search(r'\b\d{4,8}\b', message)
    if match:
        return match.group(0)
    return ""

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def fetch_new_sms():
    global latest_stamp
    params = {"page": 1, "per-page": 10}
    
    try:
        response = requests.get(API_URL, params=params, auth=(API_USERNAME, API_PASSWORD), timeout=15)
        
        if response.status_code == 200:
            sms_list = response.json()
            if not sms_list:
                return

            if latest_stamp is None:
                latest_stamp = sms_list[0].get('start_stamp')
                print(f"বট চালু হয়েছে। সর্বশেষ SMS সময়: {latest_stamp}")
                return

            for sms in reversed(sms_list):
                current_stamp = sms.get('start_stamp')
                
                if current_stamp and current_stamp > latest_stamp:
                    message = sms.get('short_message') or ""
                    receiver = sms.get('destination_addr') or ""
                    source = sms.get('source_addr') or "FB"
                    
                    if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin", "password", "reset", "1xbet", "facebook", "est votre code"]):
                        country_tag = get_country_style(receiver)
                        brand_emoji = get_source_emoji(source)
                        masked_number = mask_phone_premium(receiver)
                        otp_code = extract_otp(message)
                        
                        if otp_code:
                            alert_text = f"{country_tag} {brand_emoji} `{masked_number}`\n\n🛡️ *{otp_code}*"
                        else:
                            alert_text = f"{country_tag} {brand_emoji} `{masked_number}`\n\n📝 `{message}`"
                        
                        send_telegram_message(alert_text)
                        print(f"টেলিগ্রামে পাঠানো হয়েছে! সময়: {current_stamp}")
                    
                    latest_stamp = current_stamp
    except Exception as e:
        print(f"Error: {e}")

def main_loop():
    print("টেলিগ্রাম ওটিপি ফরওয়ার্ডার বট সঠিকভাবে রান হচ্ছে...")
    while True:
        fetch_new_sms()
        time.sleep(5)

if __name__ == "__main__":
    t = threading.Thread(target=main_loop)
    t.start()
    run_app()
