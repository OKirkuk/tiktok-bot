import os, json, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- هذا حتى يرضى Render ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# ---------------------------

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
DB_FILE = "users.json"
ADMIN_ID = 6351625764

def load_users():
    try: return set(json.load(open(DB_FILE)))
    except: return set()

def save_users(users):
    json.dump(list(users), open(DB_FILE, "w"))

users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    save_users(users)
    await update.message.reply_text("أهلاً! دزلي رابط تيك توك واني احمله الك بدون علامة مائية ✅")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"عدد المستخدمين: {len(users)}")
    else:
        await update.message.reply_text("هذا الامر للادمن فقط")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url and "vt.tiktok" not in url:
        return
    
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '%(title)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                video_url = info['formats'][-1]['url']
            
            # نرسل الفيديو مباشرة بدون ما ننزله على السيرفر
            await update.message.reply_video(video_url, caption="✅ تم التحميل @DownloadTikTok_Bot")
            await msg.delete()
    except Exception as e:
        await msg.edit_text(f"فشل التحميل: {e}\nجرب رابط ثاني 🙏\n\nتأكد تحدث yt-dlp")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    main()
