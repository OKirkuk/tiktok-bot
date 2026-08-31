import os

# ... باقي الكود مالك نفسه ...

# ضيف هاي الدالتين فوك

def save_user(user_id):
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

async def start(update, context):
    save_user(update.effective_user.id)
    await update.message.reply_text("هلا صديقي! 👋\nدزلي رابط تيك توك وانا انزله الك بدون علامة مائية")

async def stats(update, context):
    # بس انت تكدر تشوفه - حط الايدي مالك هنا
    MY_ID = 123456789  # <--- بدل هذا الرقم بالايدي مالتك
    if update.effective_user.id == MY_ID:
        count = 0
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                count = len(f.read().splitlines())
        await update.message.reply_text(f"عدد المشتركين: {count}")
