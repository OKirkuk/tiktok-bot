from flask import Flask
import threading, os, requests, telebot

# --- حل مشكلة Render ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running OK!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

# --- الاعدادات ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("UPSTASH_REDIS_REST_URL")
TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def redis_req(command):
    try:
        r = requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"}, json=command, timeout=10)
        return r.json()
    except: return {}

def add_user(uid):
    redis_req(["SADD", "users", str(uid)])

@bot.message_handler(commands=['start', 'id', 'stats'])
def all_cmd(m):
    add_user(m.from_user.id)
    
    if m.text.startswith('/id'):
        bot.reply_to(m, f"الايدي مالتك: {m.from_user.id}")
        return

    if m.text.startswith('/stats'):
        res = redis_req(["SCARD", "users"])
        count = res.get("result", 0)
        bot.reply_to(m, f"📊 عدد المشتركين الكلي: {count}\nالايدي مالتك: {m.from_user.id}")
        return

    bot.reply_to(m, "هلا بيك! دزلي رابط التيك توك وانزله الك بدون علامة")

@bot.message_handler(func=lambda m: True)
def handle(m):
    add_user(m.from_user.id)
    url = m.text
    if "tiktok.com" not in url and "vt.tiktok" not in url:
        return
    try:
        msg = bot.reply_to(m, "جاري التحميل...")
        api = f"https://tikwm.com/api/?url={url}"
        data = requests.get(api, timeout=15).json()
        video_url = data['data']['play']
        bot.delete_message(m.chat.id, msg.message_id)
        bot.send_video(m.chat.id, video_url, caption="#ياسر_الدوسري")
    except Exception as e:
        bot.reply_to(m, "ما كدرت انزله، تأكد من الرابط")

bot.infinity_polling()
