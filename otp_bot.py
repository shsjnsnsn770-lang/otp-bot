import requests
import time
import re
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 with 40+ Global Country Autodetect!"

def run_app():
    try:
        app.run(host='0.0.0.0', port=10000)
    except Exception:
        pass

# ==================== আপনার কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = "8884098961:AAE1UxFAH60LQaUdnB6q3MKN2VHJ8mw84Q0"
TELEGRAM_CHAT_ID = "-1004358010030"

API_USERNAME = "RamAli25"
API_PASSWORD = "md7247600@gmail.com"
# ==========================================================

API_URL = "https://iprns.stats.direct/rest/sms"
latest_stamp = None  

# নাম্বারের মাঝখানের অংশ হাইড করার ফাংশন
def mask_phone_number(phone):
    if not phone:
        return ""
    phone_str = str(phone)
    if len(phone_str) <= 7:
        return f"+{phone_str}"
    
    start = phone_str[:4]      # শুরুর ৪টি সংখ্যা
    end = phone_str[-3:]       # শেষের ৩টি সংখ্যা
    masked = "*" * (len(phone_str) - 7) # মাঝখানের সংখ্যা অনুযায়ী স্টার (*) বসবে
    return f"+{start}{masked}{end}"

# থার্ডপার্টি লাইব্রেরি ছাড়া গ্লোবাল কান্ট্রি কোড অটোমেটিক ডিটেকশন (৪০+ দেশ যুক্ত করা হয়েছে)
def get_global_country(phone):
    phone_str = str(phone)
    
    country_map = {
        # আপনার আগের মূল দেশগুলো
        "236": ("Central African Republic", "🇨🇫"),
        "241": ("Gabon", "🇬🇦"),
        "994": ("Azerbaijan", "🇦🇿"),
        "213": ("Algeria", "🇩🇿"),
        "961": ("Lebanon", "🇱🇧"),
        "880": ("Bangladesh", "🇧🇩"),
        "91": ("India", "🇮🇳"),
        "92": ("Pakistan", "🇵🇰"),
        "7": ("Russia/Kazakhstan", "🇷🇺"),
        "33": ("France", "🇫🇷"),
        "49": ("Germany", "🇩🇪"),
        "966": ("Saudi Arabia", "🇸🇦"),
        "971": ("UAE", "🇦🇪"),
        "60": ("Malaysia", "🇲🇾"),
        "65": ("Singapore", "🇸🇬"),
        "44": ("United Kingdom", "🇬🇧"),
        "1": ("USA/Canada", "🇺🇸"),
        
        # নতুন ৩০টি প্লাস দেশ (আপনার রিকোয়েস্ট অনুযায়ী)
        "974": ("Qatar", "🇶🇦"),
        "965": ("Kuwait", "🇰🇼"),
        "968": ("Oman", "🇴🇲"),
        "973": ("Bahrain", "🇧🇭"),
        "962": ("Jordan", "🇯🇴"),
        "20": ("Egypt", "🇪🇬"),
        "90": ("Turkey", "🇹🇷"),
        "27": ("South Africa", "🇿🇦"),
        "234": ("Nigeria", "🇳🇬"),
        "254": ("Kenya", "🇰🇪"),
        "212": ("Morocco", "🇲🇦"),
        " Tunis": ("Tunisia", "🇹🇳"),
        "216": ("Tunisia", "🇹🇳"),
        "964": ("Iraq", "🇮🇶"),
        "39": ("Italy", "🇮🇹"),
        "34": ("Spain", "🇪🇸"),
        "41": ("Switzerland", "🇨🇭"),
        "31": ("Netherlands", "🇳🇱"),
        "32": ("Belgium", "🇧🇪"),
        "46": ("Sweden", "🇸🇪"),
        "47": ("Norway", "🇳🇴"),
        "61": ("Australia", "🇦🇺"),
        "64": ("New Zealand", "🇳🇿"),
        "81": ("Japan", "🇯🇵"),
        "82": ("South Korea", "🇰🇷"),
        "86": ("China", "🇨🇳"),
        "62": ("Indonesia", "🇮🇩"),
        "66": ("Thailand", "🇹🇭"),
        "63": ("Philippines", "🇵🇭"),
        "84": ("Vietnam", "🇻🇳"),
        "94": ("Sri Lanka", "🇱🇰"),
        "977": ("Nepal", "🇳🇵"),
        "960": ("Maldives", "🇲🇻"),
        "55": ("Brazil", "🇧🇷"),
        "52": ("Mexico", "🇲🇽"),
        "54": ("Argentina", "🇦🇷")
    }
    
    # ৩ অক্ষরের কোড আগে চেক করবে, তারপর ২ অক্ষর, তারপর ১ অক্ষর
    for length in [3, 2, 1]:
        prefix = phone_str[:length]
        if prefix in country_map:
            return country_map[prefix]
            
    return "International", "🌍"

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
                return

            for sms in reversed(sms_list):
                current_stamp = sms.get('start_stamp')
                
                if current_stamp and current_stamp > latest_stamp:
                    message = sms.get('short_message') or ""
                    receiver = sms.get('destination_addr') or ""
                    source = sms.get('source_addr') or "Unknown"
                    
                    if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin", "password"]):
                        otp_code = extract_otp(message)
                        
                        # গ্লোবাল অটো কান্ট্রি নেম ও নাম্বার মাস্কিং
                        country_name, country_flag = get_global_country(receiver)
                        masked_number = mask_phone_number(receiver)
                        service_name = source.upper() if "Unknown" not in source else "Service"
                        
                        # আপনার ফাইনাল প্রিমিয়াম ফায়ার ফরম্যাট
                        alert_text = (
                            f"💥 {country_name} {service_name} OTP Detected\n\n"
                            f"📞 **Number:** `{masked_number}`\n"
                            f"🔑 **OTP:** `{otp_code}`\n"
                            f"🛠 **Service:** {service_name}\n"
                            f"🌍 **Country:** {country_name} {country_flag}\n"
                            f"⏰ **Time:** {current_stamp}\n\n"
                            f"✉️ **Message:**\n"
                            f"`{message}`"
                        )
                        
                        send_telegram_message(alert_text)
                        print(f"গ্লোবাল অটো কান্ট্রি মডেলে মেসেজ পাঠানো হয়েছে!")
                    
                    latest_stamp = current_stamp
    except Exception as e:
        print(f"Error: {e}")

def main_loop():
    while True:
        fetch_new_sms()
        time.sleep(5)

if __name__ == "__main__":
    t = threading.Thread(target=main_loop)
    t.start()
    run_app()
