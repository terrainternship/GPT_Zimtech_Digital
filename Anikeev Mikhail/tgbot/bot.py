from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import httpx
import logging


load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Логгирование в консоль
        logging.FileHandler('bot.log', encoding='utf-8')  # Логгирование в файл
    ]
)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TG_TOKEN')
API_URL = "http://127.0.0.1:8000"
timeout = httpx.Timeout(300.0, read=None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Добро пожаловать!")


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User:")
    logger.info(update.message.text)

    payload = {"text": update.message.text}
    response = await request_post(f"{API_URL}/api/get_answer", payload)

    answer = ""
    if response.status_code == 200:
        answer = response.json()['message']
    else:
        answer = f'Ошибка при получении данных. Код статуса: {response.status_code}, текст: "{response.text}"'

    logger.info("Bot:")
    logger.info(answer)
    
    await update.message.reply_text(answer)


async def request_get(url: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url, timeout=timeout)


async def request_post(url: str, data) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=data, timeout=timeout)


def main():

    application = Application.builder().token(TOKEN).build()
    logger.info('Бот запущен...')

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, text))

    application.run_polling()
    logger.info('Бот остановлен')


if __name__ == "__main__":
    main()
