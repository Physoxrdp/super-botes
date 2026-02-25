from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from checker import update_account, check_profile
from db import cur

BOT_TOKEN = "8493639166:AAFB75cMJfZmiUQli6MeaKPXx8ILs8lrBLg"
ADMIN_CHAT_ID = 7477558605  # apna chat id

# ---------------- FLASK APP ----------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "IG Monitor Running ✅"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# ---------------- TELEGRAM BOT ----------------
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.args[0]
    cur.execute("INSERT OR IGNORE INTO accounts VALUES (?,?,?,?)",
                (username, "unknown", 0, None))
    await update.message.reply_text(f"Tracking started for @{username}")

async def check_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]
    res = check_profile(name)
    await update.message.reply_text(f"@{name} → {res}")

def monitor_job(app):
    cur.execute("SELECT username FROM accounts")
    for (u,) in cur.fetchall():
        result = update_account(u)
        if result == "NOT_FOUND":
            app.bot.send_message(ADMIN_CHAT_ID, f"🚨 @{u} BANNED (3 checks)")
        elif result == "VISIBLE":
            app.bot.send_message(ADMIN_CHAT_ID, f"🎉 @{u} UNBANNED (3 checks)")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("check_username", check_username))

    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_job, "interval", minutes=5, args=[app])
    scheduler.start()

    app.run_polling()

# ---------------- MAIN ----------------
if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
