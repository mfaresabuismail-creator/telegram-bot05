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

async def monitor_channels():
    await asyncio.sleep(5)
    
    last_msg_id = 0
    try:
        async for message in app.get_chat_history(SOURCE_CHAT, limit=1):
            last_msg_id = message.id
            print(f"تم بنجاح الاتصال بقناة المصدر. آخر رسالة مسجلة ID: {last_msg_id}")
            break
    except Exception as e:
        print(f"تحذير: لم يتم قراءة سجل القناة مباشرة، السبب: {e}")

    while True:
        try:
            await asyncio.sleep(10)
            
            async for message in app.get_chat_history(SOURCE_CHAT, limit=3):
                if message.id > last_msg_id:
                    print(f"تم العثور على رسالة جديدة برقم ID: {message.id}، جاري نسخها...")
                    await message.copy(chat_id=TARGET_CHAT)
                    last_msg_id = message.id
                    print("تم نسخ ونشر الرسالة بنجاح تام!")
                    
        except Exception as e:
            print(f"خطأ دوري أثناء جلب الرسائل: {e}")

async def handle(request):
    return web.Response(text="Bot is Live and Running!")

async def main():
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await app.start()
    print("تم تشغيل البوت وحساب المستخدم بنجاح، وبدأت مراقبة القنوات...")
    
    asyncio.create_task(monitor_channels())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
