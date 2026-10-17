import os
import time
import requests
import xml.etree.ElementTree as ET

# --- جلب البيانات من متغيرات البيئة تلقائياً ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_هنا_إذا_لم_تستخدم_متغيرات_البيئة")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "test_test373").replace("@", "").strip()
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@hakar_ae").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))

def get_latest_posts():
    """جلب أحدث الرسائل من أي قناة مصدر عامة عبر تغذية RSS"""
    url = f"https://rsshub.app/telegram/channel/{SOURCE_CHANNEL}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            posts = []
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                guid = item.find("guid").text if item.find("guid") is not None else ""
                posts.append({"guid": guid, "text": description or title})
            return posts
    except Exception as e:
        print(f"خطأ أثناء جلب الرسائل من القناة المصدر: {e}")
    return []

def send_telegram_message(text):
    """إرسال الرسائل إلى أي قناة مستهدفة محددة"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHANNEL,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"فشل الإرسال: {response.text}")
    except Exception as e:
        print(f"خطأ أثناء إرسال الرسالة: {e}")

def main():
    last_sent_id = None
    print(f"بدأ البوت بمراقبة القناة المصدر (@{SOURCE_CHANNEL}) والتوجيه إلى ({TARGET_CHANNEL})...")
    
    while True:
        posts = get_latest_posts()
        if posts:
            latest_post = posts[0]
            post_id = latest_post["guid"]
            
            if last_sent_id is None:
                last_sent_id = post_id
            elif post_id != last_sent_id:
                last_sent_id = post_id
                clean_text = latest_post["text"]
                if clean_text:
                    send_telegram_message(clean_text)
                    print("تم تحويل رسالة جديدة بنجاح!")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
