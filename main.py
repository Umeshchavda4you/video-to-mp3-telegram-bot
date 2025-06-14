import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import aiofiles
import subprocess

API_ID = int(os.getenv("API_ID", "1310650"))  # Replace with your actual API_ID
API_HASH = os.getenv("API_HASH", "8b85f95e0e07d0aee4fa812ce9ea46f4")  # Replace with your actual API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7756547155:AAFZlx3EX42GIsxj_Y-hiX5lIiBEutxFHqQ")  # Replace with your bot token

app = Client("video_to_audio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

saved_files = {}

async def convert_to_mp3(input_path, output_path):
    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-i", input_path, "-vn", "-c:a", "libmp3lame", "-q:a", "2", output_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()

@app.on_message(filters.video & filters.private)
async def video_handler(client: Client, message: Message):
    video = message.video
    file_name = video.file_name or "video"
    file_size = round(video.file_size / (1024 * 1024), 2)
    base_name = file_name.rsplit(".", 1)[0]
    input_path = f"downloads/{file_name}"
    output_path = f"downloads/{base_name}.mp3"

    await message.reply_text("📥 Downloading video...")
    await client.download_media(message, file_name=input_path)

    await message.reply_text("🎵 Converting to MP3...")
    await convert_to_mp3(input_path, output_path)

    caption = f"<b>{base_name}.mp3</b> | <i>{file_size} MB</i>"

    async with aiofiles.open(output_path, "rb") as f:
        await message.reply_document(document=f, caption=caption, parse_mode="html")

    os.remove(input_path)
    os.remove(output_path)

@app.on_message(filters.command(["save"]) & filters.private)
async def save_file(client, message):
    if len(message.command) < 2 or not message.reply_to_message:
        return await message.reply("❗ Reply to a media message with /save <name>")

    key = message.command[1].lower()
    saved_files[key] = message.reply_to_message
    await message.reply(f"✅ Saved file as '{key}'")

@app.on_message(filters.command(["get"]) & filters.private)
async def get_file(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Use /get <name> to retrieve saved file")

    key = message.command[1].lower()
    if key in saved_files:
        saved = saved_files[key]
        await saved.copy(message.chat.id)
    else:
        await message.reply("❌ No file saved with that name")

@app.on_message(filters.command(["start", "help"]) & filters.private)
async def start(client, message):
    await message.reply(
        "👋 Send me a video to convert it to MP3.\n"
        "💾 Use /save <name> by replying to any file to save it.\n"
        "📂 Use /get <name> to retrieve the saved file."
    )

if __name__ == "__main__":
    app.run()
