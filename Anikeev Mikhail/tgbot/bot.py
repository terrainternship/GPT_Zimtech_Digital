from typing import Any
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import aiohttp
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Добро пожаловать!")


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User:")
    logger.info(update.message.text)

    answer = ""
    try:
        payload = {"text": update.message.text}
        result = await request_post(f"{API_URL}/api/get_answer", payload)
        answer = result['message']
    except Exception as e:
        logger.exception(e)
        answer = f'Ошибка при получении ответа: {e}'

    logger.info("Bot:")
    logger.info(answer)
    
    await update.message.reply_text(answer)


async def request_get(url) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()


async def request_post(url: str, data) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            resp.raise_for_status()
            return await resp.json()


def main():

    application = Application.builder().token(TOKEN).build()
    logger.info('Бот запущен...')

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, text))

    application.run_polling()
    logger.info('Бот остановлен')


if __name__ == "__main__":
    main()
