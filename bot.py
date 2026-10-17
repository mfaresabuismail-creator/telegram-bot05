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

# متغيّر لتخزين معرّف آخر رسالة تم نقلها
last_copied_id = 0

async def check_new_messages():
    global last_copied_id
    
    # جلب آخر رسالة نُشرت بالقناة عند تشغيل البوت لأول مرة
    try:
        async for msg in app.get_chat_history(SOURCE_CHAT, limit=1):
            last_copied_id = msg.id
            print(f"تم بدء المراقبة، آخر رسالة حالية هي رقم: {last_copied_id}")
    except Exception as e:
        print(f"خطأ في الوصول إلى القناة المصدر: {e}")

    while True:
        try:
            await asyncio.sleep(10)  # الفحص كل 10 ثوانٍ
            
            # جلب الرسائل الجديدة التي صدرت بعد آخر رسالة تم حفظها
            async for message in app.get_chat_history(SOURCE_CHAT, limit=5):
                if message.id > last_copied_id:
                    print(f"تم العثور على رسالة جديدة ID: {message.id}، جاري نقلها...")
                    await message.copy(chat_id=TARGET_CHAT)
                    last_copied_id = message.id
                    print("تم النقل بنجاح!")
                    
        except Exception as e:
            print(f"خطأ أثناء الفحص الدوري: {e}")

async def handle(request):
    return web.Response(text="Bot is Live and Running!")

async def main():
    # تشغيل سيرفر الويب لمنع Render من النوم
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # تشغيل التليجرام والمراقبة
    await app.start()
    print("البوت يعمل الآن بنظام الفحص الدوري للأعضاء العاديين!")
    
    # بدء عملية التفقّد المستمر
    asyncio.create_task(check_new_messages())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
