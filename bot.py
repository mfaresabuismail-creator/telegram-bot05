import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", "1234567"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SOURCE_CHAT = os.environ.get("SOURCE_CHAT", "@SourceChannelUsername")
TARGET_CHAT = os.environ.get("TARGET_CHAT", "@YourTargetChannelUsername")

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHAT))
async def forward_messages(client, message):
    try:
        await message.copy(chat_id=TARGET_CHAT)
        print(f"تم نسخ الرسالة بنجاح.")
    except Exception as e:
        print(f"خطأ: {e}")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    # تشغيل سيرفر الويب الخاص بمنصة Render
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # تشغيل بوت تيليجرام
    await app.start()
    print("البوت يعمل الآن بنجاح مع سيرفر الويب!")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
