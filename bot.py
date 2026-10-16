import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", "1234567"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SOURCE_CHAT = os.environ.get("SOURCE_CHAT", "@SourceChannelUsername")
TARGET_CHAT = os.environ.get("TARGET_CHAT", "@YourTargetChannelUsername")

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHAT))
async def forward_messages(client: Client, message: Message):
    try:
        await message.copy(chat_id=TARGET_CHAT)
        print(f"تم نسخ الرسالة رقم {message.id} بنجاح.")
    except Exception as g:
        print(f"خطأ: {g}")

if __name__ == "__main__":
    print("السكربت يعمل...")
    app.run()
