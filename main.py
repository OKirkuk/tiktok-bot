import os, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK Bot is running")
    def log_message(self, *a): return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting fake server on port {port}")
    HTTPServer(('0.0.0.0', port), H).serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا عمر! دزلي رابط التيك توك توك وآني احمله الك بدون علامة.")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        return
    m = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}, timeout=20)
        j = r.json()
        if j.get("code") == 0:
            v = j["data"].get("hdplay") or j["data"].get("play")
            t = j["data"].get("title", "")
            await update.message.reply_video(v, caption=t[:200])
            await m.delete()
        else:
            await m.edit_text("❌ فشل التحميل، جرب رابط ثاني")
    except Exception as e:
        print(f"Error: {e}")
        await m.edit_text(f"صار خطأ: {e}")

def main():
    print("Bot starting...")
    threading.Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))
    print("Bot polling started!")
    app.run_polling()

if __name__ == "__main__":
    main()
