import requests
import time
import re
import threading
from flask import Flask
from phone_iso3166.country import phone_country

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 with Live Country Detector!"

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

# অটোমেটিক দেশের ফ্ল্যাগ জেনারেট করার ফাংশন
def get_flag(country_code):
    if not country_code or len(country_code) != 2:
        return "🌍"
    return chr(127397 + ord(country_code[0].upper())) + chr(127397 + ord(country_code[1].upper()))

# নাম্বার থেকে দেশের নাম ও ফ্ল্যাগ লাইভ বের করার ফাংশন
def get_live_country(phone):
    try:
        # ফোন নাম্বার থেকে ISO ২ অক্ষরের কোড বের করবে (যেমন: 'AZ', 'GA', 'BD')
        iso_code = phone_country(f"+{phone}")
        
        # ISO কোড থেকে পুরো দেশের নাম জানার এপিআই (টেলিগ্রামেরই ইন্টারনাল এপিআই ব্যবহার করে)
        res = requests.get(f"https://restcountries.com/v3.1/alpha/{iso_code}", timeout=5)
        if res.status_code == 200:
            country_data = res.json()
            country_name = country_data[0]['name']['common']
            flag = country_data[0].get('flag', get_flag(iso_code))
            return country_name, flag
        else:
            return iso_code, "🌍"
    except Exception:
        return "Unknown Country", "🌍"

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
                    
                    if any(keyword in message.lower() for keyword in ["otp", "code", "verification", "pin", "password", "telegram", "facebook", "whatsapp"]):
                        otp_code = extract_otp(message)
                        
                        # লাইভ কান্ট্রি ও ফ্ল্যাগ ডিটেকশন
                        country_name, country_flag = get_live_country(receiver)
                        service_name = source.upper() if "Unknown" not in source else "Service"
                        
                        # আপনার ফাইনাল প্রিমিয়াম ফায়ার মডেল
                        alert_text = (
                            f"{country_flag} **{country_name} {service_name} OTP Detected**\n\n"
                            f"📞 **Number:** `+{receiver}`\n"
                            f"🔑 **OTP:** **{otp_code}**\n"
                            f"🛠 **Service:** {service_name}\n"
                            f"🌍 **Country:** {country_name} {country_flag}\n"
                            f"⏰ **Time:** {current_stamp}\n\n"
                            f"✉️ **Message:**\n"
                            f"`{message}`"
                        )
                        
                        send_telegram_message(alert_text)
                        print(f"লাইভ কান্ট্রি মডেলে ওটিপি পাঠানো হয়েছে!")
                    
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
