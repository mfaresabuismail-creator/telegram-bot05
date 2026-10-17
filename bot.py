import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

# القناة المصدر والهدف
SOURCE_CHAT = "hpress"
TARGET_CHAT = "@GazaNews_Live"

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.chat(SOURCE_CHAT))
async def forward_messages(client, message):
    try:
        # نسخ الرسالة كما هي بكل محتواها (نص، صور، روابط) إلى القناة الهدف مباشرة
        await message.copy(chat_id=TARGET_CHAT)
        print("تم نسخ الرسالة ونقلها بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء النسخ: {e}")

async def handle(request):
    return web.Response(text="Bot is Live and Running!")

async def main():
    # تشغيل سيرفر الويب المصغر لمنصة Render
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # تشغيل البوت
    await app.start()
    print("البوت يعمل الآن بنجاح تام وبدون أي تعقيدات!")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
