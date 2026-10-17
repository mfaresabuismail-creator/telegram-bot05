import os
import time
import requests
from html.parser import HTMLParser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- خادم ويب لإرضاء منصة Render والبقاء مجاناً ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- الإعدادات الأساسية ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "test_test373").replace("@", "").strip()
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@hakar_ae").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))

class TelegramHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.messages = []
        self._in_message = False
        self._current_text = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        if 'tgme_widget_message_text' in classes:
            self._in_message = True
            self._current_text = []

    def handle_data(self, data):
        if self._in_message:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if tag == 'div' and self._in_message:
            self._in_message = False
            full_text = "".join(self._current_text).strip()
            if full_text:
                self.messages.append(full_text)

def get_latest_posts():
    """جلب الرسائل مباشرة من صفحة المعاينة العامة لتليجرام بدون RSS"""
    url = f"https://t.me/s/{SOURCE_CHANNEL}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Web Preview Status Code: {response.status_code}")
        if response.status_code == 200:
            parser = TelegramHTMLParser()
            parser.feed(response.text)
            posts = []
            for msg in parser.messages:
                posts.append({"guid": msg[:50], "text": msg})
            return posts
        else:
            print(f"Failed to fetch page, status: {response.status_code}")
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
    print(f"بدأ البوت بمراقبة القناة العامة (@{SOURCE_CHANNEL}) مباشرة...")
    
    while True:
        posts = get_latest_posts()
        if posts:
            latest_post = posts[-1]  # أحدث رسالة في الأسفل
            post_id = latest_post["guid"]
            
            if last_sent_id is None:
                last_sent_id = post_id
                print("تم ضبط المعرف الأساسي للرسائل بنجاح.")
            elif post_id != last_sent_id:
                last_sent_id = post_id
                clean_text = latest_post["text"]
                if clean_text:
                    print("رسالة جديدة اكتشفت، جاري الإرسال للقناة المستهدفة...")
                    send_telegram_message(clean_text)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    main_bot()
