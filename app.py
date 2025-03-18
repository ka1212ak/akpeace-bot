from flask import Flask, request
import telegram
from telegram import ReplyKeyboardMarkup
import os
import asyncio
import httpx
from telegram import Bot
import asyncio

# Увеличиваем лимит соединений
client = httpx.AsyncClient(limit=50)  # Увеличиваем лимит соединений

# Создаем объект бота с клиентом
bot = Bot(token="YOUR_BOT_TOKEN", request_kwargs={"client": client})

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Ограничиваем количество одновременных соединений (например, 10)
semaphore = asyncio.Semaphore(10)

async def send_message(chat_id, text, buttons=None):
    async with semaphore:  # Ограничиваем число одновременных запросов
        if buttons:
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=chat_id, text=text)
from telegram import TelegramError

# Функция для отправки сообщения с повторными попытками
async def send_message_with_retry(chat_id, text, retries=3, delay=2):
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id, text)
            return  # Сообщение успешно отправлено
        except TelegramError as e:
            if attempt < retries - 1:
                print(f"Ошибка при отправке сообщения, повторная попытка через {delay} секунд...")
                await asyncio.sleep(delay)
                continue  # Повторяем попытку
            else:
                print(f"Ошибка при отправке сообщения: {e}")
                raise  # В конце выбрасываем ошибку, если все попытки неудачны
# Создаем семафор для ограничения количества одновременно выполняющихся запросов
semaphore = asyncio.Semaphore(10)  # Ограничиваем количество одновременно выполняющихся запросов

# Асинхронная функция для отправки сообщения с использованием семафора
async def send_message(chat_id, text):
    async with semaphore:
        await send_message_with_retry(chat_id, text)

@app.route("/", methods=["POST"])
async def webhook():
    update = telegram.Update.de_json(request.get_json(), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    main_menu = [["🤖 AI-ассистент", "🛍 Маркетплейс"], ["🥗 Подбор еды", "💬 Поддержка"]]

    if text == "/start":
        await send_message(chat_id, "Привет! Выберите, чем я могу помочь:", main_menu)
    elif text == "🤖 AI-ассистент":
        await send_message(chat_id, "Я ваш AI-ассистент! Задайте мне вопрос.")
    elif text == "🛍 Маркетплейс":
        await send_message(chat_id, "Маркетплейс скоро будет доступен!")
    elif text == "🥗 Подбор еды":
        await send_message(chat_id, "Опишите ваш рацион, и я помогу подобрать питание.")
    elif text == "💬 Поддержка":
        await send_message(chat_id, "Если вам нужна помощь, напишите нашему оператору.")
    else:
        await send_message(chat_id, "Я пока не знаю эту команду. Попробуйте выбрать из меню.")

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

