import requests
import time
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_app():
    app.run(host='0.0.0.0', port=10000)

# ==================== কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = "8910208193:AAGRJDmNA4bkMRFsDBlLMN5fDG3HjQ1DZHE"
TELEGRAM_CHAT_ID = "-1004358010030"

API_USERNAME = "RamAli25"
API_PASSWORD = "md7247600@gmail.com"
# ====================================================

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
    params = {"page": 1, "per-page": 5} # টেস্ট করার জন্য শুধু ৫টি ডাটা দেখব
    
    try:
        response = requests.get(API_URL, params=params, auth=(API_USERNAME, API_PASSWORD), timeout=15)
        
        if response.status_code == 200:
            sms_list = response.json()
            if not sms_list:
                print("API থেকে কোনো SMS ডাটা পাওয়া যায়নি (খালি রেসপন্স)।")
                return

            # --- গুরুত্বপূর্ণ টেস্টিং লাইন ---
            # এটি এপিআই থেকে আসা প্রথম মেসেজের পুরো ফরম্যাটটি Render লগে প্রিন্ট করবে
            print("--- API থেকে আসা আসল ডাটার নমুনা নিচে দেখুন ---")
            print(sms_list[0])
            print("------------------------------------------------")

            if latest_id is None:
                # যদি 'id' কী-টি সঠিক না হয়, তবে অন্য কী খুঁজতে হবে
                latest_id = sms_list[0].get('id') or sms_list[0].get('ID')
                return

            for sms in reversed(sms_list):
                current_id = sms.get('id') or sms.get('ID')
                
                # এখানে আমরা নাম বা ওটিপি ফিল্টার সাময়িকভাবে বন্ধ রাখছি 
                # যাতে যেকোনো নতুন মেসেজ আসামাত্রই টেলিগ্রামে টেস্ট মেসেজ চলে যায়
                if current_id and current_id > latest_id:
                    # এপিআই-এর ভেতরের মেসেজটি বের করার চেষ্টা
                    message_content = sms.get('text') or sms.get('message') or sms.get('msg') or str(sms)
                    
                    alert_text = f"🧪 *টেস্ট মেসেজ রিসিভ হয়েছে!*\n\n{message_content}"
                    send_telegram_message(alert_text)
                    latest_id = current_id

        else:
            print(f"API সমস্যা! স্ট্যাটাস কোড: {response.status_code}")
    except Exception as e:
        print(f"রিকোয়েস্ট ফেইল্ড: {e}")

def main_loop():
    print("টেস্টিং বট রান হচ্ছে...")
    while True:
        fetch_new_sms()
        time.sleep(10) # ১০ সেকেন্ড পর পর চেক করবে

if __name__ == "__main__":
    t = threading.Thread(target=main_loop)
    t.start()
    run_app()
