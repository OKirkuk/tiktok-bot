import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا دزلي رابط تيك توك")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        return
    await update.message.reply_text("⏳ جاي احمل...")
    try:
        opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        await update.message.reply_video(video=open('video.mp4','rb'))
        os.remove('video.mp4')
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
