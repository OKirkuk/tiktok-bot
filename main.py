import os
import telebot
import requests
import yt_dlp
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "البوت شغال"

# --- تحميل تيك توك عن طريق API قوي ---
def download_tiktok(url):
    api_url = "https://www.tikwm.com/api/"
    data = {"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}
    res = requests.post(api_url, data=data).json()
    if res.get("data"):
        # يجيب اعلى جودة بدون علامة مائية
        video_url = res["data"].get("hdplay") or res["data"].get("play")
        title = res["data"].get("title", "فيديو تيك توك")
        # نحمل الفيديو
        r = requests.get(video_url, stream=True)
        path = f"downloads/{title[:20]}.mp4"
        os.makedirs("downloads", exist_ok=True)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return path, title
    else:
        raise Exception("ما كدرت احمل الفيديو")

# --- تحميل فيس بوك ---
def download_facebook(url):
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {'format': 'best', 'outtmpl': 'downloads/%(title)s.%(ext)s', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info.get('title', 'فيديو فيس')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا 👋\nدزلي رابط تيك توك او فيس بوك واني انزله الك بجودة عالية")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    if "tiktok.com" not in url and "facebook.com" not in url and "fb.watch" not in url:
        return

    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    try:
        if "tiktok.com" in url:
            file_path, title = download_tiktok(url)
        else:
            file_path, title = download_facebook(url)

        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"✅ {title}")
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل: {e}", message.chat.id, msg.message_id)

def run_bot(): bot.infinity_polling()
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
