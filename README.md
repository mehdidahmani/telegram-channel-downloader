# Telegram Channel Downloader

Download media and messages from Telegram channels using the Telegram API (Telethon).

## Setup

1. Get `api_id` and `api_hash` at <https://my.telegram.org> → API development tools.
2. Install:
   ```bash
   git clone https://github.com/mehdidahmani/telegram-channel-downloader.git
   cd telegram-channel-downloader
   pip install -r requirements.txt
   ```
3. Create `.env`:
   ```env
   API_ID=1234567
   API_HASH=your_api_hash
   ```

On first run, log in with your phone number and code. A `.session` file is saved, so keep it private.




Downloads are resumable: existing files are skipped.

## Notes

- Works only on channels you can access (public or joined).
- Respects "Restrict saving content" and handles `FloodWait` automatically.
- Use only for content you have the right to download, and follow Telegram's [Terms of Service](https://telegram.org/tos).


## Work in progress
Change made without commit (stash demo).
