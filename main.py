import os
import asyncio
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError


# ==================================================
# 1. السجلات
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

log = logging.getLogger("telegram_sync")


# ==================================================
# 2. إعدادات Render
# ==================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"].strip()
SESSION_STRING = os.environ["SESSION_STRING"].strip()
PORT = int(os.environ.get("PORT", "10000"))

if not SESSION_STRING:
    raise RuntimeError("متغير SESSION_STRING فارغ")

CHANNEL_PAIRS = []

for i in range(4):
    suffix = "" if i == 0 else str(i)

    source = os.getenv(f"SOURCE_CHAT{suffix}", "").strip()
    target = os.getenv(f"TARGET_CHAT{suffix}", "").strip()

    if source and target:
        CHANNEL_PAIRS.append((source, target))
    elif source or target:
        log.error(
            "زوج القنوات رقم %s غير مكتمل؛ يجب ضبط المصدر والوجهة",
            i + 1,
        )

if not CHANNEL_PAIRS:
    raise RuntimeError("لم يتم ضبط أي زوج قنوات مكتمل")

log.info("عدد أزواج القنوات المكتملة: %s", len(CHANNEL_PAIRS))


# ==================================================
# 3. خادم الصحة الخاص بـ Render
# ==================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_response(404)
            self.end_headers()
            return

        body = b"Telegram sync process is running"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return


def start_web_server():
    try:
        server = ThreadingHTTPServer(
            ("0.0.0.0", PORT),
            HealthHandler,
        )
        log.info("HTTP health server يعمل على المنفذ %s", PORT)
        server.serve_forever()
    except Exception:
        log.exception("تعذر تشغيل خادم HTTP")


# ==================================================
# 4. عميل تيليجرام
# ==================================================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH,
)

TARGETS = {}
SOURCE_LABELS = {}


# ==================================================
# 5. نقل الرسالة
# ==================================================

async def copy_message(message, target):
    """
    نقل رسالة نصية أو ذات وسائط.
    لا يتجاوز حماية المحتوى التي يفرضها تيليجرام.
    """

    if message.media:
        await client.send_file(
            target,
            message.media,
            caption=message.message or "",
            formatting_entities=message.entities,
        )

    elif message.message:
        await client.send_message(
            target,
            message.message,
            formatting_entities=message.entities,
            link_preview=bool(message.web_preview),
        )

    else:
        log.warning(
            "رسالة لا تحتوي على نص أو وسائط قابلة للنقل: id=%s",
            message.id,
        )


# ==================================================
# 6. معالجة المنشورات الجديدة
# ==================================================

async def process_new_message(event):
    message = event.message
    source_id = event.chat_id
    target = TARGETS.get(source_id)

    log.info(
        "حدث رسالة جديد: source_id=%s message_id=%s",
        source_id,
        message.id,
    )

    if target is None:
        log.error("لا توجد وجهة مرتبطة بالمصدر %s", source_id)
        return

    try:
        await copy_message(message, target)

        log.info(
            "نجح نقل الرسالة: المصدر=%s الرسالة=%s",
            SOURCE_LABELS.get(source_id, str(source_id)),
            message.id,
        )

    except FloodWaitError as error:
        log.error(
            "فرض تيليجرام انتظارًا لمدة %s ثانية. لم تُعَد محاولة "
            "نقل الرسالة تلقائيًا؛ message_id=%s",
            error.seconds,
            message.id,
        )

    except Exception:
        log.exception(
            "فشل نقل الرسالة: source_id=%s message_id=%s",
            source_id,
            message.id,
        )


# ==================================================
# 7. تشغيل المراقبة
# ==================================================

async def main():
    log.info("بدء تشغيل عميل تيليجرام")

    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "جلسة تيليجرام غير مصرح بها. أنشئ جلسة جديدة وآمنة."
        )

    me = await client.get_me()

    log.info(
        "نجح تسجيل الدخول إلى تيليجرام؛ user_id=%s",
        me.id,
    )

    source_ids = []

    for source_name, target_name in CHANNEL_PAIRS:
        try:
            source = await client.get_entity(source_name)
            target = await client.get_entity(target_name)

            if source.id in TARGETS:
                log.warning(
                    "المصدر %s مكرر في الإعدادات؛ ستُستخدم آخر وجهة له",
                    source_name,
                )

            TARGETS[source.id] = target
            SOURCE_LABELS[source.id] = source_name

            if source.id not in source_ids:
                source_ids.append(source.id)

            log.info(
                "تم تجهيز الزوج: %s -> %s",
                source_name,
                target_name,
            )

        except Exception:
            log.exception(
                "فشل تجهيز الزوج: %s -> %s",
                source_name,
                target_name,
            )

    if not source_ids:
        raise RuntimeError(
            "لم يتم تجهيز أي مصدر. تحقق من صلاحية الوصول وأسماء القنوات."
        )

    # التسجيل بعد تجهيز المصادر
    client.add_event_handler(
        process_new_message,
        events.NewMessage(chats=source_ids),
    )

    log.info("عدد مصادر المراقبة: %s", len(source_ids))
    log.info("البوت جاهز لمراقبة المنشورات الجديدة")

    await client.run_until_disconnected()


# ==================================================
# 8. نقطة البداية
# ==================================================

if __name__ == "__main__":
    Thread(
        target=start_web_server,
        daemon=True,
    ).start()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("تم إيقاف البرنامج يدويًا")
    except Exception:
        log.exception("توقف البرنامج بسبب خطأ غير معالج")
        raise
