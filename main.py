from flask import Flask
import threading, os, requests, telebot

# --- يحل مشكلة Render ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running OK!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

# --- الاعدادات ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("UPSTASH_REDIS_REST_URL")
TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
ADMIN_ID = 6502620677  # حط ايديك هنا من @userinfobot
bot = telebot.TeleBot(BOT_TOKEN)

def redis_req(command):
    try:
        r = requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"}, json=command, timeout=10)
        return r.json()
    except: return {}

def add_user(uid):
    redis_req(["SADD", "users", str(uid)])

def get_count():
    res = redis_req(["SCARD", "users"])
    return res.get("result", 0)

@bot.message_handler(commands=['start'])
def start(m):
    add_user(m.from_user.id)
    bot.reply_to(m, "هلا بيك! دزلي رابط التيك توك وانزله الك بدون علامة")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id == ADMIN_ID:
        bot.reply_to(m, f"عدد المشتركين: {get_count()}")
    else:
        bot.reply_to(m, "هذا الامر للادمن فقط")

@bot.message_handler(func=lambda m: True)
def handle(m):
    add_user(m.from_user.id)
    url = m.text
    if "tiktok.com" not in url:
        return
    try:
        msg = bot.reply_to(m, "جاري التحميل...")
        # هنا كود التحميل مالتك القديم - خليته بسيط
        api = f"https://tikwm.com/api/?url={url}"
        data = requests.get(api).json()
        video_url = data['data']['play']
        bot.delete_message(m.chat.id, msg.message_id)
        bot.send_video(m.chat.id, video_url, caption="تم التحميل @ بوتك")
    except Exception as e:
        bot.reply_to(m, f"ما كدرت انزله، تأكد من الرابط")

bot.infinity_polling()
