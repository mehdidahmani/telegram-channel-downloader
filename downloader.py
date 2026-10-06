import os
import logging
from dotenv import load_dotenv
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument

# ==============================
# CONFIG
# ==============================
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")

if not api_id or not api_hash or not channel_username:
    raise SystemExit("Missing API_ID, API_HASH or CHANNEL_USERNAME. Set them in your .env file.")

api_id = int(api_id)

download_dir = "downloads"
text_log_file = "channel_messages.txt"

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".zip", ".doc", ".docx", ".rar", ".apk", ".txt", ".plp", ".key", ".exe", ".torrent"}

# ==============================
# LOGGING (Terminal only)
# ==============================
logging.basicConfig(format="%(asctime)s | %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
logging.getLogger("telethon").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def human_size(num):
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


# ==============================
# MAIN
# ==============================
async def main():
    stats = {"texts": 0, "downloaded": 0, "skipped": 0, "bytes": 0}

    client = TelegramClient("session", api_id, api_hash)
    await client.start()
    logger.info("✅ Connected to Telegram")

    os.makedirs(download_dir, exist_ok=True)

    total = (await client.get_messages(channel_username, limit=0)).total
    logger.info(f"📡 Channel: @{channel_username} ({total} messages)")
    logger.info("-" * 60)

    with logging_redirect_tqdm(), open(text_log_file, "a", encoding="utf-8") as f:
        index = 0
        width = len(str(total))

        async for message in client.iter_messages(channel_username, reverse=True):
            index += 1
            prefix = f"[{index:>{width}}/{total}]"

            # Save text messages (silent, counted in the summary)
            if message.message:
                f.write(message.message + "\n")
                f.write("=" * 50 + "\n")
                stats["texts"] += 1

            # Save files if extension is allowed
            if message.media and isinstance(message.media, MessageMediaDocument):
                file_name = message.file.name
                if not file_name:
                    continue

                ext = os.path.splitext(file_name)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                save_path = os.path.join(download_dir, file_name)

                if os.path.exists(save_path):
                    stats["skipped"] += 1
                    logger.info(f"{prefix} ⏭️  Skipped (exists): {file_name}")
                    continue

                size = message.file.size or 0
                logger.info(f"{prefix} ⬇️  {file_name} ({human_size(size)})")

                with tqdm(
                    total=size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="    ",
                    bar_format="{desc}{percentage:3.0f}%|{bar:30}| {n_fmt}/{total_fmt} [{rate_fmt}, {remaining}]",
                    leave=False,
                ) as bar:
                    def progress_callback(current, total_bytes, bar=bar):
                        bar.update(current - bar.n)

                    await message.download_media(file=save_path, progress_callback=progress_callback)

                stats["downloaded"] += 1
                stats["bytes"] += size
                logger.info(f"{prefix} ✅ Saved: {save_path}")

    await client.disconnect()

    logger.info("-" * 60)
    logger.info(
        f"🏁 Finished | texts: {stats['texts']} | downloaded: {stats['downloaded']} "
        f"({human_size(stats['bytes'])}) | skipped: {stats['skipped']}"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())