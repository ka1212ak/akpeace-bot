from flask import Flask, request
import telegram
import os
import asyncio

TOKEN = os.getenv("BOT_TOKEN")  # Получаем токен из переменных окружения
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(), bot)
        chat_id = update.message.chat.id
        asyncio.run(send_message(chat_id, "Привет! Я Антоний Великолепный!"))
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
