import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
TEXT_MODEL = os.getenv("TEXT_MODEL").strip().strip('"').strip("'")

# Using a smaller model and keeping it loaded in memory
rewriter_model = ChatOllama(model=TEXT_MODEL, temperature=0, keep_alive="30m")

rewriter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a question rewriting assistant for an HR chatbot.
Rewrite the user's latest message into a standalone question using conversation history.
Do not answer the question or invent facts. Return only the rewritten question."""),
    ("human", "History: {history}\n\nQuestion: {question}")
])

PRONOUNS = {"i", "me", "my", "he", "him", "his", "she", "her", "they", "them", "their", "it", "that", "this", "those"}

def rewrite_question(question, history):
    if not history or history == "No previous conversation found.":
        return question
        
    # Check for pronoun presence
    words = set(re.findall(r'\b\w+\b', question.lower()))
    if not words.intersection(PRONOUNS):
        return question

    chain = rewriter_prompt | rewriter_model
    response = chain.invoke({"history": history, "question": question})
    return response.content.strip()