import os, asyncio, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a): return

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), H).serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! دزلي رابط تيك توك ✅")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url: return
    m = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "hd": 1}, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        j = r.json()
        if j.get("code") == 0:
            v = j["data"].get("hdplay") or j["data"].get("play")
            t = j["data"].get("title","")[:200]
            await update.message.reply_video(v, caption=f"✅ {t}")
            await m.delete()
        else:
            await m.edit_text("ما كدرت احمله، جرب رابط ثاني")
    except Exception as e:
        await m.edit_text(f"خطأ: {e}")

def main():
    threading.Thread(target=run_server, daemon=True).start()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except: pass
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
