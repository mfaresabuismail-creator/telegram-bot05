import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# بيانات الاعتماد
api_id = 7871586
api_hash = 'c4692d3c5a30332fc359ecb2a61604fe'

# قراءة نص الجلسة من متغير البيئة SESSION_STRING في Render
string_session = os.environ.get('SESSION_STRING', '')

# خريطة توجيه القنوات (المصدر -> الهدف)
# يفضل استخدام معرفات الأرقام للمصدر إن أمكن، أو أسمائها الدقيقة
CHANNEL_MAPPING = {
    'test_test373': '@hokoz_os',
    'malek_eldahab': '@malak_eldahab',
    'hpress': '@GazaNews_Live',
    'stqdson': '@Applicants039'
}

client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage)
async def forward_handler(event):
    try:
        # التأكد من أن الرسالة قادمة من قناة/مجموعة
        if not event.is_channel and not event.is_group:
            return
            
        chat = await event.get_chat()
        source_username = chat.username or ""
        source_id = str(chat.id)
        
        target = None
        for src, tgt in CHANNEL_MAPPING.items():
            # مقارنة الاسم أو الـ ID لضمان المطابقة الدقيقة
            if src.lower() in source_username.lower() or src in source_id:
                target = tgt
                break

        if target:
            await client.forward_messages(target, event.message)
            print(f"تم توجيه رسالة من المصدر إلى {target} بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء التوجيه: {e}")

async def main():
    await client.start()
    print("تم الاتصال بتيليجرام بنجاح عبر StringSession!")
    
    # جلب الكاش لكل القنوات المصدر لضمان ربطها بالحساب وعدم ظهور خطأ عدم الارتباط
    for src in CHANNEL_MAPPING.keys():
        try:
            entity = await client.get_entity(src if src.startswith('@') or src.startswith('-') else src)
            print(f"تم ربط القناة المصدر بنجاح: {src} (ID: {entity.id})")
        except Exception as e:
            print(f"تنبيه: لم يتم العثور على الكيان للقناة {src}: {e}")
        
    print("البوت جاهز تماماً لمراقبة المنشورات الجديدة...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
