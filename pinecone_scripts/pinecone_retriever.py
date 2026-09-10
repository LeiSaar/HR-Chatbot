import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from src.utilities import download_embeddings

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set.")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

INDEX_NAME = "hrchatbotllm"
embedding = download_embeddings()
docsearch = PineconeVectorStore.from_existing_index(index_name=INDEX_NAME, embedding=embedding)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

@lru_cache(maxsize=200)
def get_pinecone_context(question):
    docs = retriever.invoke(question)
    if not docs:
        return "No relevant HR policy documents were found."

    context_parts = []
    for index, doc in enumerate(docs, start=1):
        context_parts.append(f"--- HR POLICY DOCUMENT {index} ---\n{doc.page_content}")

    return "\n".join(context_parts)