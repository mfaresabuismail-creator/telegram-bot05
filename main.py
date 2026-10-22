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

# خريطة توجيه القنوات المحدثة (المصدر -> الهدف)
CHANNEL_MAPPING = {
    'test_test373': 'Gold_trading04',  # التعديل الجديد للقناة المصدر والهدف
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
            text = event.message.text or ''
            
            # الشروط الخاصة فقط بقناة المصدر test_test373 والهدف Gold_trading04
            if 'test_test373' in source_username.lower() or 'test_test373' in source_id:
                # 1. منع إرسال الرسالة إذا احتوت على أي من الرابطين المحظورين
                link1 = "https://web.mygtc.app/login/register?ref=JEwetYpP"
                link2 = "https://one.justmarkets.link/a/ir7ce086xo"
                if link1 in text or link2 in text:
                    print("تم تخطي الرسالة لاحتوائها على أحد روابط الإحالة الممنوعة.")
                    return

                # 2. استبدال اليوزر المطلوب حصرياً في هذه القناة
                if text:
                    text = text.replace('@EL_OSTORA_1', '@Gold_055')

            # القاعدة القديمة لقناة malek_eldahab إذا لزم الاحتفاظ بها
            if 'malek_eldahab' in source_username.lower() and target == '@malak_eldahab':
                if text:
                    text = text.replace('@el_malek001', '@Gold_055')

            if event.message.media:
                await client.send_file(target, event.message.media, caption=text)
            elif text:
                await client.send_message(target, text)
                
            print(f"تم إرسال ونشر الرسالة في الهدف بنجاح: {target}")
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال: {e}")

async def main():
    await client.start()
    print("تم الاتصال بتيليجرام بنجاح!")
    
    for src, tgt in CHANNEL_MAPPING.items():
        try:
            await client.get_entity(src)
        except Exception:
            pass
        try:
            await client.get_entity(tgt)
        except Exception:
            pass
        
    print("البوت يعمل الآن وجاهز لمراقبة ونشر الرسائل وتطبيق الفلاتر الجديدة 24/7...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
