import os
import time
import threading
import logging
import requests

from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ---------------- إعدادات السجل ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("telegram-sync")

# ---------------- خادم Render ----------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram sync service is running.")

    def log_message(self, *args):
        pass


def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ---------------- الإعدادات السرية ----------------

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# لا تضع ملف الجلسة في GitHub.
# سنحتاج لاحقًا إلى إعداد تخزين دائم وآمن له على Render.
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()

# ---------------- ربط القنوات ----------------

def get_channel_pairs():
    pairs = []

    # المصدر الأول والهدف الأول
    # ثم المصدر الثاني والهدف الثاني وهكذا
    for index in range(4):
        suffix = "" if index == 0 else str(index)

        source = os.getenv(f"SOURCE_CHAT{suffix}", "").strip()
        target = os.getenv(f"TARGET_CHAT{suffix}", "").strip()

        if source and target:
            pairs.append((source, target))

    return pairs


CHANNEL_PAIRS = get_channel_pairs()

# ---------------- التحقق من الإعدادات ----------------

if not SESSION_STRING:
    raise RuntimeError(
        "متغير SESSION_STRING غير موجود. "
        "يجب إعداد جلسة Telethon بطريقة آمنة قبل التشغيل."
    )

if not CHANNEL_PAIRS:
    raise RuntimeError(
        "لم يتم العثور على أزواج قنوات مصدر وهدف في متغيرات البيئة."
    )


# ---------------- عميل تيليجرام ----------------

client = TelegramClient(
    TelegramClient.session if False else SESSION_STRING,
    API_ID,
    API_HASH
)


# ---------------- تشغيل المزامنة ----------------

async def main():
    await client.start()

    me = await client.get_me()
    log.info("تم تسجيل الدخول بنجاح: %s", me.first_name)

    for source_name, target_name in CHANNEL_PAIRS:
        log.info("ربط المصدر %s بالهدف %s", source_name, target_name)

    log.warning(
        "تم الاتصال. لم يبدأ نقل المنشورات التاريخية بعد؛ "
        "يلزم إعداد سجل دائم للتقدم قبل تفعيل المزامنة."
    )

    await client.run_until_disconnected()


if __name__ == "__main__":
    threading.Thread(
        target=run_web_server,
        daemon=True
    ).start()

    with client:
        client.loop.run_until_complete(main())
