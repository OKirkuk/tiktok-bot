import os
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"
def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("توك توك بوت جاهز 🚀 دزلي رابط")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        return
    await update.message.reply_text("⏳ جاري التحميل...")
    try:
        opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    application.run_polling()
