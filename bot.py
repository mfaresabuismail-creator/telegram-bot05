import os
import re
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

# خريطة القنوات المحددة
CHANNELS_MAP = {
    "@hpress": "@GazaNews_Live",
    "@malek_eldahab": "@malak_eldahab", # يمكنك إبقاء أو إزالة هذه القناة حسب رغبتك
}

# قائمة الاستبدالات المخصصة للروابط
LINK_REPLACEMENTS = {
    "https://t.me/hpress": "https://t.me/GazaNews_Live",
    "http://t.me/hpress": "https://t.me/GazaNews_Live",
}

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.chat(list(CHANNELS_MAP.keys())))
async def forward_messages(client, message):
    try:
        target_chat = None
        for src, tgt in CHANNELS_MAP.items():
            if message.chat.username and src.lower() == f"@{message.chat.username.lower()}":
                target_chat = tgt
                break
        
        if target_chat:
            # الحصول على نص الرسالة أو التعليق المرفق مع الوسائط
            text = message.text or message.caption
            
            if text:
                # استبدال رابط المصدر برابط قناتك الهدف
                updated_text = text
                for old_link, new_link in LINK_REPLACEMENTS.items():
                    updated_text = re.sub(re.escape(old_link), new_link, updated_text, flags=re.IGNORECASE)
                
                # إرسال الرسالة مع النص المحدث
                if message.media:
                    await message.copy(chat_id=target_chat, caption=updated_text)
                else:
                    await client.send_message(chat_id=target_chat, text=updated_text)
            else:
                # إذا كانت الرسالة عبارة عن وسائط بدون نص
                await message.copy(chat_id=target_chat)
                
            print(f"تم نسخ الرسالة واستبدال الرابط بنجاح إلى {target_chat}")
    except Exception as e:
        print(f"خطأ أثناء معالجة الرسالة: {e}")

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
    print("البوت يعمل الآن ويقوم باستبدال الروابط المحددة تلقائياً!")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
