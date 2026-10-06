import os
import logging
from dotenv import load_dotenv
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
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==============================
# MAIN
# ==============================
async def main():
    client = TelegramClient("session", api_id, api_hash)
    await client.start()
    logger.info("Connected to Telegram ✅")

    os.makedirs(download_dir, exist_ok=True)

    # Open text log
    with open(text_log_file, "a", encoding="utf-8") as f:
        logger.info(f"Fetching messages from channel: {channel_username}")

        async for message in client.iter_messages(channel_username, reverse=True):
            # Save text messages
            if message.message:
                f.write(message.message + "\n")
                f.write("=" * 50 + "\n")
                logger.info(f"Saved text message ID {message.id}")

            # Save files if extension is allowed
            if message.media and isinstance(message.media, MessageMediaDocument):
                file_name = message.file.name
                if file_name:
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in ALLOWED_EXTENSIONS:
                        save_path = os.path.join(download_dir, file_name)

                        if os.path.exists(save_path):
                            logger.info(f"File already exists, skipping: {file_name}")
                            continue

                        logger.info(f"Downloading file: {file_name}")

                        # Progress callback
                        def progress_callback(current, total):
                            percent = int(current * 100 / total)
                            logger.info(f"Downloading {file_name}... {percent}%")

                        await message.download_media(
                            file=save_path,
                            progress_callback=progress_callback
                        )
                        logger.info(f"Downloaded file: {save_path}")

    await client.disconnect()
    logger.info("Finished ✅")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())