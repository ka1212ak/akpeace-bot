from fastapi import FastAPI, Request
import telegram
import os
import asyncio

# Получаем токен для бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = FastAPI()

# Ограничиваем количество одновременных соединений
semaphore = asyncio.Semaphore(10)

async def send_message(chat_id, text, buttons=None):
    async with semaphore:
        if buttons:
            reply_markup = telegram.ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=chat_id, text=text)

@app.post("/")
async def webhook(request: Request):
    # Получаем данные от Telegram
    update = telegram.Update.de_json(await request.json(), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    main_menu = [["🤖 AI-ассистент", "🛍 Маркетплейс"], ["🥗 Подбор еды", "💬 Поддержка"]]

    # Обрабатываем команды
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

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

