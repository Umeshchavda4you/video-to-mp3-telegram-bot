Video to Audio Telegram Bot
This is a Telegram bot that converts videos to audio (MP3) with a limit of 100 conversions per user per day. It is built using Python, python-telegram-bot, and moviepy, and is designed to be deployed on Render.
Setup Instructions

Create a Telegram Bot:

Talk to BotFather on Telegram and create a new bot.
Copy the bot token provided by BotFather.


Set Up the Project:

Clone this repository.
Install dependencies: pip install -r requirements.txt
Set the TELEGRAM_BOT_TOKEN environment variable with your bot token.


Deploy to Render:

Create a new Web Service on Render.
Connect your GitHub repository.
Set the following environment variable in Render:
TELEGRAM_BOT_TOKEN: Your Telegram bot token.


Use the following settings:
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: Defined in Procfile (python main.py)




Usage:

Start the bot by sending /start.
Send a video file to convert it to MP3.
The bot enforces a limit of 100 conversions per user per day.



Project Structure

main.py: Main bot script with video-to-audio conversion logic.
requirements.txt: Python dependencies.
Procfile: Render deployment configuration.
conversions.db: SQLite database to track conversion counts (created automatically).

Notes

The bot stores conversion counts in a SQLite database (conversions.db).
Temporary video and audio files are deleted after processing.
Ensure the Render instance has sufficient storage for temporary files.

