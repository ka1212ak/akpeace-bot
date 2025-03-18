from flask import Flask, request
import telegram
from telegram import ReplyKeyboardMarkup, TelegramError
import os
import asyncio
import httpx
import logging

# Настройка логирования для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем Flask приложение
app = Flask(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Создаем асинхронный HTTP-клиент с увеличенным лимитом соединений
client = httpx.AsyncClient(limits=httpx.Limits(max_connections=50, max_keepalive_connections=20))

# Создаем объект бота с кастомным клиентом
bot = telegram.Bot(token=TOKEN, request_kwargs={"client": client})

# Создаем семафор для ограничения одновременных запросов
semaphore = asyncio.Semaphore(10)

# Асинхронная функция для отправки сообщения с повторными попытками
async def send_message_with_retry(chat_id, text, buttons=None, retries=3, delay=2):
    async with semaphore:
        for attempt in range(retries):
            try:
                if buttons:
                    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
                else:
                    await bot.send_message(chat_id=chat_id, text=text)
                logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
                return  # Успешно отправлено
            except TelegramError as e:
                if attempt < retries - 1:
                    logger.warning(f"Ошибка {e}, повторная попытка {attempt + 1}/{retries} через {delay} сек...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Не удалось отправить сообщение после {retries} попыток: {e}")
                    raise

# Обработка вебхука
@app.route("/", methods=["POST"])
def webhook():
    # Получаем данные из запроса
    data = request.get_json()
    if not data:
        logger.error("Нет данных в запросе")
        return "No data", 400

    # Парсим обновление
    update = telegram.Update.de_json(data, bot)
    if not update or not update.message:
        logger.error(f"Некорректное обновление: {data}")
        return "Invalid update", 400

    chat_id = update.message.chat.id
    text = update.message.text
    logger.info(f"Получено сообщение от {chat_id}: {text}")

    # Определяем главное меню
    main_menu = [["🤖 AI-ассистент", "🛍 Маркетплейс"], ["🥗 Подбор еды", "💬 Поддержка"]]

    # Асинхронная функция обработки ответа
    async def process_response():
        try:
            if text == "/start":
                await send_message_with_retry(chat_id, "Привет! Выберите, чем я могу помочь:", main_menu)
            elif text == "🤖 AI-ассистент":
                await send_message_with_retry(chat_id, "Я ваш AI-ассистент! Задайте мне вопрос.")
            elif text == "🛍 Маркетплейс":
                await send_message_with_retry(chat_id, "Маркетплейс скоро будет доступен!")
            elif text == "🥗 Подбор еды":
                await send_message_with_retry(chat_id, "Опишите ваш рацион, и я помогу подобрать питание.")
            elif text == "💬 Поддержка":
                await send_message_with_retry(chat_id, "Если вам нужна помощь, напишите нашему оператору.")
            else:
                await send_message_with_retry(chat_id, "Я пока не знаю эту команду. Попробуйте выбрать из меню.", main_menu)
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

    # Запускаем асинхронную задачу
    asyncio.run(process_response())

    return "OK", 200

# Закрытие клиента при завершении работы приложения
@app.teardown_appcontext
def shutdown_client(exception=None):
    try:
        asyncio.run(client.aclose())
        logger.info("HTTP-клиент успешно закрыт")
    except Exception as e:
        logger.error(f"Ошибка при закрытии клиента: {e}")

if __name__ == "__main__":
    # Render задает порт через переменную окружения PORT
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
