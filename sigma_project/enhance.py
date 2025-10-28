import cv2
import numpy as np
from PIL import Image

def preprocess_image(pil_image):
    """Convert a PIL image to a cleaned-up grayscale OpenCV image."""
    # Convert PIL → OpenCV format
    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # grayscale

    # 1️⃣ Denoise
    image = cv2.fastNlMeansDenoising(image, h=30)

    # 2️⃣ Thresholding (binarize)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # 3️⃣ (Optional) Deskew
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return Image.fromarray(image)
TESSERACT_PATH = r"C:\Tesseract-OCR\tesseract.exe"
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd =TESSERACT_PATH
POPPLER_PATH = r"C:\Users\DELL\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin"
pages = convert_from_path("samples/2 prop sheet 1.pdf", poppler_path=POPPLER_PATH)

def extract_text_from_scanned_pdf(pdf_path, poppler_path):
    """Extracts text from a scanned (image-based) PDF using OCR, adaptive to quality."""
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    text = ""
    for i, page in enumerate(pages):
        print(f"\nProcessing page {i+1}...")

        # 1️⃣ Try direct OCR first (clean scan)
        clean_text = pytesseract.image_to_string(page, lang='eng', config='--oem 1 --psm 11')

        # 2️⃣ If it's gibberish or too short, retry with preprocessing
        if len(clean_text.strip()) < 20 or not any(c.isalpha() for c in clean_text):
            print("Low text quality detected — applying preprocessing...")
            preprocessed = preprocess_image(page)
            clean_text = pytesseract.image_to_string(preprocessed, lang='eng', config='--oem 1 --psm 11')

        text += f"\n--- Page {i+1} ---\n{clean_text}"
        print(f"✅ Extracted text from page {i+1}")
        print(clean_text)
    return text
extracted_text = extract_text_from_scanned_pdf("samples/4 comp house 2.pdf", POPPLER_PATH)
