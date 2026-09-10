from typing import List

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

from langchain_huggingface import HuggingFaceEmbeddings


def load_pdf_files(data):

    loader = DirectoryLoader(
        data,

        glob="*.pdf",

        loader_cls=PyPDFLoader
    )


    return loader.load()


def filter_to_minimal_docs(docs: List[Document]):

    minimal_docs = []


    for doc in docs:

        source = doc.metadata.get("source")


        minimal_docs.append(
            Document(
                page_content=doc.page_content,

                metadata={"source": source}
            )
        )


    return minimal_docs


def text_split(documents):

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    return splitter.split_documents(documents)

def download_embeddings():
    return HuggingFaceEmbeddings(model_name=("sentence-transformers/all-MiniLM-L6-v2"))