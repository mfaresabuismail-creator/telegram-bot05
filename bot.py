import os
import re
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

# قائمة القنوات (اسم المصدر بدون @ : اسم الهدف بدون @)
CHANNELS_MAP = {
    "hpress": "GazaNews_Live",
    "malek_eldahab": "malak_eldahab",
}

# الروابط المراد استبدالها
LINK_REPLACEMENTS = {
    "https://t.me/hpress": "https://t.me/GazaNews_Live",
    "http://t.me/hpress": "https://t.me/GazaNews_Live",
}

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# الاستماع لكافة الرسائل في القنوات
@app.on_message(filters.group | filters.channel)
async def forward_messages(client, message):
    try:
        if not message.chat or not message.chat.username:
            return

        current_username = message.chat.username.lower()

        # البحث عن القناة الهدف
        target_username = None
        for src, tgt in CHANNELS_MAP.items():
            if current_username == src.lower():
                target_username = f"@{tgt}"
                break

        if not target_username:
            return

        print(f"وصلت رسالة من @{current_username}، جاري معالجتها إلى {target_username}...")

        # جلب النص أو التعليق
        text = message.text or message.caption or ""

        # استبدال الرابط إن وجد
        if text:
            for old_link, new_link in LINK_REPLACEMENTS.items():
                text = re.sub(re.escape(old_link), new_link, text, flags=re.IGNORECASE)

        # إعادة الإرسال
        if message.media:
            await message.copy(chat_id=target_username, caption=text)
        elif text:
            await client.send_message(chat_id=target_username, text=text)
        else:
            await message.copy(chat_id=target_username)

        print(f"تم الإرسال بنجاح إلى {target_username}")

    except Exception as e:
        print(f"حدث خطأ أثناء المعالجة: {e}")

async def handle(request):
    return web.Response(text="Bot is Live and Running!")

async def main():
    # تشغيل سيرفر الويب لبقاء الخدمة حية
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # تشغيل البوت
    await app.start()
    print("تم تشغيل البوت بنجاح وحساب المستخدم جاهز ومستقر!")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
