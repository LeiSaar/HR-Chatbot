import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from src.prompt import system_prompt

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME").strip().strip('"').strip("'")

chat_model = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
    keep_alive="30m"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Context:\n{context}\n\nUser Query:\n{input}")
])

answer_chain = prompt | chat_model