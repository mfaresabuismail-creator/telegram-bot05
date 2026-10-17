import os
import asyncio
from aiohttp import web
from pyrogram import Client

API_ID = int(os.environ.get("API_ID", "39045345"))
API_HASH = os.environ.get("API_HASH", "7a9774c50c785dd4fb46ac6afe3ficc0")
SESSION_STRING = os.environ.get("SESSION_STRING")

# القنوات الجديدة المحددة
SOURCE_CHAT = "@test_test373"
TARGET_CHAT = "@hakar_ae"

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

async def monitor_channels():
    print("جاري تهيئة الاتصال بالقنوات وتخزين الذاكرة المؤقتة...")
    await asyncio.sleep(5)
    
    # 1. محاولة الانضمام التلقائي أو جلب معلومات القناة لحل مشكلة الصلاحيات والذاكرة المؤقتة
    try:
        source_peer = await app.get_chat(SOURCE_CHAT)
        print(f"تم التعرف على قناة المصدر بنجاح: {source_peer.title} (ID: {source_peer.id})")
    except Exception as e:
        print(f"خطأ في التعرف على قناة المصدر (تأكد من وجود الحساب فيها): {e}")

    try:
        target_peer = await app.get_chat(TARGET_CHAT)
        print(f"تم التعرف على قناة الهدف بنجاح: {target_peer.title} (ID: {target_peer.id})")
    except Exception as e:
        print(f"خطأ في التعرف على قناة الهدف: {e}")

    last_msg_id = 0
    
    # 2. تحديد آخر رسالة حالية لبدء المراقبة منها
    try:
        async for message in app.get_chat_history(SOURCE_CHAT, limit=1):
            last_msg_id = message.id
            print(f"آخر رسالة مسجلة حالياً في المصدر برقم ID: {last_msg_id}")
            break
    except Exception as e:
        print(f"تعذر جلب السجل الأولي للرسائل: {e}")

    # 3. حلقة المراقبة المستمرة بالفحص الدوري
    while True:
        try:
            await asyncio.sleep(10)  # الفحص كل 10 ثوانٍ
            
            async for message in app.get_chat_history(SOURCE_CHAT, limit=3):
                if message.id > last_msg_id:
                    print(f"تم رصد رسالة جديدة برقم ID: {message.id}، جاري نقلها إلى {TARGET_CHAT}...")
                    
                    # محاولة النسخ مع طباعة النتيجة بدقة
                    await message.copy(chat_id=TARGET_CHAT)
                    last_msg_id = message.id
                    print("تم نقل ونشر الرسالة بنجاح تام!")
                    
        except Exception as e:
            print(f"خطأ أثناء حلقة الفحص والدوري: {e}")

async def handle(request):
    return web.Response(text="Bot is Live and Running!")

async def main():
    # تشغيل سيرفر الويب لمنع النوم على Render
    server = web.Application()
    server.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # تشغيل جلسة البوت
    await app.start()
    print("تم تشغيل البوت بنجاح تام وبدأت فحص القنوات...")
    
    asyncio.create_task(monitor_channels())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
