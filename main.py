import os
import asyncio
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# ---------------- إعداد السجلات ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- إعدادات البيئة ----------------

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"].strip()

PORT = int(os.environ.get("PORT", "10000"))

CHANNEL_PAIRS = []

for i in range(4):
    suffix = "" if i == 0 else str(i)

    source = os.getenv(f"SOURCE_CHAT{suffix}", "").strip()
    target = os.getenv(f"TARGET_CHAT{suffix}", "").strip()

    if source and target:
        CHANNEL_PAIRS.append((source, target))

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING غير موجود")

if not CHANNEL_PAIRS:
    raise RuntimeError("لم يتم إعداد أزواج القنوات")


# ---------------- خادم HTTP ----------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            body = b"Telegram sync service is running"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logging.info("HTTP health server listening on port %s", PORT)
    server.serve_forever()


# ---------------- عميل تيليجرام ----------------

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

TARGETS = {}


async def copy_message(message, target):
    """نسخ رسالة جديدة نصية أو ذات وسائط فردية."""

    if message.media:
        await client.send_file(
            target,
            message.media,
            caption=message.message or "",
            formatting_entities=message.entities
        )
    elif message.message:
        await client.send_message(
            target,
            message.message,
            formatting_entities=message.entities,
            link_preview=bool(message.web_preview)
        )


async def main():
    await client.start()
    logging.info("تم الاتصال بتيليجرام")

    source_ids = []

    for source_name, target_name in CHANNEL_PAIRS:
        source = await client.get_entity(source_name)
        target = await client.get_entity(target_name)

        TARGETS[source.id] = target
        source_ids.append(source.id)

        logging.info(
            "تم تجهيز زوج القنوات: %s -> %s",
            source_name,
            target_name
        )

    @client.on(events.NewMessage(chats=source_ids))
    async def new_post(event):
        target = TARGETS.get(event.chat_id)

        if target is None:
            return

        try:
            await copy_message(event.message, target)
            logging.info("تم نقل منشور جديد من القناة %s", event.chat_id)

        except FloodWaitError as error:
            logging.warning(
                "طلب تيليجرام الانتظار %s ثانية",
                error.seconds
            )
            await asyncio.sleep(error.seconds)

        except Exception:
            logging.exception("فشل نقل المنشور")

    logging.info("البوت جاهز لمراقبة المنشورات الجديدة")
    await client.run_until_disconnected()


def run_telegram_client():
    asyncio.run(main())


if __name__ == "__main__":
    # تشغيل خادم HTTP في الخلفية
    Thread(target=start_web_server, daemon=True).start()

    # تشغيل متابعة تيليجرام
    run_telegram_client()
