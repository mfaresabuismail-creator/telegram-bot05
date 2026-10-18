import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# 1. إنشاء سيرفر ويب وهمي مصغر لضمان بقاء خدمة Render مستيقظة 24/7 وعدم إيقافها
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram Bot is active and running 24/7!")
        
    def log_message(self, format, *args):
        # إلغاء طباعة رسائل السيرفر الوهمي حتى لا تزدحم السجلات
        return

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# تشغيل سيرفر الويب في الخلفية بشكل متزامن
threading.Thread(target=run_web_server, daemon=True).start()

# 2. بيانات الاعتماد وبوت تيليجرام
api_id = 7871586
api_hash = 'c4692d3c5a30332fc359ecb2a61604fe'

string_session = os.environ.get('SESSION_STRING', '')

# خريطة توجيه القنوات (المصدر -> الهدف)
CHANNEL_MAPPING = {
    'test_test373': '@hakar_ae',
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
        source_username = chat.username or ""
        source_id = str(chat.id)
        
        target = None
        for src, tgt in CHANNEL_MAPPING.items():
            if src.lower() in source_username.lower() or src in source_id:
                target = tgt
                break

        if target:
            # نشر الرسالة في الهدف بدون مصدر
            if event.message.media:
                await client.send_file(target, event.message.media, caption=event.message.text or '')
            elif event.message.text:
                await client.send_message(target, event.message.text)
                
            print(f"تم إرسال ونشر الرسالة في الهدف بدون مصدر: {target}")
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال: {e}")

async def main():
    await client.start()
    print("تم الاتصال بتيليجرام بنجاح عبر StringSession وخادم الويب يعمل!")
    
    for src, tgt in CHANNEL_MAPPING.items():
        try:
            await client.get_entity(src)
        except Exception:
            pass
        try:
            await client.get_entity(tgt)
        except Exception:
            pass
        
    print("البوت يعمل الآن وجاهز لنشر الرسائل بدون مصدر 24/7 دون أن يتوقف...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
