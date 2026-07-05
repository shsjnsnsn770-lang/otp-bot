import requests
import time

# ==================== কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = "8910208193:AAGRJDmNA4bkMRFsDBlLMN5fDG3HjQ1DZHE"
TELEGRAM_CHAT_ID = "-1004358010030"

API_USERNAME = "RamAli25"
API_PASSWORD = "md7247600@gmail.com"

# আপনি যদি চান সব নাম্বারের ওটিপি আসবে, তবে নিচের লাইনটি এভাবেই রাখুন।
# আর যদি নির্দিষ্ট একটি নাম্বারের ওটিপি চান, তবে None কেটে "017XXXXXXXX" লিখে দিন।
TARGET_NUMBER = None 
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
                print(f"বট চালু হয়েছে। বর্তমান SMS ID: {latest_id} এর পর থেকে চেক করা হচ্ছে...")
                return

            for sms in reversed(sms_list):
                current_id = sms.get('id')
                sender = sms.get('from')      
                receiver = sms.get('to')      
                message = sms.get('text')     
                
                if TARGET_NUMBER and receiver != TARGET_NUMBER:
                    latest_id = current_id
                    continue
                
                # মেসেজে ওটিপি বা কোড থাকলে টেলিগ্রামে পাঠাবে
                if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin"]):
                    alert_text = (
                        f"🔔 *নতুন OTP রিসিভ হয়েছে!*\n\n"
                        f"📱 *নাম্বার:* `{receiver}`\n"
                        f"📩 *মেসেজ:* {message}\n"
                        f"🆔 *SMS ID:* {current_id}"
                    )
                    send_telegram_message(alert_text)
                    print(f"টেলিগ্রামে পাঠানো হয়েছে, SMS ID: {current_id}")
                
                latest_id = current_id

        elif response.status_code == 401:
            print("ভুল ইউজারনেম বা পাসওয়ার্ড দেওয়া হয়েছে।")
        else:
            print(f"API সমস্যা! স্ট্যাটাস কোড: {response.status_code}")
            
    except Exception as e:
        print(f"রিকোয়েস্ট ফেইল্ড: {e}")

print("টেলিগ্রাম ওটিপি ফরওয়ার্ডার বট রান হচ্ছে...")
while True:
    fetch_new_sms()
    time.sleep(5) # প্রতি ৫ সেকেন্ড পর পর নতুন এসএমএস চেক করবে