from pathlib import Path
import pandas as pd
from docx import Document as DocxDocument
from pypdf import PdfReader
from src.paddle_ocr import extract_text as extract_image_text_paddle


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        text = page.extract_text() or ""

        pages.append(
            f"--- PAGE {page_number} ---\n{text}"
        )

    return "\n\n".join(pages)


def extract_docx_text(file_path: str) -> str:
    document = DocxDocument(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def extract_csv_text(file_path: str) -> str:
    dataframe = pd.read_csv(file_path)

    return dataframe.to_csv(
        index=False
    )


def extract_excel_text(file_path: str) -> str:
    sheets = pd.read_excel(
        file_path,
        sheet_name=None
    )

    output = []

    for sheet_name, dataframe in sheets.items():

        output.append(
            f"--- SHEET: {sheet_name} ---"
        )

        output.append(
            dataframe.to_csv(
                index=False
            )
        )

    return "\n".join(output)


def extract_txt_text(file_path: str) -> str:
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        return file.read()


def extract_image_text(file_path: str) -> str:
    return extract_image_text_paddle(file_path)

def extract_text(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()
    if extension == ".pdf": return extract_pdf_text(file_path)
    if extension == ".docx": return extract_docx_text(file_path)
    if extension == ".csv": return extract_csv_text(file_path)
    if extension == ".xlsx": return extract_excel_text(file_path)
    if extension == ".txt": return extract_txt_text(file_path)
    if extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return extract_image_text(file_path)
        
    raise ValueError(f"Unsupported file type: {extension}")