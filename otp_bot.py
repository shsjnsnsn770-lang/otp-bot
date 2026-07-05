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
    # Render অটোমেটিক পোর্ট ৫০ Plan বা অন্য পোর্টে রান করবে
    app.run(host='0.0.0.0', port=10000)

# ==================== আপনার আসল কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = "8910208193:AAGRJDmNA4bkMRFsDBlLMN5fDG3HjQ1DZHE"
TELEGRAM_CHAT_ID = "-1004358010030"

API_USERNAME = "RamAli25"
API_PASSWORD = "md7247600@gmail.com"

TARGET_NUMBER = None 
API_URL = "https://iprns.stats.direct/rest/sms"
latest_id = None  

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def fetch_new_sms():
    global latest_id
    params = {"page": 1, "per-page": 100}
    if latest_id:
        params["id"] = latest_id

    try:
        response = requests.get(API_URL, params=params, auth=(API_USERNAME, API_PASSWORD), timeout=15)
        
        if response.status_code == 200:
            sms_list = response.json()
            if not sms_list:
                return

            if latest_id is None:
                latest_id = sms_list[0].get('id')
                print(f"বট চালু হয়েছে। বর্তমান SMS ID: {latest_id}")
                return

            for sms in reversed(sms_list):
                current_id = sms.get('id')
                receiver = sms.get('to')      
                message = sms.get('text')     
                
                if TARGET_NUMBER and receiver != TARGET_NUMBER:
                    latest_id = current_id
                    continue
                
                if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin"]):
                    alert_text = (
                        f"🔔 *নতুন OTP রিসিভ হয়েছে!*\n\n"
                        f"📱 *নাম্বার:* `{receiver}`\n"
                        f"📩 *মেসেজ:* {message}\n"
                        f"🆔 *SMS ID:* {current_id}"
                    )
                    send_telegram_message(alert_text)
                    print(f"ტেলিগ্রামে পাঠানো হয়েছে, SMS ID: {current_id}")
                
                latest_id = current_id
        else:
            print(f"API সমস্যা! স্ট্যাটাস কোড: {response.status_code}")
    except Exception as e:
        print(f"রিকোয়েস্ট ফেইল্ড: {e}")

def main_loop():
    print("টেলিগ্রাম ওটিপি ফরওয়ার্ডার বট রান হচ্ছে...")
    while True:
        fetch_new_sms()
        time.sleep(5)

if __name__ == "__main__":
    # মেইন লুপটিকে আলাদা থ্রেডে চালানো যাতে ফ্ল্যাস্ক সার্ভার ব্লক না হয়
    t = threading.Thread(target=main_loop)
    t.start()
    
    # ডামি ওয়েব সার্ভার চালু করা
    run_app()
