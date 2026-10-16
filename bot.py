import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from aiohttp import web

API_ID = int(os.environ.get("API_ID", "1234567"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SOURCE_CHAT = os.environ.get("SOURCE_CHAT", "@SourceChannelUsername")
TARGET_CHAT = os.environ.get("TARGET_CHAT", "@YourTargetChannelUsername")

app = Client(
    "my_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.chat(SOURCE_CHAT))
async def forward_messages(client: Client, message: Message):
    try:
        await message.copy(chat_id=TARGET_CHAT)
        print(f"تم نسخ الرسالة رقم {message.id} بنجاح.")
    except Exception as g:
        print(f"خطأ: {g}")

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    while True:
        await asyncio.sleep(3600)

async def main():
    asyncio.create_task(web_server())
    await app.start()
    print("البوت وخادم الويب يعملان معاً بنجاح!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
