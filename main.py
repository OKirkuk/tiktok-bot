import os
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def start(update: Update, context):
    await update.message.reply_text("رابط تيك توك دزلي حتى احمله الك بدون علامة مائية")

async def download(update: Update, context):
    url = update.message.text
    if "tiktok.com" not in url:
        return
    await update.message.reply_text("⏳ جاري التحميل...")
    try:
        opts = {
            'format': 'best',
            'outtmpl': '%(id)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                'Referer': 'https://www.tiktok.com/'
            },
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        await update.message.reply_video(video=open(file_path, 'rb'))
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def main():
    threading.Thread(target=run_flask).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    application.run_polling()

if __name__ == "__main__":
    main()
