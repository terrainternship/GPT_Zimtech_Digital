from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import openai
import tiktoken
import os
import logging


# получим переменные окружения из .env
load_dotenv()

# API-key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# задаем system
default_system = "Ты-консультант в компании Simble, ответь на вопрос клиента на основе документа с информацией. Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией для ответа клиенту. Клиент ничего не должен знать про Документ с информацией для ответа клиенту"

db_folder_path = ""
db_index_name = "SimbleDB"
db_path = os.path.join(db_folder_path, db_index_name)


class Chunks():

    def __init__(self, path_to_base:str) -> None:

        self.logger = logging.getLogger(__name__)

        self.embeddings = OpenAIEmbeddings()

        if not os.path.exists(db_path + ".faiss") or not os.path.exists(db_path + ".pkl"):
            self.create_db(path_to_base)

        self.db = FAISS.load_local(
            folder_path=db_folder_path,
            embeddings=self.embeddings,
            index_name=db_index_name
        )

        self.logger.info("База загружена")

    
    def create_db(self, path_to_base:str) -> None:
        ch_size = 1024

        self.logger.info("База создается...")

        # загружаем базу
        with open(path_to_base, 'r', encoding='utf-8') as file:
            document = file.read()

        self.logger.info(f"Размер документа: {len(document)}")

        # создаем список чанков
        source_chunks = []
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "."],
            chunk_size=ch_size,
            chunk_overlap=0,
            length_function=lambda x: self.num_tokens_from_string(x)
        )

        for chunk in splitter.split_text(document):
            source_chunks.append(Document(page_content=chunk, metadata={}))

        self.logger.info(f"Количество чанков: {len(source_chunks)}")

        # создаем индексную базу
        self.db = FAISS.from_documents(source_chunks, self.embeddings)

        self.db.save_local(folder_path=db_folder_path, index_name=db_index_name)

        self.logger.info(f"База создана")


    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens
 

    async def get_answer(self, system:str = default_system, query:str = None):
        # релевантные чанки из базы
        docs = await self.db.asimilarity_search(query, k=4)
        message_content = '\n'.join([f'{doc.page_content}' for doc in docs])
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе. Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{query}"}
        ]

        # получение ответа от chatgpt
        completion = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo-16k",
                                                  messages=messages,
                                                  temperature=0)
        
        return completion.choices[0].message.content
