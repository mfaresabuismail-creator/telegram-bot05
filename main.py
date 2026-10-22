import os
import asyncio
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# 1. سيرفر الويب المصغر لضمان استمرار عمل الاستضافة على Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram Bot is active and running 24/7!")
        
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# 2. بيانات الاعتماد وبوت تيليجرام
api_id = 7871586
api_hash = 'c4692d3c5a30332fc359ecb2a61604fe'

string_session = os.environ.get('SESSION_STRING', '')

# خريطة توجيه القنوات (المصدر -> الهدف)
CHANNEL_MAPPING = {
    'amirgolder_01': '@Gold_trading04',
    'malek_eldahab': '@malak_eldahab',
    'hpress': '@GazaNews_Live',
    'Mtqdmon': '@Applicants039'
}

client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage)
async def forward_handler(event):
    try:
        if not event.is_channel and not event.is_group:
            return
            
        chat = await event.get_chat()
        source_username = getattr(chat, 'username', '') or ''
        source_id = str(chat.id)
        
        target = None
        for src, tgt in CHANNEL_MAPPING.items():
            if src.lower() in source_username.lower() or src in source_id:
                target = tgt
                break

        if target:
            text = event.message.text or ''
            
            # 1. تصفية رابط الإحالة المخصص
            forbidden_link = "https://signup.godocm.com?ptr=2000217935&rm=390&agr=2788"
            if forbidden_link in text:
                print("تم تخطي الرسالة لاحتوائها على رابط الإحالة المحدد.")
                return

            # 2. معالجة الرسائل المتجهة لقناة Gold_trading04
            if target == '@Gold_trading04':
                if text:
                    # استبدال أي يوزر بـ @Gold_055
                    text = re.sub(r'@[A-Za-z0-9_]+', '@Gold_055', text)
                
                # إضافة الهاشتاغات تلقائياً
                hashtags = "\n\n#الذهب #xauusd"
                text = (text + hashtags) if text else hashtags

            # 3. إرسال المحتوى إلى القناة الهدف
            if event.message.media:
                await client.send_file(target, event.message.media, caption=text)
            elif text:
                await client.send_message(target, text)
                
            print(f"تم بنجاح نقل الرسالة إلى الهدف: {target}")
    except Exception as e:
        print(f"حدث خطأ أثناء نقل الرسالة: {e}")

# دالة دورية لإبقاء اتصال تيليجرام حياً 24/7
async def keep_alive_ping():
    while True:
        await asyncio.sleep(60)
        try:
            if client.is_connected():
                await client.get_me()
        except Exception:
            pass

async def main():
    while True:
        try:
            await client.start()
            print("تم الاتصال بتيليجرام بنجاح!")
            
            # تحديث معرفات القنوات المباشرة
            for src, tgt in CHANNEL_MAPPING.items():
                try:
                    await client.get_entity(src)
                except Exception:
                    pass
                try:
                    await client.get_entity(tgt)
                except Exception:
                    pass
                
            print("البوت يعمل الآن ومستعد لنقل الرسائل 24/7...")
            
            # تشغيل دالة إبقاء الاتصال حياً
            asyncio.create_task(keep_alive_ping())
            
            await client.run_until_disconnected()
        except Exception as e:
            print(f"حدث انقطاع في الاتصال: {e}. إعادة المحاولة بعد 5 ثوانٍ...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
