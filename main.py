import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from moviepy.editor import VideoFileClip
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("conversions.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS conversions
                 (user_id INTEGER, conversion_count INTEGER, last_reset TEXT)"""
    )
    conn.commit()
    conn.close()

# Check and update conversion count
async def check_conversion_limit(user_id: int) -> bool:
    conn = sqlite3.connect("conversions.db")
    c = conn.cursor()
    c.execute("SELECT conversion_count, last_reset FROM conversions WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if result:
        count, last_reset = result
        if last_reset != current_date:
            # Reset count if it's a new day
            c.execute(
                "UPDATE conversions SET conversion_count = 0, last_reset = ? WHERE user_id = ?",
                (current_date, user_id),
            )
            count = 0
    else:
        # New user
        c.execute(
            "INSERT INTO conversions (user_id, conversion_count, last_reset) VALUES (?, 0, ?)",
            (user_id, current_date),
        )
        count = 0
    
    if count >= 100:
        conn.close()
        return False
    
    c.execute(
        "UPDATE conversions SET conversion_count = conversion_count + 1 WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()
    return True

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Video to Audio Converter Bot! Send me a video, and I'll convert it to audio (MP3). Limit: 100 conversions per day."
    )

# Handle video messages
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if not await check_conversion_limit(user_id):
        await update.message.reply_text(
            "You've reached the daily limit of 100 conversions. Try again tomorrow!"
        )
        return

    await update.message.reply_text("Processing your video... Please wait.")

    # Get the video file
    video_file = await update.message.video.get_file()
    video_path = f"temp_{user_id}.mp4"
    audio_path = f"temp_{user_id}.mp3"

    try:
        # Download video
        await video_file.download_to_drive(video_path)

        # Convert video to audio
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()

        # Send audio file
        with open(audio_path, "rb") as audio:
            await update.message.reply_audio(audio=audio, title="Converted Audio")

        # Clean up
        os.remove(video_path)
        os.remove(audio_path)

        await update.message.reply_text("Conversion complete! Send another video if you'd like.")
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await update.message.reply_text("Sorry, an error occurred while processing your video.")
        # Clean up in case of error
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")

def main() -> None:
    # Initialize database
    init_db()

    # Get Telegram Bot Token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
