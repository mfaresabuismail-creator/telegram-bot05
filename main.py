import os
import time
import requests
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- خادم ويب لإرضاء منصة Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- الإعدادات ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "test_test373").replace("@", "").strip()
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@hakar_ae").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))

def get_latest_posts():
    """جلب أحدث الرسائل مع طباعة الحالة للتشخيص"""
    url = f"https://rsshub.app/telegram/channel/{SOURCE_CHANNEL}"
    try:
        response = requests.get(url, timeout=10)
        print(f"RSS Status Code: {response.status_code}") # طباعة حالة الاستجابة في السجلات
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            posts = []
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                guid = item.find("guid").text if item.find("guid") is not None else ""
                posts.append({"guid": guid, "text": description or title})
            print(f"Found {len(posts)} posts from RSS.")
            return posts
        else:
            print(f"Failed to fetch RSS, content: {response.text[:200]}")
    except Exception as e:
        print(f"خطأ أثناء جلب الرسائل: {e}")
    return []

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHANNEL,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print(f"Telegram API Response: {res.status_code}")
    except Exception as e:
        print(f"خطأ أثناء الإرسال: {e}")

def main_bot():
    last_sent_id = None
    print(f"بدأ البوت بمراقبة القناة (@{SOURCE_CHANNEL})...")
    
    while True:
        posts = get_latest_posts()
        if posts:
            latest_post = posts[0]
            post_id = latest_post["guid"]
            
            if last_sent_id is None:
                last_sent_id = post_id
                print(f"Initial post ID set to: {post_id}")
            elif post_id != last_sent_id:
                last_sent_id = post_id
                clean_text = latest_post["text"]
                if clean_text:
                    print("رسالة جديدة اكتشفت، جاري الإرسال...")
                    send_telegram_message(clean_text)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    main_bot()
