# Optional: specify paths (Windows setup)

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os



def is_scanned_pdf(pdf_path,tesseract,poppler):
    TESSERACT_PATH = tesseract

    POPPLER_PATH = poppler
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    """
    Checks if the PDF contains selectable text.
    Returns True if scanned (image-based), False if text-based.
    """
    text_threshold=20
    doc = fitz.open(pdf_path)
    total_text = ""
    for page in doc:
        print("Checking page...")
        print(page)
        total_text += page.get_text()
        print(total_text)
        # Early exit if enough text detected
        if len(total_text) > text_threshold:
            return False
    return True



def extract_text_from_scanned_pdf(pdf_path,poppler):
    """Extracts text from a scanned (image-based) PDF using OCR."""
    POPPLER_PATH = poppler
    pages = convert_from_path(pdf_path, poppler_path=poppler)
    text = ""
    for i, page in enumerate(pages):
        page_text = pytesseract.image_to_string(page)
        text += f"\n--- Page {i+1} ---\n{page_text}"
        print(f"Extracted text from page {i+1}")
        print(text)
    return text
