import os, json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"

def load_users():
    try: return set(json.load(open(DB_FILE)))
    except: return set()

def save_users(users):
    json.dump(list(users), open(DB_FILE, "w"))

users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    save_users(users)
    await update.message.reply_text("👋 هلا! دزلي رابط التيك توك وانزله الك بدون علامة مائية\n\nارسل /stats لمعرفة عدد المشتركين (للادمن فقط)")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # خلي الايدي مالتك هنا
    ADMIN_ID = 6351625764  # هذا ايدي افتراضي غيره لايديك
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"📊 عدد المشتركين: {len(users)}")
    else:
        await update.message.reply_text(f"📊 البوت بيه {len(users)} مشترك")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url and "vt.tiktok.com" not in url:
        return
    
    users.add(update.effective_user.id)
    save_users(users)
    
    msg = await update.message.reply_text("⏳ جاري التحميل... ثواني")
    try:
        ydl_opts = {'format': 'mp4', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            await update.message.reply_video(video=video_url, caption="✅ تم التحميل @TikNowaterMarkBot")
            await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ فشل: {e}\nجرب رابط ثاني")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.run_polling()
