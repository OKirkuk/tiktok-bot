import os, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a): return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), H).serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا عمر! دزلي رابط تيك توك")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url: return
    m = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}, headers=headers, timeout=30)
        j = r.json()
        if j.get("code") == 0:
            v = j["data"].get("hdplay") or j["data"].get("play") or j["data"].get("wmplay")
            if v and v.startswith("/"):
                v = "https://www.tikwm.com" + v
            if not v:
                await m.edit_text("❌ ما لگيت الفيديو")
                return
            await m.edit_text("⏳ دا انزله...")
            data = requests.get(v, headers=headers, timeout=60).content
            open("/tmp/v.mp4","wb").write(data)
            await update.message.reply_video(open("/tmp/v.mp4","rb"), caption=j["data"].get("title","")[:200])
            await m.delete()
        else:
            await m.edit_text("❌ فشل")
    except Exception as e:
        await m.edit_text(f"خطأ: {e}")

def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))
    app.run_polling()

if __name__ == "__main__":
    main()
