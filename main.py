import os, json, threading
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

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
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
    await update.message.reply_text("أهلاً! دزلي رابط تيك توك وانا انزله بدون علامة مائية.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    await update.message.reply_text(f"عدد المشتركين: {len(users)}")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        return
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        ydl_opts = {'format': 'mp4', 'outtmpl': 'video.mp4', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_video(video=open('video.mp4', 'rb'))
        await msg.delete()
        os.remove('video.mp4')
    except Exception as e:
        await msg.edit_text(f"فشل التحميل: {e}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
