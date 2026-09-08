import os, requests, yt_dlp, telebot
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "البوت شغال"

def download_tiktok(url):
    api_url = "https://www.tikwm.com/api/"
    data = {"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}
    res = requests.post(api_url, data=data).json()
    if res.get("data"):
        video_url = res["data"].get("hdplay") or res["data"].get("play")
        if video_url.startswith("/"):
            video_url = "https://www.tikwm.com" + video_url
        title = res["data"].get("title", "فيديو")
        os.makedirs("downloads", exist_ok=True)
        path = f"downloads/tiktok_{os.urandom(4).hex()}.mp4"
        r = requests.get(video_url, stream=True)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return path, title
    else:
        raise Exception("فشل جلب الفيديو")

def download_facebook(url):
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {'format': 'best', 'outtmpl': 'downloads/%(id)s.%(ext)s', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info.get('title', 'فيس بوك')

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "هلا 👋 دزلي رابط تيك توك او فيس بوك")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if "tiktok.com" not in url and "facebook.com" not in url and "fb.watch" not in url and "fb.com" not in url:
        return
    msg = bot.reply_to(m, "⏳ جاري التحميل...")
    try:
        if "tiktok.com" in url:
            file_path, title = download_tiktok(url)
        else:
            file_path, title = download_facebook(url)
        with open(file_path, 'rb') as v:
            bot.send_video(m.chat.id, v, caption=title)
        os.remove(file_path)
        bot.delete_message(m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ فشل: {e}", m.chat.id, msg.message_id)

def run_bot(): bot.infinity_polling()
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
