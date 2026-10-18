import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# 1. سيرفر الويب المصغر لضمان بقاء البوت يعمل 24/7 على Render
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
    'test_test373': '@hakar_ae',
    'malek_eldahab': '@malak_eldahab',
    'hpress': '@GazaNews_Live',
    'Mtqdmon': '@Applicants039'
}

client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def process_and_send(message, target):
    try:
        text = message.text or ''
        if text:
            # استبدال اليوزر المطلوب فقط في قناة malek_eldahab أو عموماً حسب الرغبة
            text = text.replace('@el_malek001', '@Gold_055')

        if message.media:
            await client.send_file(target, message.media, caption=text)
        elif text:
            await client.send_message(target, text)
    except Exception as e:
        print(f"خطأ أثناء إرسال الرسالة: {e}")

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
            await process_and_send(event.message, target)
            print(f"تم إرسال ونشر الرسالة الجديدة في الهدف: {target}")
    except Exception as e:
        print(f"حدث خطأ: {e}")

async def main():
    await client.start()
    print("تم الاتصال بتيليجرام بنجاح!")
    
    # جلب ونشر آخر 100 رسالة قديمة من كل قناة مصدر عند التشغيل لأول مرة
    for src, tgt in CHANNEL_MAPPING.items():
        try:
            print(f"جاري سحب آخر 100 رسالة من {src} إلى {tgt}...")
            async for message in client.iter_messages(src, limit=100):
                if message.text or message.media:
                    await process_and_send(message, tgt)
                    # فاصل زمني قصير لمنع الحظر من تيليجرام
                    await asyncio.sleep(1)
            print(f"تم الانتهاء من سحب الرسائل القديمة للقناة: {src}")
        except Exception as e:
            print(f"تنبيه أثناء سحب الرسائل القديمة لـ {src}: {e}")
        
    print("البوت يعمل الآن وجاهز لمراقبة الرسائل الجديدة 24/7...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
