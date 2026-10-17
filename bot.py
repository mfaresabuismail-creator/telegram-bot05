import os
import asyncio
from aiohttp import web
from pyrogram import Client

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHAT = "test_test373"
TARGET_CHAT = "hakar_ae"

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

async def monitor_channels():
    print("--- بدأ تشغيل خدمة المراقبة ---")
    await asyncio.sleep(5)
    
    try:
        # جلب الكيان البرمجي للقنوات لضمان استقرار الجلسة
        source_chat = await app.get_chat(SOURCE_CHAT)
        target_chat = await app.get_chat(TARGET_CHAT)
        print(f"تم ربط المصدر: {source_chat.title} والهدف: {target_chat.title}")
    except Exception as e:
        print(f"خطأ في ربط القنوات: {e}")

    last_msg_id = 0
    
    # التقاط أحدث رسالة حالية
    try:
        async for message in app.get_chat_history(SOURCE_CHAT, limit=1):
            last_msg_id = message.id
            print(f"آخر معرف رسالة تم تسجيله في البداية هو: {last_msg_id}")
            break
    except Exception as e:
        print(f"تعذر قراءة السجل الأولي: {e}")

    while True:
        try:
            await asyncio.sleep(8)  # الفحص كل 8 ثوانٍ
            
            # جلب آخر 5 رسائل للتحقق منها
            async for message in app.get_chat_history(SOURCE_CHAT, limit=5):
                if message.id > last_msg_id:
                    print(f"وجدنا رسالة جديدة! الرقم: {message.id}")
                    
                    # نسخ الرسالة إلى القناة الهدف
                    await message.copy(chat_id=TARGET_CHAT)
                    last_msg_id = message.id
                    print("تم النسخ والنشر بنجاح تام!")
                    
        except Exception as e:
            print(f"خطأ أثناء حلقة الفحص: {e}")

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
    print("تم بدء جلسة البوت بنجاح تام.")
    
    asyncio.create_task(monitor_channels())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
