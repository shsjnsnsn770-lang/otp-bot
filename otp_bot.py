import requests
import time
import threading
from flask import Flask

# ==================== ডামি ফ্ল্যাস্ক সার্ভার (Render এর জন্য) ====================
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

            # প্রথমবার রান হলে লেটেস্ট টাইমস্ট্যাম্প সেট করা
            if latest_stamp is None:
                latest_stamp = sms_list[0].get('start_stamp')
                print(f"বট চালু হয়েছে। বর্তমান সর্বশেষ SMS সময়: {latest_stamp}")
                return

            # নতুন মেসেজ চেক করার লুপ
            for sms in reversed(sms_list):
                current_stamp = sms.get('start_stamp')
                
                if current_stamp and current_stamp > latest_stamp:
                    message = sms.get('short_message') or ""
                    receiver = sms.get('destination_addr') or "Unknown"
                    source = sms.get('source_addr') or "Unknown"
                    
                    # ওটিপি বা যেকোনো কোড থাকলে টেলিগ্রামে অ্যালার্ট পাঠানো
                    if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin", "password", "reset", "1xbet", "facebook"]):
                        alert_text = (
                            f"🔔 *নতুন OTP রিসিভ হয়েছে!*\n\n"
                            f"📱 *নাম্বার:* `{receiver}`\n"
                            f"🏢 *উৎস:* `{source}`\n"
                            f"📩 *মেসেজ:* {message}\n"
                            f"⏰ *সময়:* `{current_stamp}`"
                        )
                        send_telegram_message(alert_text)
                        print(f"টেলিগ্রামে পাঠানো হয়েছে, সময়: {current_stamp}")
                    
                    latest_stamp = current_stamp
        else:
            print(f"API সমস্যা! স্ট্যাটাস কোড: {response.status_code}")
    except Exception as e:
        print(f"রিকোয়েস্ট ফেইল্ড: {e}")

def main_loop():
    print("টেলিগ্রাম ওটিপি ফরওয়ার্ডার বট সঠিকভাবে রান হচ্ছে...")
    while True:
        fetch_new_sms()
        time.sleep(5)

if __name__ == "__main__":
    # ল্যাপটপে লোকাল রান এবং ক্লাউড রান উভয়ের সামঞ্জস্যের জন্য থ্রেড ব্যবহার
    t = threading.Thread(target=main_loop)
    t.start()
    
    # ডামি ওয়েব সার্ভার চালু করা
    run_app()
