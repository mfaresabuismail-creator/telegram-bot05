import os
import re
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

# خريطة القنوات (قناة المصدر: قناة الهدف)
CHANNELS_MAP = {
    "hpress": "GazaNews_Live",
    "malek_eldahab": "malak_eldahab",
}

# استبدال الروابط
LINK_REPLACEMENTS = {
    "https://t.me/hpress": "https://t.me/GazaNews_Live",
    "http://t.me/hpress": "https://t.me/GazaNews_Live",
}

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.channel)
async def forward_messages(client, message):
    try:
        # الحصول على معرف القناة الحالية بدون علامة @
        chat_username = message.chat.username
        if not chat_username:
            return

        target_chat = None
        for src, tgt in CHANNELS_MAP.items():
            if chat_username.lower() == src.lower():
                target_chat = f"@{tgt}"
                break

        if target_chat:
            print(f"وصلت رسالة جديدة من @{chat_username}، جاري التوجيه إلى {target_chat}...")
            
            # استخراج النص أو التعليق
            text = message.text or message.caption
            
            if text:
                # استبدال الروابط
                updated_text = text
                for old_link, new_link in LINK_REPLACEMENTS.items():
                    updated_text = re.sub(re.escape(old_link), new_link, updated_text, flags=re.IGNORECASE)
                
                if message.media:
                    await message.copy(chat_id=target_chat, caption=updated_text)
                else:
                    await client.send_message(chat_id=target_chat, text=updated_text)
            else:
                await message.copy(chat_id=target_chat)
                
            print(f" تم نقل الرسالة بنجاح إلى {target_chat}")
            
    except Exception as e:
        print(f" خطأ أثناء التوجيه: {e}")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await app.start()
    print(" البوت يعمل ويراقب القنوات الآن...")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
