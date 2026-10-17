import os
import asyncio
from aiohttp import web
from pyrogram import Client

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHAT = "@hpress"
TARGET_CHAT = "@GazaNews_Live"

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

last_copied_id = 0

async def check_new_messages():
    global last_copied_id
    
    # الحصول على رقم آخر رسالة عند بدء التشغيل
    try:
        async for msg in app.get_chat_history(SOURCE_CHAT, limit=1):
            last_copied_id = msg.id
            print(f"تم بدء المراقبة بنجاح، رقم آخر رسالة: {last_copied_id}")
    except Exception as e:
        print(f"خطأ عند قراءة سجل القناة: {e}")

    while True:
        try:
            await asyncio.sleep(10)  # الفحص كل 10 ثوانٍ
            
            # جلب الرسائل الجديدة
            messages_to_copy = []
            async for message in app.get_chat_history(SOURCE_CHAT, limit=5):
                if message.id > last_copied_id:
                    messages_to_copy.append(message)
            
            # ترتيب الرسائل من القديم للحديث لنقلها بالترتيب الصحيح
            messages_to_copy.reverse()
            
            for message in messages_to_copy:
                print(f"جاري نقل الرسالة رقم: {message.id}")
                await message.copy(chat_id=TARGET_CHAT)
                last_copied_id = message.id
                print("تم نقل الرسالة بنجاح!")
                
        except Exception as e:
            print(f"خطأ أثناء الفحص: {e}")

async def handle(request):
    return web.Response(text="Bot is Live!")

async def start_services():
    # 1. تشغيل سيرفر الويب
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print("سيرفر الويب يعمل بنجاح!")

    # 2. تشغيل التليجرام
    await app.start()
    print("تم الاتصال بحساب التليجرام!")
    
    # 3. تشغيل عملية المراقبة الدورية
    asyncio.create_task(check_new_messages())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_services())
    loop.run_forever()
