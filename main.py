import os
import telebot
import yt_dlp
from flask import Flask
import threading

# --- الاعدادات ---
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال"

# --- دالة التحميل ---
def download_video(url):
    # مجلد التحميلات
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # اعلى جودة
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'فيديو')

# --- اوامر البوت ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "هلا بيك 👋\n"
        "دزلي رابط تيك توك او فيس بوك (ريلز - فيديو عادي - ستوري)\n"
        "واني انزله الك بأعلى جودة"
    )

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    
    # نتأكد الرابط من تيك توك او فيس بوك
    if "tiktok.com" in url or "facebook.com" in url or "fb.watch" in url or "fb.com" in url:
        msg = bot.reply_to(message, "⏳ جاري التحميل بأعلى جودة، انتظر...")
        try:
            file_path, title = download_video(url)
            
            # نرسل الفيديو
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=f"✅ تم التحميل\n{title}")
            
            # نمسح الفيديو من السيرفر حتى لا ينترس
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"❌ صار خطأ بالتحميل\nتأكد الرابط عام ومو خاص\n\nالخطأ: {e}", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "دزلي رابط صحيح من تيك توك او فيس بوك بس")

# --- تشغيل البوت ---
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
