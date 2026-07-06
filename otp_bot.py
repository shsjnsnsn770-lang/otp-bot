import requests
import time
import re
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 with Model 1!"

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
    # মডেল ১ এর জন্য দেশের পুরো নাম ও ফ্ল্যাগ
    if phone.startswith("241"):
        return "🇬🇦 **Gabon** (#GA)"
    elif phone.startswith("236"):
        return "🇨🇫 **Central African Republic** (#CF)"
    elif phone.startswith("961"):
        return "🇱🇧 **Lebanon** (#LB)"
    return "🌐 **International** (#INT)"

def get_source_name(source):
    src_upper = source.upper()
    if "WHATSAPP" in src_upper or "WA" in src_upper:
        return "WhatsApp"
    elif "FACEBOOK" in src_upper or "FB" in src_upper:
        return "Facebook"
    elif "1XBET" in src_upper:
        return "1XBet"
    return source

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
                    source = sms.get('source_addr') or "Unknown"
                    
                    if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin", "password", "whatsapp", "facebook", "1xbet"]):
                        country_info = get_country_style(receiver)
                        source_name = get_source_name(source)
                        otp_code = extract_otp(message)
                        
                        # মডেল ১ এর ক্লিন ফরম্যাট
                        if otp_code:
                            alert_text = (
                                f"{country_info}\n"
                                f"📱 **Phone:** `+{receiver}`\n"
                                f"🏢 **Source:** {source_name}\n"
                                f"🛡️ **OTP Code:** **{otp_code}**"
                            )
                        else:
                            alert_text = (
                                f"{country_info}\n"
                                f"📱 **Phone:** `+{receiver}`\n"
                                f"🏢 **Source:** {source_name}\n"
                                f"📝 **Message:** `{message}`"
                            )
                        
                        send_telegram_message(alert_text)
                        print(f"টেলিগ্রামে পাঠানো হয়েছে! সময়: {current_stamp}")
                    
                    latest_stamp = current_stamp
    except Exception as e:
        print(f"Error: {e}")

def main_loop():
    print("বট মডেল ১ অনুযায়ী সফলভাবে রান হচ্ছে...")
    while True:
        fetch_new_sms()
        time.sleep(5)

if __name__ == "__main__":
    t = threading.Thread(target=main_loop)
    t.start()
    run_app()
