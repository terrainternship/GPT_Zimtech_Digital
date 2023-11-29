from fastapi import FastAPI
from chunks import Chunks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging


logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Логгирование в консоль
        logging.FileHandler('app.log', encoding='utf-8')  # Логгирование в файл
    ]
)

class Question(BaseModel): 
    text: str

# инициализация индексной базы
chunks = Chunks(path_to_base="Simble.txt")

# создаем объект приложения
app = FastAPI()

# настройки для работы запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# функция обработки post запроса + декоратор 
@app.post("/api/get_answer")
async def get_answer(question: Question):
    answer = await chunks.get_answer(query=question.text)
    return {"message": answer}
