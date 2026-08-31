import os
import threading
import requests
import telebot
from flask import Flask

# --- الاعدادات ---
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- دالة اضافة المستخدمين (اذا ما عندك ريدس اتركها مثل ما هي) ---
def redis_req(cmd):
    # اذا انت تستخدم Upstash حط الكود مالك هنا
    # اذا ما تحتاج احصائيات خليها ترجع 0
    try:
        import requests as req
        url = os.getenv("REDIS_URL")
        if not url:
            return {"result": 0}
        r = req.post(f"{url}", json=cmd, headers={"Authorization": f"Bearer {os.getenv('REDIS_TOKEN')}"}, timeout=5)
        return r.json()
    except:
        return {"result": 0}

def add_user(user_id):
    try:
        redis_req(["SADD", "users", str(user_id)])
    except:
        pass

# --- اوامر البوت ---
@bot.message_handler(commands=['start', 'id', 'stats'])
def all_cmd(m):
    add_user(m.from_user.id)

    if m.text.startswith('/id'):
        bot.reply_to(m, f"الايدي مالتك: {m.from_user.id}")
        return

    if m.text.startswith('/stats'):
        res = redis_req(["SCARD", "users"])
        count = res.get("result", 0)
        bot.reply_to(m, f"📊 عدد مستخدمين البوت: {count}")
        return

    bot.reply_to(m, "هلا بيك 👋\nدزلي رابط التيك توك وانزله الك بدون علامة")

# --- تحميل التيك توك ---
@bot.message_handler(func=lambda m: True)
def handle(m):
    add_user(m.from_user.id)
    url = m.text.strip()

    if "tiktok.com" not in url and "vt.tiktok" not in url:
        return

    try:
        msg = bot.reply_to(m, "جاري التحميل...")
        api = f"https://tikwm.com/api/?url={url}"
        data = requests.get(api, timeout=15).json()
        video_url = data['data']['play']

        bot.delete_message(m.chat.id, msg.message_id)
        bot.send_video(m.chat.id, video_url, caption="تم التحميل @بوتك")

    except Exception as e:
        print(e)
        bot.reply_to(m, "ما كدرت انزله، تأكد من الرابط صحيح")

# --- حل مشكلة رندر (موقع وهمي حتى ما يفشل) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- تشغيل البوت ---
print("Bot started...")
bot.infinity_polling()
