import os, asyncio, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! دزلي رابط تيك توك واني احمله الك بدون علامة ✅")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        return
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "hd": 1}, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        data = r.json()
        if data.get("code") == 0:
            video_url = data["data"].get("hdplay") or data["data"].get("play")
            title = data["data"].get("title", "")[:200]
            await update.message.reply_video(video_url, caption=f"✅ {title}")
            await msg.delete()
        else:
            await msg.edit_text("ما كدرت احمل الفيديو")
    except Exception as e:
        await msg.edit_text(f"خطأ: {e}")

async def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
