import os

from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec

from langchain_pinecone import PineconeVectorStore

from src.utilities import load_pdf_files, filter_to_minimal_docs, text_split, download_embeddings

load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


if not PINECONE_API_KEY:

    raise ValueError("PINECONE_API_KEY is not set.")


INDEX_NAME = "hrchatbotllm"


pc = Pinecone(api_key=PINECONE_API_KEY)


extracted_data = load_pdf_files( "data/policies")


minimal_docs = filter_to_minimal_docs(extracted_data)


text_chunks = text_split(minimal_docs)


embedding = download_embeddings()


if not pc.has_index(INDEX_NAME):

    pc.create_index(
        name=INDEX_NAME,

        dimension=384,

        metric="cosine",

        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )


docsearch = PineconeVectorStore.from_documents(
        documents=text_chunks,
        embedding=embedding,
        index_name=INDEX_NAME
    )


print("Pinecone indexing completed.")